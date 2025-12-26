from app.core import config
from langchain.messages import HumanMessage, AIMessage


class ChatMemory:
    def __init__(self):
        self._messages = list()

    def get_messages(self) -> list:
        return self._messages.copy()
    
    def add_message(self, message: HumanMessage | AIMessage):
        if not isinstance(message, (HumanMessage, AIMessage)):
            raise ValueError("messages must be a HumanMessage or AIMessage instance")
        
        # adding new message into the memory
        self._messages.append(message)
        # checking memory size
        if len(self._messages) > config.MEMORY_WINDOW_SIZE * 2:
            self._messages = self._messages[-config.MEMORY_WINDOW_SIZE * 2:]
        


class ChatManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChatManager, cls).__new__(cls)
            # Initialize the chats dict only once
            cls._instance.all_chats = dict()
        return cls._instance
    
    def get_chat(self, chat_id: str):
        if chat_id not in self.all_chats:
            self.all_chats[chat_id] = ChatMemory()
        return self.all_chats[chat_id]
    
    
    def reset_chat(self, chat_id: str):
        if chat_id in self.all_chats:
            del self.all_chats[chat_id]
    
    def reset_all(self):
        self.all_chats = dict()


