from dotenv import load_dotenv
import os
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.api import router as api_router
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

API_PREFIX = "/api"

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/pura", response_class=HTMLResponse)
async def pura_list(request: Request):
    url = str(request.base_url).rstrip("/") + f"{API_PREFIX}/pura"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        pura_list = resp.json()
    return templates.TemplateResponse("pura_list.html", {"request": request, "pura_list": pura_list})

@app.get("/pura/{id_pura}", response_class=HTMLResponse)
async def pura_detail(request: Request, id_pura: str):
    url = str(request.base_url).rstrip("/") + f"{API_PREFIX}/pura/{id_pura}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        if resp.status_code != 200:
            return HTMLResponse("<h2>Pura not found</h2>", status_code=404)
        pura = resp.json()
    return templates.TemplateResponse("pura_detail.html", {"request": request, "pura": pura})

@app.get("/kabupaten", response_class=HTMLResponse)
async def kabupaten_list(request: Request):
    url = str(request.base_url).rstrip("/") + f"{API_PREFIX}/kabupaten"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        kabupaten_list = resp.json()
    return templates.TemplateResponse("kabupaten_list.html", {"request": request, "kabupaten_list": kabupaten_list})

@app.get("/jenis_pura", response_class=HTMLResponse)
async def jenis_pura_list(request: Request):
    url = str(request.base_url).rstrip("/") + f"{API_PREFIX}/jenis_pura"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        jenis_pura_list = resp.json()
    return templates.TemplateResponse("jenis_pura_list.html", {"request": request, "jenis_pura_list": jenis_pura_list})
