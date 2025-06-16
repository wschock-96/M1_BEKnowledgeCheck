from app import create_app
from app.extensions import db

app = create_app('DevelopmentConfig')

with app.app_context():
    db.create_all()

app.run(debug=True)