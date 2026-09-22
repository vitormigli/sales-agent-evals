"""Synthetic product catalog for a fictional online store. No real business."""

PRODUCTS: list[dict] = [
    {"id": "p001", "nome": "Cadeira ergonômica Aurora", "categoria": "móveis",
     "preco": 899.90, "estoque": 12},
    {"id": "p002", "nome": "Mesa de escritório Lumen 120cm", "categoria": "móveis",
     "preco": 649.00, "estoque": 5},
    {"id": "p003", "nome": "Monitor 27\" UltraWide Nimbus", "categoria": "eletrônicos",
     "preco": 1799.00, "estoque": 0},
    {"id": "p004", "nome": "Teclado mecânico Cinder 75%", "categoria": "eletrônicos",
     "preco": 349.90, "estoque": 30},
    {"id": "p005", "nome": "Headset sem fio Orbit", "categoria": "eletrônicos",
     "preco": 429.00, "estoque": 8},
    {"id": "p006", "nome": "Luminária de mesa LED Solstice", "categoria": "móveis",
     "preco": 129.90, "estoque": 22},
    {"id": "p007", "nome": "Suporte para notebook Ridge", "categoria": "acessórios",
     "preco": 89.90, "estoque": 40},
    {"id": "p008", "nome": "Webcam Full HD Focal", "categoria": "eletrônicos",
     "preco": 259.00, "estoque": 3},
]


def find_products(query: str) -> list[dict]:
    q = query.strip().lower()
    if not q:
        return PRODUCTS
    return [
        p for p in PRODUCTS
        if q in p["nome"].lower() or q in p["categoria"].lower()
    ]


def get_product(product_id: str) -> dict | None:
    return next((p for p in PRODUCTS if p["id"] == product_id), None)
