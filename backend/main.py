from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from websocket import router as ws_router
from auth import router as auth_router

app = FastAPI()

# Simplify CORS - allow all origins temporarily to test
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This will allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(ws_router)
app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "Chat App API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))