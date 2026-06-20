def normalize_products(products):
    grouped = []
    for p in products:
        p['normalized_name'] = p['product_name'].lower().replace("men's", '').strip()
        grouped.append(p)
    return grouped