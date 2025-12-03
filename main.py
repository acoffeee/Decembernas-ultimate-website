from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path
app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def load_page():
    html_path = Path("Frontend/Index.html")
    return html_path.read_text()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)
