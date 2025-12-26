from langchain.messages import HumanMessage, AIMessage
from app.core.persistence.repositories import ChatRepository, MessageRepository
from app.core.memory import ChatManager
from app.core.persistence import sessions
from app.agents import agents


class ChatService:
    def __init__(self):
        self.chat_manager = ChatManager()
    
    def handle_user_message(self, chat_id: str, prompt: str) -> str:
        with sessions.get_session() as session:
            assert session is not None
            if ChatRepository.get_by_id(db_session=session, chat_id=chat_id) is None:
                ChatRepository.create(db_session=session, chat_id=chat_id, title=prompt[:60])
            
            MessageRepository.create(db_session=session, chat_id=chat_id, role="user", content=prompt)
        
        # updating in-memory memory
        chat = self.chat_manager.get_chat(chat_id=chat_id)
        chat.add_message(HumanMessage(content=prompt))
        
        
        # calling the ai agents
        ai_message = agents.get_completion(all_messages=chat.get_messages())
        
        # normalizing ai output
        content = ai_message.content
        if isinstance(content, list):
            content = "\n".join(str(x) for x in content)
            
        
        if ai_message:
            with sessions.get_session() as session:
                assert session is not None
                MessageRepository.create(
                    db_session=session,
                    chat_id=chat_id,
                    role="assistant",
                    content=content,
                )
        
        # updating in-memory memory
        chat.add_message(ai_message)
        
        return content