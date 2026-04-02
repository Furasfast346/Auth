from fastapi import FastAPI, HTTPException, Depends
import uvicorn
from pydantic import BaseModel, Field

app = FastAPI()

class Users(BaseModel):
    pass
