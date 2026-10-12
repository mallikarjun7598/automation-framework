"""Mini Amazon-retail storefront (the application under test).

A deliberately small Flask app so the end-to-end automation story is easy to
follow. It supports: browsing products, searching, adding to a cart, and
checking out. Cart state is kept in the session.

Run locally:
    python -m app.server
    # serves on http://127.0.0.1:5001
"""
from __future__ import annotations

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

# In-memory product catalogue. Keeping it as a module-level list keeps the demo
# simple (no database needed) while still being realistic enough to test.
PRODUCTS = [
    {"id": 1, "name": "Echo Dot (5th Gen)", "price": 49.99, "category": "Devices"},
    {"id": 2, "name": "Kindle Paperwhite", "price": 139.99, "category": "Devices"},
    {"id": 3, "name": "Fire TV Stick 4K", "price": 59.99, "category": "Devices"},
    {"id": 4, "name": "USB-C Charging Cable", "price": 12.49, "category": "Accessories"},
    {"id": 5, "name": "Wireless Mouse", "price": 24.99, "category": "Accessories"},
    {"id": 6, "name": "Stainless Water Bottle", "price": 18.95, "category": "Home"},
]

PRODUCTS_BY_ID = {p["id"]: p for p in PRODUCTS}


def create_app() -> Flask:
    """Application factory (standard Flask pattern; also eases testing)."""
    app = Flask(__name__)
    app.secret_key = "demo-secret-not-for-production"

    def _cart() -> dict[str, int]:
        """Return the cart dict from the session, creating it if absent."""
        return session.setdefault("cart", {})

    @app.context_processor
    def inject_cart_count() -> dict[str, int]:
        cart = session.get("cart", {})
        return {"cart_count": sum(cart.values())}

    @app.route("/")
    def index():
        """Home / product listing, with optional ?q= search filter."""
        query = (request.args.get("q") or "").strip().lower()
        if query:
            items = [p for p in PRODUCTS if query in p["name"].lower()]
        else:
            items = PRODUCTS
        return render_template("index.html", products=items, query=query)

    @app.route("/product/<int:product_id>")
    def product(product_id: int):
        item = PRODUCTS_BY_ID.get(product_id)
        if not item:
            return redirect(url_for("index"))
        return render_template("product.html", product=item)

    @app.route("/cart/add/<int:product_id>", methods=["POST"])
    def add_to_cart(product_id: int):
        if product_id in PRODUCTS_BY_ID:
            cart = _cart()
            cart[str(product_id)] = cart.get(str(product_id), 0) + 1
            session.modified = True
        return redirect(request.referrer or url_for("index"))

    @app.route("/cart")
    def view_cart():
        cart = session.get("cart", {})
        lines = []
        total = 0.0
        for pid, qty in cart.items():
            item = PRODUCTS_BY_ID.get(int(pid))
            if not item:
                continue
            line_total = item["price"] * qty
            total += line_total
            lines.append({"product": item, "qty": qty, "line_total": round(line_total, 2)})
        return render_template("cart.html", lines=lines, total=round(total, 2))

    @app.route("/cart/clear", methods=["POST"])
    def clear_cart():
        session["cart"] = {}
        session.modified = True
        return redirect(url_for("view_cart"))

    @app.route("/checkout", methods=["GET", "POST"])
    def checkout():
        cart = session.get("cart", {})
        if request.method == "POST":
            name = (request.form.get("name") or "").strip()
            if not cart:
                return render_template("checkout.html", error="Your cart is empty.")
            if not name:
                return render_template("checkout.html", error="Name is required.")
            order_id = f"ORD-{abs(hash(name)) % 100000:05d}"
            session["cart"] = {}
            session.modified = True
            return render_template("confirmation.html", order_id=order_id, name=name)
        return render_template("checkout.html", error=None)

    # ---------------------------------------------------------------- apps hub
    @app.route("/apps")
    def apps_home():
        """Simple hub linking to the standalone PWA apps."""
        return render_template("apps_home.html")

    @app.route("/apps/todo")
    def todo_app():
        """To-Do app. Data persists client-side via localStorage."""
        return render_template("todo.html")

    @app.route("/apps/expenses")
    def expenses_app():
        """Expense Tracker. Data persists client-side via localStorage."""
        return render_template("expenses.html")

    # ------------------------------------------------------- PWA plumbing
    @app.route("/manifest.webmanifest")
    def manifest():
        """Web App Manifest — makes the apps installable on mobile/desktop."""
        return app.send_static_file("manifest.webmanifest")

    @app.route("/service-worker.js")
    def service_worker():
        """Service worker — enables offline support and install prompts.

        Served from the root scope so it can control the whole origin.
        """
        resp = app.make_response(app.send_static_file("service-worker.js"))
        resp.headers["Content-Type"] = "application/javascript"
        resp.headers["Service-Worker-Allowed"] = "/"
        return resp

    @app.route("/health")
    def health():
        """Lightweight endpoint CI uses to confirm the app is up."""
        return {"status": "ok"}, 200

    return app


if __name__ == "__main__":
    import os

    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5001"))
    # debug is off by default so the auto-reloader doesn't spawn child processes
    # that the test fixture can't terminate cleanly.
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    create_app().run(host=host, port=port, debug=debug)
