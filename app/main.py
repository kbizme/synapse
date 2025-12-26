from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat

# creating the synapse app
app = FastAPI(title='Synapse')

# including the chat router
app.include_router(chat.router)


# adding the CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

