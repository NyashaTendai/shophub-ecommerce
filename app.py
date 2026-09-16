from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <h1>Welcome to ShopHub</h1>
    <p>Cloud-Native E-Commerce Platform</p>
    <p>Flask application is running successfully!</p>
    """


if __name__ == "__main__":
    app.run(debug=True)