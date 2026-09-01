from fastapi import FastAPI
from app.routes.todo import router as todo_router
from app.routes.user import router as user_router
from contextlib import asynccontextmanager
from app.database.connection import  Base, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()                 # shutdown


app = FastAPI(
    title="FastAPI Todo API",
    description="A FastAPI todo API",
    version="0.1.0",
    contact={
        "name": "John Doe",
        "email": "john.doe@example.com"
    },
    license_info={
        "name": "MIT License"
    },
    lifespan=lifespan
)


app.include_router(todo_router)
app.include_router(user_router)
@app.get("/")
def root():
    return {"message": "Hello World from FastAPI"}