from langchain.agents import create_agent
from langchain_groq import ChatGroq
from app.core import config, memory
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage


# loading env variables
load_dotenv()


# llm model
llm = ChatGroq(model=config.DEFAULT_MODEL, temperature=config.DEFAULT_TEMPERATURE)


# agent
agent = create_agent(model=llm, system_prompt=config.get_system_prompt(config.DEFAULT_SYSTEM_PROMPT_ID))


def get_completion(prompt: str):
    if not isinstance(prompt, str):
        raise ValueError("Prompt must be a string")
    
    # memory handling
    prompt_obj = HumanMessage(content=prompt)
    memory.add_message(prompt_obj)
    all_messages = memory.get_messages()
    response = agent.invoke(input={"messages": all_messages})
    ai_completion = response['messages'][-1]
    memory.add_message(ai_completion)
    return ai_completion.content