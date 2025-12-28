from langchain.messages import HumanMessage, AIMessage
from app.core.persistence.repositories import ChatRepository, MessageRepository
from app.core.memory import ChatManager
from app.core.persistence.db_sessions import get_session
from app.agents import agents


class ChatService:
    def __init__(self):
        self.chat_manager = ChatManager()
    
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
    
    
    
    def handle_user_message_stream(self, chat_id: str, prompt: str):
        with get_session() as session:
            assert session is not None
            if ChatRepository.get_by_id(session, chat_id) is None:
                ChatRepository.create(session, chat_id, title=prompt[:60])
            # inserting the new message
            MessageRepository.create(session, chat_id, "user", prompt)
            ChatRepository.touch(session, chat_id)

        # updating in-memory memory
        current_chat = self.chat_manager.get_chat(chat_id)
        last_message_in_memory = current_chat.get_messages()[-1]
        if not isinstance(last_message_in_memory, HumanMessage):
            current_chat.add_message(HumanMessage(content=prompt)) 

        def token_stream():
            full_content = ""

            for token in agents.get_completion_stream(all_messages=current_chat.get_messages()):
                full_content += token
                yield token

            if not full_content.strip():
                return

            with get_session() as session:
                MessageRepository.create(
                    session, chat_id, "assistant", full_content
                )
                ChatRepository.touch(session, chat_id)

            current_chat.add_message(AIMessage(content=full_content))

        return token_stream()
            
            

