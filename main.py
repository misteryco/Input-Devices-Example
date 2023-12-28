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
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.WARNING)

Base = declarative_base()


class CapturedImageModel(Base):
    __tablename__ = 'captured_images'

    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    mouse_x = Column(Integer, nullable=False)
    mouse_y = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)


def start_mouse_listener(mouse_position, mouse_position_lock, click_position, click_position_lock):
    engine = create_engine(f'sqlite:///captured_images.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    def on_move(x, y):
        with mouse_position_lock:
            mouse_position['x'] = x
            mouse_position['y'] = y
            logging.debug(f"Mouse moved mouse_position: (X:{mouse_position['x']}, Y:{mouse_position['y']})")

    def on_click(x, y, button, pressed):
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
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()

    timestamp = datetime.now().strftime("-%d%H%M%S")
    f_name = f'captured_image{timestamp}.png'
    image_filename = os.path.join(os.path.dirname(__file__), 'images', f_name)
    cv2.imwrite(image_filename, frame)
    print(f"Image saved as {f_name}")

    # Save the image path to the database
    image_entry = CapturedImageModel(path=f_name, mouse_x=click_coords['x'], mouse_y=click_coords['y'])
    session.add(image_entry)
    session.commit()

    cap.release()


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
        Run the WebSocket server handler.

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
            except Exception as e:
                logging.error(f"Error sending mouse position: {e}")
            await asyncio.sleep(0.1)
            '''
            Adjust above sleep duration for performance.
            Introducing a small delay defines the rate at which the server sends updates. 
            Preventing the while loop from running too frequently. 
            Otherwise, the loop might run as fast as the system can handle, consuming unnecessary resources.
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
