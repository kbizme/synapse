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
agent = create_agent(model=llm, system_prompt=config.get_system_prompt(config.DEFAULT_SYSTEM_PROMPT_ID))


def get_completion(all_messages: list):
    ai_response = agent.invoke(input={"messages": all_messages})
    last_message = ai_response['messages'][-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError("Last message is not an AIMessage")
    # returnign the ai completion
    return last_message


def get_completion_stream(all_messages: list):
    for msg, metadata in agent.stream(input={"messages": all_messages}, stream_mode="messages"):
        if isinstance(msg, (AIMessageChunk, BaseMessageChunk)):
            content = msg.content
            if isinstance(content, str) and content:
                yield content
            elif isinstance(content, list):
                yield "".join(str(x) for x in content)

