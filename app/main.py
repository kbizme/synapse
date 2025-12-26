from fastapi import FastAPI
from app.api import chat

# creating the synapse app
app = FastAPI(title='Synapse')

# including the chat router
app.include_router(chat.router)



