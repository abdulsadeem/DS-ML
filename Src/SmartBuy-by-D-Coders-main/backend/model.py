def rank_products(products):
    ranked = []

    for p in products:
        # Safe defaults if field missing
        rating = p.get("rating", 4)
        seller_score = p.get("seller_score", 80)
        delivery_days = p.get("delivery_days", 3)
        current_price = p.get("current_price", 1000)

        score = (
            0.35 * rating * 20
            + 0.25 * seller_score
            + 0.20 * max(0, 100 - delivery_days * 10)
            + 0.20 * max(0, 100 - current_price / 100)
        )

        p["smartbuy_score"] = round(score, 2)
        p["recommendation"] = "BUY NOW" if score >= 80 else "WAIT"

        ranked.append(p)

    ranked.sort(key=lambda x: x["smartbuy_score"], reverse=True)
    return ranked