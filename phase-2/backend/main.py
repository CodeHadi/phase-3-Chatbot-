from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine
from backend.models import SQLModel
from backend.routes.tasks import router as tasks_router
from backend.routes.auth import router as auth_router
from backend.routes.mcp import router as mcp_router
from backend.routes.chat import router as chat_router

app = FastAPI(title="Todo API - Phase II Hackathon")

# CORS allow frontend se calls (Next.js localhost:3000 se)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

# Startup event: tables create karo Neon DB mein
@app.on_event("startup")
def startup_event():
    SQLModel.metadata.create_all(engine)
    print("✅ Tables created in Neon DB!")

@app.get("/")
def root():
    return {"message": "Todo Backend Running! Visit /docs for API"}

# Include routers
app.include_router(tasks_router)
app.include_router(auth_router)
app.include_router(mcp_router)
app.include_router(chat_router)