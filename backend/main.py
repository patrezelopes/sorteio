from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import participants, raffles, instagram
from instagram_service import instagram_service
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Ticket Raffle API",
    description="API for managing ticket raffles and participants",
    version="1.0.0"
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(participants.router)
app.include_router(raffles.router)
app.include_router(instagram.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database and Instagram login on startup"""
    init_db()
    
    # Auto-login to Instagram if credentials are provided
    instagram_username = os.getenv("INSTAGRAM_USERNAME")
    instagram_password = os.getenv("INSTAGRAM_PASSWORD")
    
    if instagram_username and instagram_password:
        print(f"🔐 Attempting Instagram login for @{instagram_username}...")
        try:
            success = instagram_service.login(instagram_username, instagram_password)
            if success:
                print(f"✅ Instagram login successful for @{instagram_username}")
            else:
                print(f"⚠️  Instagram login failed for @{instagram_username}")
        except Exception as e:
            print(f"❌ Instagram login error: {str(e)}")
    else:
        print("ℹ️  No Instagram credentials found in environment variables")
        print("   Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in .env file to enable auto-login")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Ticket Raffle API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
