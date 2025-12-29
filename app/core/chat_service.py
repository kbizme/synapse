from langchain.messages import HumanMessage, AIMessage, ToolMessage
from app.core.persistence.repositories import ChatRepository, MessageRepository
from app.core.memory import ChatManager
from app.core.persistence.db_sessions import get_session
from app.agents import agents
from app.tools.registry import TOOL_REGISTRY
import json




class ChatService:
    def __init__(self):
        self.chat_manager = ChatManager()

    def handle_user_message_stream(self, chat_id: str, prompt: str):
        # 1. Persistence Logic
        with get_session() as session:
            if ChatRepository.get_by_id(db_session=session, chat_id=chat_id) is None:
                ChatRepository.create(db_session=session, chat_id=chat_id, title=prompt[:60])
            
            MessageRepository.create(db_session=session, chat_id=chat_id, role="user", content=prompt)
            ChatRepository.touch(db_session=session, chat_id=chat_id)
        
        current_chat = self.chat_manager.get_chat(chat_id)
        last_message_in_memory = current_chat.get_messages()[-1]
        if not isinstance(last_message_in_memory, HumanMessage):
            current_chat.add_message(HumanMessage(content=prompt)) 

        def token_stream():
            history = current_chat.get_messages()
            iteration = 0
            
            while True:
                iteration += 1
                print(f"\n--- [DEBUG ITERATION {iteration}] ---")
                
                # Print History State for Debugging
                for i, m in enumerate(history):
                    t_calls = getattr(m, 'tool_calls', [])
                    t_id = getattr(m, 'tool_call_id', 'N/A')
                    print(f"  Msg {i}: {type(m).__name__} | Tools: {len(t_calls) if t_calls else 0} | T_ID: {t_id}")

                full_content = ""
                tool_calls = []

                # --- STEP 1: ASK LLM & STREAM ---
                try:
                    for chunk in agents.get_stream(history):
                        # Capture tool calls first
                        if chunk.tool_calls:
                            print(f"  --> Received Tool Call Chunk: {chunk.tool_calls}")
                            tool_calls.extend(chunk.tool_calls)
                        
                        # Process content
                        if chunk.content:
                            content_to_append = ""
                            if isinstance(chunk.content, str):
                                content_to_append = chunk.content
                            elif isinstance(chunk.content, list):
                                for part in chunk.content:
                                    if isinstance(part, str): content_to_append += part
                                    elif isinstance(part, dict) and "text" in part: content_to_append += part["text"]

                            if content_to_append:
                                full_content += content_to_append
                                
                                # FIX: Only yield to FastAPI if we are NOT in a tool-calling state
                                # If tool_calls are present in the chunk, it's metadata, don't show it.
                                if not chunk.tool_calls and not tool_calls:
                                    yield content_to_append
                                    
                except Exception as e:
                    print(f"!!! GROQ API ERROR: {str(e)}")
                    if hasattr(e, 'failed_generation'):
                        print(f"!!! FAILED GENERATION: {e}")
                    raise e

                # --- STEP 2: CHECK FOR TOOLS ---
                if tool_calls:
                    # Update internal memory with the AI's intent to call tools
                    ai_msg = AIMessage(content=full_content, tool_calls=tool_calls)
                    history.append(ai_msg)
                    current_chat.add_message(ai_msg)

                    for tc in tool_calls:
                        # --- WORKAROUND: Groq "Name+Args" Hallucination ---
                        raw_name = tc.get("name", "")
                        tool_args = tc.get("args", {})
                        
                        if "{" in raw_name:
                            print(f"  [FIX] Cleaning hallucinated name: {raw_name}")
                            parts = raw_name.split("{", 1)
                            clean_name = parts[0].strip()
                            try:
                                extra_args = json.loads("{" + parts[1])
                                tool_args.update(extra_args)
                            except: pass
                        else:
                            clean_name = raw_name

                        print(f"  --> Executing: {clean_name} | Args: {tool_args}")
                        
                        tool_fn = TOOL_REGISTRY.get(clean_name)
                        if tool_fn:
                            observation = tool_fn.invoke(tool_args)
                            content_str = json.dumps(observation, ensure_ascii=False)
                            
                            # Critical: Ensure tool_call_id exists for Groq's validator
                            t_msg = ToolMessage(
                                content=content_str,
                                tool_call_id=tc.get("id") or "fallback_id", 
                                name=clean_name
                            )
                            current_chat.add_message(t_msg)
                            history.append(t_msg)
                            
                            with get_session() as session:
                                MessageRepository.create(session, chat_id, "tool", content_str)
                                session.commit()
                        else:
                            print(f"  !!! Tool '{clean_name}' not found in registry")
                    
                    # Tool results added to history; loop back for the AI to answer
                    continue 

                # --- STEP 3: FINALIZATION ---
                if full_content.strip():
                    with get_session() as session:
                        MessageRepository.create(session, chat_id, "assistant", full_content)
                        session.commit()
                    current_chat.add_message(AIMessage(content=full_content))
                
                print(f"--- [DEBUG ITERATION {iteration} COMPLETE] ---")
                break 

        return token_stream()
    
    
    
    
    
    
    def handle_user_message(self, chat_id: str, prompt: str) -> str:
        with get_session() as session:
            assert session is not None
            if ChatRepository.get_by_id(db_session=session, chat_id=chat_id) is None:
                ChatRepository.create(db_session=session, chat_id=chat_id, title=prompt[:60])
            
            # entering data into the messages table
            MessageRepository.create(db_session=session, chat_id=chat_id, role="user", content=prompt)
            # updating related chat table entry
            ChatRepository.touch(db_session=session, chat_id=chat_id)
        
        # updating in-memory memory
        current_chat = self.chat_manager.get_chat(chat_id)
        last_message_in_memory = current_chat.get_messages()[-1]
        if not isinstance(last_message_in_memory, HumanMessage):
            current_chat.add_message(HumanMessage(content=prompt)) 
        
        # calling the ai agents
        ai_message = agents.get_completion(all_messages=current_chat.get_messages())
        
        # normalizing ai output
        content = ai_message.content
        if isinstance(content, list):
            content = "\n".join(str(x) for x in content)
            
        
        if ai_message:
            with get_session() as session:
                assert session is not None
                MessageRepository.create(
                    db_session=session,
                    chat_id=chat_id,
                    role="assistant",
                    content=content,
                )
                # updating related chat table entry
                ChatRepository.touch(db_session=session, chat_id=chat_id)
        
        # updating in-memory memory
        current_chat.add_message(ai_message)
        # returning the completion
        return content
    
    
    
    # def handle_user_message_stream(self, chat_id: str, prompt: str):
    #     with get_session() as session:
    #         assert session is not None
    #         if ChatRepository.get_by_id(session, chat_id) is None:
    #             ChatRepository.create(session, chat_id, title=prompt[:60])
    #         # inserting the new message
    #         MessageRepository.create(session, chat_id, "user", prompt)
    #         ChatRepository.touch(session, chat_id)

    #     # updating in-memory memory
    #     current_chat = self.chat_manager.get_chat(chat_id)
    #     last_message_in_memory = current_chat.get_messages()[-1]
    #     if not isinstance(last_message_in_memory, HumanMessage):
    #         current_chat.add_message(HumanMessage(content=prompt)) 

        
    #     def token_stream():
    #         full_content = ""

    #         for token in agents.get_completion_stream(all_messages=current_chat.get_messages()):
    #             full_content += token
    #             # print('token:', token, type(token))
    #             yield token

    #         if not full_content.strip():
    #             return

    #         with get_session() as session:
    #             MessageRepository.create(
    #                 session, chat_id, "assistant", full_content
    #             )
    #             ChatRepository.touch(session, chat_id)

    #         current_chat.add_message(AIMessage(content=full_content))

    #     return token_stream()
            
     