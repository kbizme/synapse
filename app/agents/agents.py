from langchain_groq import ChatGroq
from dotenv import load_dotenv
from app.core import config
from langchain_core.messages import SystemMessage
from app.tools.weather_tools import get_weather_data
from app.tools.time_tools import get_current_time, calculate_date_relative, convert_time_zones
from app.tools.math_tools import scientific_calculator, calculate_statistics
from app.tools.knowledge_base import query_knowledge_base

load_dotenv()


TOOLS = [
    get_weather_data,
    get_current_time,
    calculate_date_relative,
    convert_time_zones,
    scientific_calculator,
    calculate_statistics,
    query_knowledge_base
]



# factory function
def get_model(model_name: str | None = None, temperature: float | None = None):
    """Factory function to get a configured LLM."""
    return ChatGroq(
        model=model_name or config.DEFAULT_MODEL,
        temperature=temperature or config.DEFAULT_TEMPERATURE
    )


# streaming version
def get_stream(messages, assitant_type: str = config.DEFAULT_ASSISTANT_TYPE, extra_context: str | None = None):
    """ Main Model for Answering User Queries."""
    llm = get_model(model_name=config.NEW_OPENAI_MODEL)
    agent_executor = llm.bind_tools(tools=TOOLS)
    system_prompt = config.ALL_SYSTEM_PROMPTS.get(assitant_type, config.ALL_SYSTEM_PROMPTS[config.DEFAULT_ASSISTANT_TYPE])

    if extra_context:
        system_prompt += f"\n\nRelevant Context for your analysis:\n{extra_context} \n\nInstruction: Use ONLY the provided context to answer if relevant."
    
    full_message = [SystemMessage(content=system_prompt)] + messages
    return agent_executor.stream(full_message)




def generate_chat_title(user_query: str, ai_response: str) -> str:
    """Refined title generation using a cheap/fast model call."""
    llm = get_model(temperature=0)
    prompt = f"Summarize the following exchange into a 3-9 words title. No emoji, only text. \n\n Query: {user_query} \n\n Response: {ai_response}"
    res = llm.invoke(prompt)
    if isinstance(res.content, str):
        return res.content.strip().replace('"', '')
    else:
        return user_query[:60]