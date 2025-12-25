from app.core import config
from langchain.messages import HumanMessage, AIMessage



# global messages memory container
__messages = list()



def get_messages() -> list:
    global __messages
    return __messages.copy()



def add_message(message: HumanMessage | AIMessage):
    global __messages

    if not isinstance(message, (HumanMessage, AIMessage)):
        raise ValueError("messages must be a HumanMessage or AIMessage instance")
    
    # adding new message into the memory
    __messages.append(message)
    # checking memory size
    if len(__messages) > config.MEMORY_WINDOW_SIZE * 2:
        __messages = __messages[-config.MEMORY_WINDOW_SIZE * 2:]
    


def reset_memory():
    global __messages
    __messages = list()