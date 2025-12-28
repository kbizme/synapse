from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat_endpoints
from contextlib import asynccontextmanager



# app startup events
@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.persistence import db
    db.init_db()
    yield



# creating the synapse app
app = FastAPI(title='Synapse', lifespan=lifespan)



# including the chat router
app.include_router(chat_endpoints.router)


# adding the CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

