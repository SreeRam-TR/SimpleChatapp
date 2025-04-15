from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from websocket import router as ws_router
from auth import router as auth_router
import os

app = FastAPI()

# Update CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend URL once deployed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws_router)
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "Chat App API is running."}