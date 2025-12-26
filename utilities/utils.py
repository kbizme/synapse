from app.agents import agents
from langchain.messages import HumanMessage






def generate_chat_title(prompt: str) -> str:
    title_prompt = f"""
    Generate a short, concise chat title (max 6 words)
    based ONLY on the following user message:

    "{prompt}"
    """

    title_message = agents.agent.invoke({
        "messages": [HumanMessage(content=title_prompt)]
    })

    return title_message["messages"][-1].content.strip()
