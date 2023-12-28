from flask import Flask, render_template, request
from flask_socketio import SocketIO
import sqlite3

app = Flask(__name__)
socketio = SocketIO(app)

DATABASE = "captured_images.db"


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row  # Allows fetching rows as dictionaries
    return db


@app.route('/data', methods=['GET'])
def read_from_database():
    if request.method == 'GET':
        db = get_db()
        cursor = db.cursor()

        query = "SELECT * FROM captured_images;"
        cursor.execute(query)
        results = cursor.fetchall()
        rows = [dict(row) for row in results]

        # You can now use the 'results' variable in your template or return it as JSON
        return render_template('data.html', rows=rows)
    return "Method Not Allowed", 405  # HTTP status code 405 for Method Not Allowed


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
