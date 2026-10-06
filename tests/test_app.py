import pytest

from app import Product, create_app, db


@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        db.session.add(Product(name="Test Item", price_cents=1999, stock=5))
        db.session.commit()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_list_products(client):
    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Item"
    assert data[0]["price"] == 19.99


def test_missing_product_returns_404(client):
    assert client.get("/api/products/999").status_code == 404

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'ShopHub' in response.data
