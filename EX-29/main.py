import time

import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.connect import get_db
from src.routes import contacts, auth
from src.services.messages import DB_CONFIG_ERROR, DB_CONNECT_ERROR, WELCOME_MESSAGE

app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are used by the app, such as databases or caches.

    :return: A dictionary with the following keys:
    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    The add_process_time_header function adds a header to the response called &quot;My-Process-Time&quot;
    that contains the time it took for this function to run. This is useful for debugging purposes.

    :param request: Request: Access the request object
    :param call_next: Call the next middleware in the chain
    :return: A response object with an additional header
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["My-Process-Time"] = str(process_time)
    return response


@app.get("/", name='Home')
def read_root():
    """
    The read_root function returns a dictionary with the key &quot;message&quot; and value &quot;Hello&quot;.

    :return: A dictionary
    """
    return {"message": "Hello"}


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is a simple endpoint that can be used to verify the API is up and running.
    It also verifies that the database connection has been established successfully.

    :param db: Session: Pass in the database session object
    :return: A dict with a message key
    """
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        print(result)
        if result is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=DB_CONFIG_ERROR)
        return {"message": WELCOME_MESSAGE}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=DB_CONNECT_ERROR)


app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')

if __name__ == '__main__':
    uvicorn.run(app="main:app", reload=True)