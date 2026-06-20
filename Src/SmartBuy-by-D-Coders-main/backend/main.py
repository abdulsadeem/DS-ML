from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from scraper import fetch_all_sites
from model import rank_products
from image_search import image_to_query

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
@app.get("/")
def home():
    return {"message": "SmartBuy API is live 🚀"}

class SearchRequest(BaseModel):
    query: str


@app.post("/search")
def search(req: SearchRequest):
    products = fetch_all_sites(req.query)
    ranked = rank_products(products)
    return {"results": ranked}


@app.post("/image-search")
async def image_search(file: UploadFile = File(...)):
    path = f"/tmp/{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())

    query = image_to_query(path)
    products = fetch_all_sites(query)
    ranked = rank_products(products)

    return {
        "detected_query": query,
        "results": ranked
    }