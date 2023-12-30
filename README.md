# Input-Devices-Example

Basic example demonstrating the usage of input devices with Python.

# About the app:

This Python code sets up a system for capturing mouse movements and clicks, saving corresponding images and data to a SQLite database, 
and streaming the real-time mouse position and click state to a WebSocket server, using multiprocessing for parallel execution and asyncio for asynchronous handling.

1. Mouse coordinates stream is visible via index.html in 'templates' folder, or with provided "test_web_socket.py".

Captured images are saved on the disk, and also as binary in the DB.

The app use pynput library, on Linux it may needs additional installation and configuration:

      1. An X server must be running.
      2. The environment variable $DISPLAY must be set.
      3. usage of pyinput version 1.6.0 , this should be changed in requirements.txt before runnting 'pip install -r requirements.txt' command
.      

2. As secondary app there is a flask server (flask_app.py)that provide access to view the DB and to download images from
   the DB.

## Prerequisites

Python: [python.org](https://www.python.org/downloads/).

For linux -> X server  :  [x.org](https://www.x.org/wiki/).

## Setup

1. **Clone this Repository:**

    ```bash
    git clone https://github.com/misteryco/Input-Devices-Example.git
    cd Input-Devices-Example
    ```
    2. On linux install X server on Ubuntu/Debian-based systems :
          ```Bash
       sudo apt update
       sudo apt install xorg 
       ```
2. **Create new Virtual Environment:**

    ```bash
    python -m venv venv
    ```

3. **Activate the Virtual Environment:**

    - On Windows:

        ```bash
        .\venv\Scripts\activate
        ```

    - On macOS/Linux:

        ```bash
        source venv/bin/activate
        ```

4. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

6. **Run the project:**
    - In terminal window run:
    ```bash
    python main.py
    ```
    - In separate terminal window, run:
   ```bash
   python flask_app.py
    ```
    - open http://127.0.0.1:5000.

## Stack

- [Python](https://www.python.org/)
- [Websockets](https://websockets.readthedocs.io/en/stable/index.html)
- [sqlalchemy](https://docs.sqlalchemy.org/en/20/)
- [OpenCV](https://docs.opencv.org/4.x/)
- [pynput](https://pynput.readthedocs.io/en/latest/index.html)
- [Flask](https://flask.palletsprojects.com/en/3.0.x/)
