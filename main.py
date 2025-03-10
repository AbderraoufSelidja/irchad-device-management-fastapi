from fastapi import FastAPI
from api import devices, maintainers
from db.db_setup import engine



app = FastAPI()

app.include_router(devices.router)
# app.include_router(maintainers.router) 