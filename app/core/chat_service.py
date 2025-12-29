from langchain.messages import HumanMessage, AIMessage, ToolMessage
from app.core.persistence.repositories import ChatRepository, MessageRepository
from app.core.memory import ChatManager
from app.core.persistence.db_sessions import get_session
from app.agents import agents
from app.tools.registry import TOOL_REGISTRY
import json
from app.core import config



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

        # default config initialization
        assistant_type = config.DEFAULT_ASSISTANT_TYPE
        extra_context = None
        
        # dynamic intent detection
        # TODO: RAG
        
        def token_stream():
            history = current_chat.get_messages()

            while True:
                full_content = ""
                tool_calls = []

                # --- STEP 1: GENERATE & STREAM ---
                try:
                    for chunk in agents.get_stream(messages=history, asssitant_type=assistant_type, extra_context=extra_context):
                        # collecting tool metadata
                        if chunk.tool_calls:
                            tool_calls.extend(chunk.tool_calls)
                        
                        # extracting and filtering contents
                        chunk_data = chunk.content
                        
                        if chunk_data:
                            content_to_append = ""
                            if isinstance(chunk_data, str):
                                content_to_append = chunk_data
                            elif isinstance(chunk_data, list):
                                for part in chunk_data:
                                    if isinstance(part, str): content_to_append += part
                                    elif isinstance(part, dict) and "text" in part: content_to_append += part["text"]

                            if content_to_append:
                                full_content += content_to_append
                                
                                # if tool_calls are present in the chunk, then not streaming the output.
                                if not chunk.tool_calls and not tool_calls:
                                    yield content_to_append
                                    
                except Exception as e:
                    print(f"!!! GROQ API ERROR in token_stream(): {str(e)}")
                    raise e

                # --- STEP 2: CHECK & EXECUTE TOOLS ---
                if tool_calls:
                    ai_msg = AIMessage(content=full_content, tool_calls=tool_calls)
                    history.append(ai_msg)
                    current_chat.add_message(ai_msg)

                    for tc in tool_calls:
                        # --- WORKAROUND: Groq "Name+Args" Hallucination ---
                        raw_name = tc.get("name", "")
                        tool_args = tc.get("args", {})
                        tool_id = tc.get("id")
                        
                        # cleaning JSON in name strings
                        clean_name = raw_name.split("{")[0].strip() if "{" in raw_name else raw_name
                        tool_func = TOOL_REGISTRY.get(clean_name)
                        
                        if tool_func:
                            observation = tool_func.invoke(tool_args)
                            content_str = json.dumps(observation, ensure_ascii=False)
                            
                            # preparing and storing tool message object
                            tool_msg = ToolMessage(content=content_str, tool_call_id=tool_id, name=clean_name)
                            current_chat.add_message(tool_msg)
                            history.append(tool_msg)
                            
                            # saving into the database
                            with get_session() as session:
                                MessageRepository.create(session, chat_id, "tool", content_str)
                                session.commit()
                        else:
                            print(f"  !!! Tool '{clean_name}' not found in registry")
                    
                    # tool results are added to history; loop back for the AI to answer
                    continue 

                # --- STEP 3: PERSIST FINAL RESPONSE ---
                if full_content.strip():
                    with get_session() as session:
                        MessageRepository.create(session, chat_id, "assistant", full_content)
                        session.commit()
                    current_chat.add_message(AIMessage(content=full_content))
                
                # finally, breaking the while loop
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
            
     