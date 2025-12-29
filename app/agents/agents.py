from langchain.agents import create_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from app.core import config
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.messages import SystemMessage, AIMessageChunk, BaseMessageChunk, AIMessage

from app.tools.weather_tools import get_weather_data
from app.tools.time_tools import get_current_time, calculate_date_relative, convert_time_zones
from app.tools.math_tools import scientific_calculator, calculate_statistics

load_dotenv()

TOOLS = [
    get_weather_data,
    get_current_time,
    calculate_date_relative,
    convert_time_zones,
    scientific_calculator,
    calculate_statistics,
]

llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

# BIND THE TOOLS CORRECTLY
# Adding .bind_tools(tools) creates a "runnable" that handles the schema for Groq
agent_executor = llm.bind_tools(tools=TOOLS)

def get_stream(messages):
    return agent_executor.stream(messages)








def get_completion(all_messages: list):
    llm = ChatGroq(
        model=config.DEFAULT_MODEL,
        temperature=config.DEFAULT_TEMPERATURE,
        streaming=True,
        
    )
    agent = create_agent(
        model=llm,
        system_prompt=config.get_system_prompt(config.DEFAULT_SYSTEM_PROMPT_ID),
        tools=TOOLS,
        
    )
    ai_response = agent.invoke(input={"messages": all_messages})
    last_message = ai_response['messages'][-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError("Last message is not an AIMessage")
    # returnign the ai completion
    return last_message


# def get_completion_stream(all_messages: list):
#     for msg, metadata in agent.stream(input={"messages": all_messages}, stream_mode="messages"):
#         print(msg, type(msg))
#         if isinstance(msg, (AIMessageChunk, BaseMessageChunk)):
#             content = msg.content
#             if isinstance(content, str) and content:
#                 yield content
#             elif isinstance(content, list):
#                 yield "".join(str(x) for x in content)



