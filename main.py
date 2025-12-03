import os
from turtledemo.clock import display_date_time
from database import getPage
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import requests
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or list your frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)
class LoginForm(BaseModel):
    username: str
    password: str

def getAccessToken():
    load_dotenv()
    token = os.getenv("ACCESS_TOKEN")
    return token

@app.get("/", response_class=HTMLResponse)
def load_page():
    token = getAccessToken()
    print(token)
    if token =="":
        return Path("frontend/Login.html").read_text()
    else:
        return Path("frontend/index.html").read_text(encoding="utf-8")


@app.post("/login", response_class=JSONResponse)
def login(shtuff: LoginForm):
    data = {"username": shtuff.username, "password": shtuff.password}
    response = requests.post("http://46.224.62.71:8080/api/auth/token", data)
    print(response.json())
    print(response.status_code)
    if response.status_code == 200:
        with open(".env", "w") as f:
            f.write(f'ACCESS_TOKEN="{response.json()["access_token"]}"')
        return JSONResponse(status_code=200, content={'redirect': "/index.html"})
    elif response.status_code == 403:
        return JSONResponse(status_code=403, content={"message": "Incorrect username or password"})
    elif response.status_code:
        return JSONResponse(status_code=response.status_code, content={"message": "Login failed"})

@app.get("/getCards", response_class=JSONResponse)
def getCards(page, page_size, request: Request):
    page = int(page)
    page_size = int(page_size)
    result = getPage(page, page_size, request)
    return JSONResponse(status_code=200, content=result)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)
    if not os.path.exists('.env'):
        with open(".env", "w") as f:
            f.write(f'ACCESS_TOKEN=""')
