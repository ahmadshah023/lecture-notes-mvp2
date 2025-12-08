"""
Minimal test to verify Vercel Python setup works
"""
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
def test():
    return {"status": "ok", "message": "Vercel Python is working!"}

@app.get("/test")
def test_path():
    return {"test": "success"}

handler = Mangum(app, lifespan="off")

