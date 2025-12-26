from langchain.agents import create_agent
from langchain_groq import ChatGroq
from app.core import config, memory
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage


# loading env variables
load_dotenv()


# llm model
llm = ChatGroq(model=config.DEFAULT_MODEL, 
               temperature=config.DEFAULT_TEMPERATURE)


# agent
agent = create_agent(model=llm, system_prompt=config.get_system_prompt(config.DEFAULT_SYSTEM_PROMPT_ID))


def get_completion(chat_id: str, prompt: str):
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt must be a non-empty string")
    
    # getting the chat manager instance
    chat_manager = memory.ChatManager()
    
    # getting the current chat
    chat = chat_manager.get_chat(chat_id)

    # memory handling
    prompt_obj = HumanMessage(content=prompt)
    chat.add_message(prompt_obj)
    all_messages = chat.get_messages()
    response = agent.invoke(input={"messages": all_messages})
    last_completion = response['messages'][-1]
    if not isinstance(last_completion, AIMessage):
        raise ValueError("Last message is not an AIMessage")
    
    # updating memory        
    chat.add_message(last_completion)
    
    content = last_completion.content
    if isinstance(content, list):
        content = "\n".join(str(x) for x in content)

    return content