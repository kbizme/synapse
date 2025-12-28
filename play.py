from langchain.agents import create_agent
from langchain_groq import ChatGroq
from app.core import config
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessageChunk, AIMessageChunk


# loading env variables
load_dotenv()


# llm model
llm = ChatGroq(model=config.DEFAULT_MODEL, 
               temperature=config.DEFAULT_TEMPERATURE,
               streaming=True)


# agent
agent = create_agent(model=llm, 
                     system_prompt=config.get_system_prompt(config.DEFAULT_SYSTEM_PROMPT_ID),
                     )


for msg, metadata in agent.stream(
    {"messages": [{"role": "user", "content": "What is gen ai?"}]}, 
    stream_mode="messages" # This tells LangChain to stream the message tokens
    ):
    if isinstance(msg, (AIMessageChunk, BaseMessageChunk)):
        print(msg.content, end="", flush=True)

