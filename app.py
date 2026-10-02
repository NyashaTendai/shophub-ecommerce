import os

from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, default="")
    price_cents = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price_cents / 100,
            "stock": self.stock,
        }


def normalize_db_url(url):
    # Neon gives postgresql://...; SQLAlchemy needs to know to use psycopg v3
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def create_app(config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = normalize_db_url(
        os.environ.get("DATABASE_URL", "sqlite:///shophub.db")
    )
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}
    if config:
        app.config.update(config)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/")
    def home():
        return """
        <h1>Welcome to ShopHub</h1>
        <p>Cloud-Native E-Commerce Platform</p>
        <p><a href="/api/products">Browse products (API)</a></p>
        """

    @app.route("/health")
    def health():
        return jsonify(status="ok")

    @app.route("/api/products")
    def list_products():
        products = Product.query.order_by(Product.id).all()
        return jsonify([p.to_dict() for p in products])

    @app.route("/api/products/<int:product_id>")
    def get_product(product_id):
        product = db.get_or_404(Product, product_id)
        return jsonify(product.to_dict())

    @app.cli.command("seed")
    def seed():
        """Add sample products if the table is empty."""
        if Product.query.count() == 0:
            db.session.add_all([
                Product(name="Wireless Headphones", description="Over-ear, 30h battery", price_cents=5999, stock=25),
                Product(name="Mechanical Keyboard", description="Hot-swappable switches", price_cents=8900, stock=12),
                Product(name="USB-C Hub", description="7-in-1 adapter", price_cents=3499, stock=40),
            ])
            db.session.commit()
            print("Seeded 3 products.")
        else:
            print("Products already exist, skipping.")

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)