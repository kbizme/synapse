from langchain.agents import create_agent
from langchain_groq import ChatGroq
from app.core import config
from dotenv import load_dotenv
from langchain_core.messages import AIMessage


# loading env variables
load_dotenv()


# llm model
llm = ChatGroq(model=config.DEFAULT_MODEL, 
               temperature=config.DEFAULT_TEMPERATURE)


# agent
agent = create_agent(model=llm, system_prompt=config.get_system_prompt(config.DEFAULT_SYSTEM_PROMPT_ID))


def get_completion(all_messages: list):
    ai_response = agent.invoke(input={"messages": all_messages})
    last_message = ai_response['messages'][-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError("Last message is not an AIMessage")
    
    return last_message