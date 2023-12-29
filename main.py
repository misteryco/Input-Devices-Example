import asyncio
import logging
import multiprocessing
from datetime import datetime
from multiprocessing import Manager
import threading
import os

import cv2
import websockets
from pynput.mouse import Listener
from sqlalchemy import create_engine, Column, Integer, String, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.WARNING)

Base = declarative_base()

if not os.path.exists('static'):
    os.makedirs('static')
    print(f"Folder created")


class CapturedImageModel(Base):
    __tablename__ = 'captured_images'

    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    mouse_x = Column(Integer, nullable=False)
    mouse_y = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    image_source = Column(LargeBinary, nullable=True)


def start_mouse_listener(mouse_position, mouse_position_lock, click_position, click_position_lock):
    """
    Starts a mouse listener that tracks mouse movements and clicks, storing relevant information
    in a SQLite database.

    Parameters:
    - mouse_position (dict): Dictionary to store current mouse position {'x': x_value, 'y': y_value}.
    - mouse_position_lock: Lock for ensuring thread-safe access to mouse_position.
    - click_position (dict): Dictionary to store current click position and button state
        {'x': x_value, 'y': y_value, 'button': True/False}.
    - click_position_lock: Lock for ensuring thread-safe access to click_position.
    """
    engine = create_engine(f'sqlite:///captured_images.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    def on_move(x, y):
        """
            Callback function triggered on mouse movement.
        """
        with mouse_position_lock:
            mouse_position['x'] = x
            mouse_position['y'] = y
            logging.debug(f"Mouse moved mouse_position: (X:{mouse_position['x']}, Y:{mouse_position['y']})")

    def on_click(x, y, button, pressed):
        """
            Callback function triggered on mouse movement.
        """
        with click_position_lock:
            click_position['x'] = x
            click_position['y'] = y
            click_position['button'] = False
            if pressed:
                threading.Thread(target=asyncio.run,
                                 args=(capture_and_save_image(
                                     session,
                                     dict(click_position)
                                 ),)).start()
                click_position['button'] = True
                logging.debug("### Button Clicked")
            else:
                click_position['button'] = False

    with Listener(on_move=on_move, on_click=on_click) as listener:
        listener.join()


async def capture_and_save_image(session, click_coords):
    """
    Captures an image from the default camera, saves it as a PNG file, and stores
    relevant information in a database.

    Parameters:
    - session (sqlalchemy.orm.Session): SQLAlchemy database session for database operations.
    - click_coords (dict): Dictionary containing 'x' and 'y' coordinates of the mouse click.
    """
    try:
        cap = cv2.VideoCapture(0)

        # Check if the camera is opened successfully
        if not cap.isOpened():
            raise Exception("Error: Unable to open the camera. Make sure it is connected.")

        ret, frame = cap.read()

        _, buffer = cv2.imencode('.png', frame)
        image_binary = buffer.tobytes()

        timestamp = datetime.now().strftime("-%d%H%M%S")
        f_name = f'captured_image{timestamp}.png'
        image_filename = os.path.join(os.path.dirname(__file__), 'static', f_name)
        cv2.imwrite(image_filename, frame)
        logging.info(f"Image saved as {f_name}")

        image_entry = CapturedImageModel(path=f"{f_name}",
                                         mouse_x=click_coords['x'],
                                         mouse_y=click_coords['y'],
                                         image_source=image_binary)
        session.add(image_entry)
        session.commit()

        cap.release()

    except Exception as e:
        logging.error(f"Error capturing and saving image: {e}")


def start_websocket_server(mouse_position, mouse_position_lock, click_position, click_position_lock):
    """
        Start a WebSocket server that streams current mouse position and click state.

        Parameters:
        - mouse_position (multiprocessing.managers.DictProxy): Shared dictionary for mouse position.
        - mouse_position_lock (multiprocessing.RLock): Lock for synchronizing access to mouse_position.
        - click_position (multiprocessing.managers.DictProxy): Shared dictionary for click position and state.
        - click_position_lock (multiprocessing.RLock): Lock for synchronizing access to click_position.
        """

    async def run_websocket_server(websocket, path):
        """
        Runs the WebSocket server.

        Parameters:
        - websocket: WebSocket connection object.
        - path: The requested WebSocket path.
        """
        while True:
            try:
                with mouse_position_lock and click_position_lock:
                    logging.debug(f"({mouse_position['x']}, {mouse_position['y']}, "
                                  f"button: {click_position['button']})")

                    await websocket.send(
                        f"current x={mouse_position['x']}, "
                        f"current y={mouse_position['y']}, "
                        f"click ?: {click_position['button']}"
                    )
            except websockets.exceptions.ConnectionClosed:
                logging.info("Client disconnected. Stopping the server loop.")
            except Exception as e:
                logging.error(f"Error sending mouse position: {e}")
            await asyncio.sleep(0.1)
            '''
            Adjustable sleep duration for performance setup.
            '''

    asyncio.get_event_loop().run_until_complete(websockets.serve(run_websocket_server, "localhost", 8765))
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    with Manager() as manager:
        # Shared dictionary's to store inter process data
        mouse_position = manager.dict({'x': 0, 'y': 0})
        click_position = manager.dict({'x': 0, 'y': 0, 'button': False})

        # Locks to synchronize access to shared data
        mouse_position_lock = manager.RLock()
        click_position_lock = manager.RLock()

        # Creating processes for the Mouse listener and for WebSocket server
        mouse_listener_process = multiprocessing.Process(target=start_mouse_listener,
                                                         args=(mouse_position, mouse_position_lock, click_position,
                                                               click_position_lock))

        websocket_server_process = multiprocessing.Process(target=start_websocket_server,
                                                           args=(mouse_position, mouse_position_lock, click_position,
                                                                 click_position_lock))

        # Starting processes concurrently
        mouse_listener_process.start()
        websocket_server_process.start()

        # Waiting for processes to finish
        mouse_listener_process.join()
        websocket_server_process.join()
