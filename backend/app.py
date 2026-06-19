from flask import Flask
from routes.hostel_routes import hostel_bp
from routes.review_routes import review_bp
from routes.admin_routes import admin_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://review-system-sigma.vercel.app", "https://review-system-km73.onrender.com"])

app.register_blueprint(
    hostel_bp,
    url_prefix="/api"
)

app.register_blueprint(
    review_bp,
    url_prefix="/api"
)

app.register_blueprint(
    admin_bp,
    url_prefix="/api"
)

if __name__ == "__main__":
    app.run(
    host="0.0.0.0",
    port=5001,
    debug=True
)