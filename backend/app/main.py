from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.models import init_db
from app.routers import expenses
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

app = FastAPI(
    title=settings.APP_NAME,
    description="API de gestion de notes de frais pour indépendants",
    version="0.1.0",
    lifespan=lifespan
)

# CORS pour le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(expenses.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Expense Tracker API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
