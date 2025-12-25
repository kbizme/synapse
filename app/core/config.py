# LLM Config
DEFAULT_MODEL = "llama-3.1-8b-instant"
DEFAULT_TEMPERATURE = 0.3
MIN_TEMPERATURE = 0.0
MAX_TEMPERATURE = 1.0
MAX_OUTPUT_TOKENS = 1024


# System Config
DEFAULT_SYSTEM_PROMPT_ID = "general_assistant"
ALL_SYSTEM_PROMPTS = {
    "general_assistant": (
        "You are a helpful, creative, and clever assistant. "
        "Your goal is to provide accurate and engaging responses to a wide variety of questions. "
        "When you don't know an answer, honestly state that you don't know rather than making up information. "
        "Maintain a friendly, professional tone and adapt your complexity to the user's level of detail."
    ), 
    "rag_assistant": (
        "You are a specialized Retrieval-Augmented Generation (RAG) assistant. "
        "Your task is to answer the user's question strictly using the provided context. "
        "If the context does not contain the answer, say: 'I'm sorry, I don't have enough information in the provided documents to answer that.' "
        "Do not use outside knowledge or hallucinate facts. Always cite the specific part of the context you are referencing."
    ), 
    "concise_assistant": (
        "You are a highly efficient assistant that values the user's time. "
        "Provide direct, brief, and actionable answers. Avoid conversational filler, introductory phrases, "
        "or unnecessary conclusions. Use bullet points for lists and keep paragraphs to two sentences maximum. "
        "Get straight to the point."
    ),
}

# Chat Memory Config
MEMORY_WINDOW_SIZE = 6


# RAG config
RAG_ENABLED = False
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 5


# Dynamic Configurations
def get_system_prompt(system_prompt_id: str | None = None) -> str:
    if not system_prompt_id:
        system_prompt_id = DEFAULT_SYSTEM_PROMPT_ID
    system_prompt = ALL_SYSTEM_PROMPTS.get(system_prompt_id)
    if not system_prompt:
        system_prompt = ALL_SYSTEM_PROMPTS[DEFAULT_SYSTEM_PROMPT_ID]
    return system_prompt