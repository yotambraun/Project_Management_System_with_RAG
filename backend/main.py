
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.routes import router as api_router
from .database.database import engine
from .database import models
from .ai_engine.rag.vector_store import vector_store
from .database.models import Base, User, Project, Task, TeamMember

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered project management system with RAG",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    return {"message": f"Welcome to the {settings.APP_NAME} API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)