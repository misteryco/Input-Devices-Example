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

5. **Run the Application with local html client:**

    ```bash
    python main.py
    ```
    - open in browser the `index.html` from templates folder to see mouse coordinates stream.

6. **Using Flask based websocket client:**
    ```bash
    python main.py
    ```
    - in separate terminal window, run:
   ```bash
    python flask_websocket_client.py
    ```
    - open http://127.0.0.1:5000 see mouse coordinates stream.
