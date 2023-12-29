from datetime import datetime
from io import BytesIO

from flask import Flask, render_template, request, send_file

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
    image_source = db.Column(db.LargeBinary, nullable=True)


@app.route('/data', methods=['GET'])
def read_from_database():
    if request.method == 'GET':
        rows = CapturedImage.query.all()
        return render_template('data.html', rows=rows)
    return "Method Not Allowed", 405


@app.route('/download_image/<int:image_id>')
def download_image(image_id):
    # Retrieve the image data from the database based on the image ID
    image_entry = CapturedImage.query.get(image_id)

    if image_entry is None or image_entry.image_source is None:
        return "Image not found", 404

    # Create a BytesIO object to hold the image data
    image_data = BytesIO(image_entry.image_source)

    # Send the image file in the response
    return send_file(
        image_data,
        mimetype='image/png',
        as_attachment=True,
        download_name=f'{image_entry.path}'
    )


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
