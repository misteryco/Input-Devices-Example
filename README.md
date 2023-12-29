# Input-Devices-Example

Basic-Input-Devices an example

# This app streams mouse coordintates via websocket server, and on a mouse click capture image using main webcam of the

machine.
Mouse coordinates stream is visible via html file.
Captured images are saved on the disk, it's not a good practice to save image in a db.
The app use pynput library, on Linux it needs additional setting:
   When running under X, the following must be true:
      1. An X server must be running.
      2. The environment variable $DISPLAY must be set.

## Prerequisites

Install Python: [python.org](https://www.python.org/downloads/).
For linux -> Install X server  :  [python.org](https://www.python.org/downloads/).

## Setup

1. **Clone this Repository:**

    ```bash
    git clone https://github.com/misteryco/Input-Devices-Example.git
    cd Input-Devices-Example
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

6. **Run data:**
    - In terminal window run:
    ```bash
    python main.py
    ```
    - In separate terminal window, run:
   ```bash
    python flask_app.py
    ```
    - open http://127.0.0.1:5000.
    - Images are saved on disk in subfolder of the project named - "template".

## Stack

- [Python](https://www.python.org/)
- [Websockets](https://websockets.readthedocs.io/en/stable/index.html)
- [OpenCV](https://docs.opencv.org/4.x/)
- [pynput](https://pynput.readthedocs.io/en/latest/index.html)
- [Flask](https://flask.palletsprojects.com/en/3.0.x/)