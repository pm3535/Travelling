from fastapi import FastAPI
from fastapi.middleware import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from back.core.config import settings
from back.core.database import create_tables


from back.api.routers.auth         import router as auth_router
from back.api.routers.trips        import router as trips_router
from back.api.routers.search       import router as search_router
from back.api.routers.agent        import router as agent_router
from back.api.routers.destinations import router as destinations_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_tables()
    print(f"✅  {settings.APP_NAME} started — DEBUG={settings.DEBUG}")
    yield
    # Shutdown
    print("👋  Shutting down...")



app = FastAPI(
    title=f"{settings.APP_NAME} API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


app.include_router(auth_router,         prefix="/api")
app.include_router(trips_router,        prefix="/api")
app.include_router(search_router,       prefix="/api")
app.include_router(agent_router,        prefix="/api")
app.include_router(destinations_router, prefix="/api")

@app.get('/')
async def Travel():
    return {"status": "ok", "app":settings.APP_NAME}
    
