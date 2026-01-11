from app.core import config
from langchain.messages import HumanMessage, AIMessage, ToolMessage
from app.core.persistence.repositories import MessageRepository
from app.core.persistence import db_sessions
from threading import Lock


class ChatMemory:
    def __init__(self):
        self._messages = list()
        self._lock = Lock()
        self.max_size = config.MEMORY_WINDOW_SIZE * 2
        

    def get_messages(self) -> list:
        with self._lock:
            return self._messages.copy()
    
    def add_message(self, message: HumanMessage | AIMessage | ToolMessage):
        if not isinstance(message, (HumanMessage, AIMessage, ToolMessage)):
            raise ValueError("messages must be a HumanMessage, AIMessage, or ToolMessage instance")
        with self._lock:
            self._messages.append(message)
            if len(self._messages) > self.max_size:
                self._messages = self._messages[-self.max_size:]
        


class ChatManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ChatManager, cls).__new__(cls)
                    cls._instance.all_chats = dict()
                    cls._instance._write_lock = Lock()

        return cls._instance
    

    def get_chat(self, chat_id: str):
        if chat_id not in self.all_chats:
            with self._write_lock:
                if chat_id not in self.all_chats:
                    self.all_chats[chat_id] = self._refill_chat_from_db(chat_id=chat_id)
        return self.all_chats[chat_id]
    
    
    def _refill_chat_from_db(self, chat_id: str):
        chat_memory = ChatMemory()
        with db_sessions.get_session() as session:
            messages = MessageRepository.get_messages_by_chat_id(db_session=session, chat_id=chat_id)
            for message in messages:
                if message.role == "user":
                    chat_memory.add_message(HumanMessage(content=message.content))
                elif message.role == "assistant":
                    chat_memory.add_message(AIMessage(content=message.content or "Processing...",
                                                      tool_calls=message.tool_calls or []))
                elif message.role == "tool":
                    chat_memory.add_message(ToolMessage(content=message.content, 
                                                        tool_call_id=message.tool_call_id or "legacy_id", 
                                                        name=message.tool_name or "unknown_tool"))
                                            
        return chat_memory
        
    
    def reset_chat(self, chat_id: str):
        with self._write_lock:
            self.all_chats.pop(chat_id, None)
    
    
    def reset_all(self):
        with self._write_lock:
            self.all_chats = dict()


