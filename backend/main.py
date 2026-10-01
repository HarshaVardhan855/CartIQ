from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import search, products, compare, ask, email
from database.connection import init_db
from utils.logger import logger

app = FastAPI(
    title="CartIQ API",
    description="AI-powered e-commerce product discovery and comparison platform API",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
def startup_event():
    logger.info("Initializing CartIQ Backend...")
    init_db()

# Mount routers
app.include_router(search.router)
app.include_router(products.router)
app.include_router(compare.router)
app.include_router(ask.router)
app.include_router(email.router)

@app.get("/api/health", tags=["Health"])
def health_check():
    """
    GET /api/health
    Service health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "CartIQ Backend",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
