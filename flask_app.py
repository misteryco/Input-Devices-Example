from datetime import datetime

from flask import Flask, render_template, request

from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "captured_images.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
db = SQLAlchemy(app)


class CapturedImage(db.Model):
    __tablename__ = 'captured_images'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String, nullable=False)
    mouse_x = db.Column(db.Integer, nullable=False)
    mouse_y = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)


@app.route('/data', methods=['GET'])
def read_from_database():
    if request.method == 'GET':
        rows = CapturedImage.query.all()
        return render_template('data.html', rows=rows)
    return "Method Not Allowed", 405


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
