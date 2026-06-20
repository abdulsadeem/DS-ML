import requests
import os
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")


def fetch_all_sites(query: str):
    url = "https://serpapi.com/search.json"

    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": SERPAPI_KEY,
        "gl": "in",
        "hl": "en"
    }

    response = requests.get(url, params=params)
    data = response.json()

    products = []

    for item in data.get("shopping_results", [])[:12]:
        source = item.get("source", "Unknown")
        title = item.get("title", "Unknown Product")
        rating = float(item.get("rating", 4))

        price_text = str(item.get("price", "0"))
        digits = "".join(ch for ch in price_text if ch.isdigit())
        price = int(digits) if digits else 0

        # SmartBuy scoring logic
        score = round((rating * 20) + max(0, 100 - price / 100), 2)

        recommendation = "BUY NOW" if score >= 80 else "WAIT"

        products.append({
            "product_name": title,
            "platform": source,
            "current_price": price,
            "rating": rating,
            "smartbuy_score": score,
            "recommendation": recommendation,
            "product_url": item.get("link", ""),
            "image_url": item.get("thumbnail", "")
        })

    # sort best first
    products = sorted(
        products,
        key=lambda x: x["smartbuy_score"],
        reverse=True
    )

    return products