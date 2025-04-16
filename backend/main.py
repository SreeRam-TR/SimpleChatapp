from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from websocket import router as ws_router
from auth import router as auth_router

app = FastAPI()

# Add your frontend URL to allowed origins
origins = [
    "https://chatapp-frontend-s6uf.onrender.com",  # your actual frontend URL
]


# Add CORS middleware before any routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use * just for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers with prefix
app.include_router(auth_router, prefix="")  # Make sure there's no prefix for auth routes
app.include_router(ws_router)

@app.get("/")
def read_root():
    return {"message": "Chat App API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
