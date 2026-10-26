"""OmniCart backend: static files + REST API + linear regression model. Python 3 standard library only."""
import json, os, threading, mimetypes
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.abspath(__file__))
LOCK = threading.Lock()
ORDERS = [
    {"id": "#OC-1048", "customer": "Elena Williams", "email": "elena.w@example.com", "total": 248.0, "status": "Shipped"},
    {"id": "#OC-1047", "customer": "Marcus Chen", "email": "marcus.c@example.com", "total": 129.0, "status": "Processing"},
    {"id": "#OC-1046", "customer": "Sofia Patel", "email": "sofia.p@example.com", "total": 76.5, "status": "Delivered"},
    {"id": "#OC-1045", "customer": "Liam Thompson", "email": "liam.thompson@example.com", "total": 314.0, "status": "Delivered"},
    {"id": "#OC-1044", "customer": "Amara Okafor", "email": "amara.okafor@example.com", "total": 58.0, "status": "Shipped"},
]
SAMPLE_CUSTOMERS = ["Rohan Kapoor", "Maya Patel", "Noah Johnson", "Ava Thompson", "Ethan Chen", "Priya Shah", "Lucas Martin", "Zara Ahmed", "Oliver Brown", "Mei Wong", "Arjun Nair", "Isabella Garcia", "Aarav Singh", "Emma Wilson", "Leo Kim", "Anika Das", "Mason Taylor", "Isha Mehta", "Eli Robinson", "Nina Foster", "Kabir Rao", "Chloe Davis", "Theo Clark", "Sara Ali", "Ryan Murphy", "Diya Iyer", "Hana Suzuki", "Ezra Lewis", "Tara Bose", "Adam Scott"]
ORDER_STATUSES = ["Processing", "Shipped", "Delivered", "Delivered", "Cancelled"]
for i, customer in enumerate(SAMPLE_CUSTOMERS):
    email = customer.lower().replace(" ", ".") + "@example.com"
    ORDERS.append({"id": "#OC-%d" % (1043 - i), "customer": customer, "email": email,
                   "total": round(35 + ((i * 73 + 41) % 465) + (i % 4) * 0.5, 2),
                   "status": ORDER_STATUSES[i % len(ORDER_STATUSES)]})

PRODUCTS = [
    {"name": "Wireless Headphones", "category": "Electronics", "stock": 124},
    {"name": "Everyday Backpack", "category": "Accessories", "stock": 68},
    {"name": "Glass Water Bottle", "category": "Home & living", "stock": 212},
    {"name": "Organic Cotton Tee", "category": "Apparel", "stock": 43},
]
EXTRA_PRODUCTS = [
    ("Trail Running Shoes", "Footwear", 87), ("Ceramic Pour-over Set", "Home & living", 56),
    ("Linen Table Runner", "Home & living", 31), ("Portable Bluetooth Speaker", "Electronics", 93),
    ("Desk Plant Kit", "Home & living", 118), ("Merino Wool Socks", "Apparel", 205),
    ("Leather Card Holder", "Accessories", 24), ("Yoga Mat", "Fitness", 76),
    ("Insulated Travel Mug", "Home & living", 142), ("Canvas Tote Bag", "Accessories", 189),
    ("USB-C Charging Hub", "Electronics", 39), ("Bamboo Cutting Board", "Home & living", 64),
    ("Classic Denim Jacket", "Apparel", 18), ("Wireless Charging Stand", "Electronics", 51),
    ("Organic Face Cleanser", "Beauty", 97), ("Scented Candle Trio", "Home & living", 33),
    ("Kids Rain Jacket", "Apparel", 46), ("Compact Travel Umbrella", "Accessories", 12),
    ("Resistance Band Set", "Fitness", 109), ("Minimalist Wall Clock", "Home & living", 27),
]
PRODUCTS.extend({"name": name, "category": category, "stock": stock} for name, category, stock in EXTRA_PRODUCTS)

# ---- Regression model: weekly_sales = a + b * week (simple linear regression) ----
XS = list(range(1, 53))
WEEKLY = [2000 + 150 * w + ((w * 37) % 7 - 3) * 60 for w in XS]   # 52 weeks of sample sales
SPLIT = 42                                                        # train on 42 weeks, test on the final 10

def fit(xs, ys):
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return my - b * mx, b

A, B = fit(XS[:SPLIT], WEEKLY[:SPLIT])
predict = lambda w: A + B * w

def r2(xs, ys):
    my = sum(ys) / len(ys)
    return 1 - sum((y - predict(x)) ** 2 for x, y in zip(xs, ys)) / sum((y - my) ** 2 for y in ys)

MODEL = {
    "type": "simple linear regression", "intercept": round(A, 2), "slope": round(B, 2),
    "train_r2": round(r2(XS[:SPLIT], WEEKLY[:SPLIT]), 4),
    "test_r2": round(r2(XS[SPLIT:], WEEKLY[SPLIT:]), 4),
    "test_mae": round(sum(abs(y - predict(x)) for x, y in zip(XS[SPLIT:], WEEKLY[SPLIT:])) / (len(XS) - SPLIT), 2),
    "train_weeks": SPLIT, "test_weeks": len(XS) - SPLIT,
}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def send_json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path); q = parse_qs(u.query)
        if u.path == "/api/health": return self.send_json(200, {"status": "ok"})
        if u.path == "/api/orders": return self.send_json(200, ORDERS)
        if u.path == "/api/products": return self.send_json(200, PRODUCTS)
        if u.path == "/api/model": return self.send_json(200, MODEL)
        if u.path == "/api/forecast":
            try:
                week = int(q.get("week", [""])[0])
                if not 1 <= week <= 104: raise ValueError
            except ValueError:
                return self.send_json(400, {"error": "week must be an integer from 1 to 104"})
            return self.send_json(200, {"week": week, "predicted_sales": round(predict(week), 2)})
        if u.path.startswith("/api/"): return self.send_json(404, {"error": "not found"})
        rel = u.path.lstrip("/") or "index.html"
        p = os.path.normpath(os.path.join(ROOT, rel))
        if not p.startswith(ROOT) or not os.path.isfile(p):
            return self.send_json(404, {"error": "not found"})
        data = open(p, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", (mimetypes.guess_type(p)[0] or "application/octet-stream") + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers(); self.wfile.write(data)

    def do_POST(self):
        if urlparse(self.path).path != "/api/orders": return self.send_json(404, {"error": "not found"})
        try:
            d = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            customer, email, total = str(d["customer"]).strip(), str(d["email"]), float(d["total"])
            if not customer or "@" not in email or not 0 < total <= 100000: raise ValueError
        except (ValueError, KeyError, TypeError):
            return self.send_json(400, {"error": "need customer, valid email, and total between 0 and 100000"})
        with LOCK:
            o = {"id": "#OC-%d" % (max(int(order["id"].split("-")[1]) for order in ORDERS) + 1), "customer": customer, "email": email,
                 "total": total, "status": "Processing"}
            ORDERS.append(o)
        self.send_json(201, o)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"OmniCart running at http://localhost:{port}  (API demo: /api.html)")
    ThreadingHTTPServer(("", port), Handler).serve_forever()
