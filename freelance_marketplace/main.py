from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from freelance_marketplace.api.utils.redis import redis_client
from freelance_marketplace.core.config import settings
from freelance_marketplace.middleware.response_wrapper import transform_response_middleware
from dotenv import load_dotenv
from freelance_marketplace.db.sql.database import init_db, AsyncSessionLocal
from freelance_marketplace.db.no_sql.mongo import mongo_session
from freelance_marketplace.api.routes.user_roles.user_roles import router as user_roles_router
from freelance_marketplace.api.routes.reviews.reviews import router as reviews_router
from freelance_marketplace.api.routes.profiles.profiles import router as profiles_router
from freelance_marketplace.api.routes.portfolios.portfolio import router as portfolio_router
from freelance_marketplace.api.routes.notifications.notifications import router as notifications_router
from freelance_marketplace.api.routes.categories.categories import router as categories_router
from freelance_marketplace.api.routes.sub_categories.subCategories import router as sub_categories_router
from freelance_marketplace.api.routes.services.services import router as services_router
from freelance_marketplace.api.routes.requests.requests import router as requests_router
from freelance_marketplace.api.routes.users.users import router as users_router
from freelance_marketplace.api.routes.hello import router as hello_router
from freelance_marketplace.models.sql.sql_tables import Role, User, MilestoneStatus, WalletTypes, RequestStatus, \
    ServiceStatus, ProposalStatus, OrderStatus, Category, SubCategory

load_dotenv()
origins = ['*', "http://localhost:4200"]


app = FastAPI(
    **settings.fastapi.model_dump()
)

# Rate Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["15/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Apply Middlewares
app.add_middleware(SlowAPIMiddleware)
app.middleware("http")(transform_response_middleware)

app.include_router(hello_router, prefix="/api/v1")
app.include_router(user_roles_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(profiles_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(portfolio_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(sub_categories_router, prefix="/api/v1")
app.include_router(services_router, prefix="/api/v1")
app.include_router(requests_router, prefix="/api/v1")
app.include_router(reviews_router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    try:
        await redis_client.ping()
        print("Redis connection successful.")
    except Exception as e:
        print(f"Redis connection failed: {e}")

    await init_db()
    await mongo_session.init_mongo()
    async with AsyncSessionLocal() as session:
        await Role.seed_roles(session)
        await MilestoneStatus.seed_status(session)
        await WalletTypes.seed_types(session)
        await RequestStatus.seed_status(session)
        await ServiceStatus.seed_status(session)
        await ProposalStatus.seed_status(session)
        await OrderStatus.seed_status(session)
        await Category.seed_categories(session)
        await SubCategory.seed_sub_categories(session)
        await User.seed_users(session)

@app.on_event("shutdown")
async def on_shutdown():
    print("shutting down")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
