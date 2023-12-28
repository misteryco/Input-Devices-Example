# Input-Devices-Example

Basic Input Devices example

# Mouse coordinates stream plus image capture Setup

## Prerequisites

Install Python: [python.org](https://www.python.org/downloads/).

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
