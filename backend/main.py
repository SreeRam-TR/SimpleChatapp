from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from websocket import router as ws_router
from auth import router as auth_router
import os

app = FastAPI()

# Update CORS settings to include your Render frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://chatapp-frontend-s6uf.onrender.com",  # Your Render frontend URL
        "http://localhost:3000",  # For local development
        "http://localhost:5000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Add routers
app.include_router(ws_router)
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "Chat App API is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))