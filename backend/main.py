from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from websocket import router as ws_router
from auth import router as auth_router
import os

app = FastAPI()

# Update CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you should list specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routers
app.include_router(ws_router)
app.include_router(auth_router)

@app.get("/")
async def read_root():
    return {"status": "ok", "message": "Chat App API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))