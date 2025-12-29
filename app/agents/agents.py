from langchain.agents import create_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from app.core import config
from langchain_core.messages import AIMessage, SystemMessage
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


llm = ChatGroq(model=config.NEW_OPENAI_MODEL,
               temperature=config.DEFAULT_TEMPERATURE)

agent_executor = llm.bind_tools(tools=TOOLS)


# streaming version
def get_stream(messages, asssitant_type: str = config.DEFAULT_ASSISTANT_TYPE, extra_context: str | None = None):
    system_prompt = config.ALL_SYSTEM_PROMPTS.get(asssitant_type)
    if not system_prompt:
        system_prompt = config.ALL_SYSTEM_PROMPTS[config.DEFAULT_ASSISTANT_TYPE]
    if extra_context:
        system_prompt += f"\n\nRelevant Context for your analysis:\n{extra_context}"
    
    full_message = [SystemMessage(content=system_prompt)] + messages

    return agent_executor.stream(full_message)


# basic version
def get_completion(all_messages: list):
    llm = ChatGroq(
        model=config.DEFAULT_MODEL,
        temperature=config.DEFAULT_TEMPERATURE,
    )
    agent = create_agent(
        model=llm,
        system_prompt=config.get_system_prompt(config.DEFAULT_ASSISTANT_TYPE),
        tools=TOOLS,
        
    )
    ai_response = agent.invoke(input={"messages": all_messages})
    last_message = ai_response['messages'][-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError("Last message is not an AIMessage")
    # returnign the ai completion
    return last_message
