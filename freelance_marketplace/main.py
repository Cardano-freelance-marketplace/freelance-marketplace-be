from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from freelance_marketplace.core.config import settings
from freelance_marketplace.api.routes.hello import router as hello_router
from freelance_marketplace.middleware.response_wrapper import transform_response_middleware
from dotenv import load_dotenv

load_dotenv()


origins = ['*', "http://localhost:4200"]

app = FastAPI(
    **settings.fastapi.model_dump()
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Apply Middlewares
app.middleware("http")(transform_response_middleware)

# Register routers
app.include_router(hello_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    print("Starting up")
    
@app.on_event("shutdown")
async def on_shutdown():
    print("shutting down")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
