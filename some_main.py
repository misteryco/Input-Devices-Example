import asyncio
import logging
import multiprocessing
from datetime import datetime
from multiprocessing import Manager
import threading

import cv2
import websockets
from pynput.mouse import Listener

logging.basicConfig(level=logging.DEBUG)


def start_mouse_listener(mouse_position, mouse_position_lock, click_position, click_position_lock):
    process_id = multiprocessing.current_process().name
    logging.debug(f"Mouse listener process ID: {process_id}")

    def on_move(x, y):
        with mouse_position_lock:
            mouse_position['x'] = x
            mouse_position['y'] = y
            logging.debug(
                f"Mouse moved mouse_position: (X:{mouse_position['x']}, Y:{mouse_position['y']}) in process {process_id}")

    def on_click(x, y, button, pressed):
        with click_position_lock:
            click_position['x'] = x
            click_position['y'] = y
            click_position['button'] = False
            if pressed:
                threading.Thread(target=asyncio.run, args=(capture_and_save_image(),)).start()
                # save_data_to_file(f"X={click_position['x']},Y={click_position['y']}")
                click_position['button'] = True
                logging.debug(f"#? ###Button Clicked")
            else:
                click_position['button'] = False

    with Listener(on_move=on_move, on_click=on_click) as listener:
        listener.join()


async def capture_and_save_image():
    # Use OpenCV to capture image from webcam
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()

    timestamp = datetime.now().strftime("-%d%H%M%S")

    # Save the captured image to disk
    image_filename = f"captured_image{timestamp}.png"
    cv2.imwrite(image_filename, frame)
    print(f"Image saved as {image_filename}")

    # Close the webcam capture
    cap.release()


# def save_data_to_file(data):
#     # Specify the file path where you want to save the text file
#     file_path = "example.txt"
#
#     # Open the file in write mode and write the content
#     with open("capture_coordinates.txt", "w") as file:
#         file.write(data)
#
#     logging.debug(f"Text file saved successfully at: {file_path}")


def start_websocket_server(mouse_position, mouse_position_lock, click_position, click_position_lock):
    async def run_websocket_server(websocket, path):
        while True:
            try:
                with mouse_position_lock and click_position_lock:
                    logging.debug(f"????????????????????????????????????????????????????????????FOR test WEB_SOCKET: "
                                  f"({mouse_position['x']}, "
                                  f"{mouse_position['y']}, "
                                  f"button: {click_position['button']})")
                    await websocket.send(
                        f"current x={mouse_position['x']}, "
                        f"current y={mouse_position['y']}, "
                        f"click ?: {click_position['button']}"
                    )
            except Exception as e:
                logging.error(f"Error sending mouse position: {e}")
            await asyncio.sleep(0.1)  # Sleep duration

    # Start the WebSocket server
    asyncio.get_event_loop().run_until_complete(websockets.serve(run_websocket_server, "localhost", 8765))
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    # Create a multiprocessing Manager to create managed objects
    with Manager() as manager:
        # Create a managed dictionary to store mouse position
        mouse_position = manager.dict({'x': 0, 'y': 0})
        click_position = manager.dict({'x': 0, 'y': 0, 'button': False})
        mouse_position_lock = manager.RLock()
        click_position_lock = manager.RLock()

        # Create a multiprocessing Process for listening to mouse events
        mouse_listener_process = multiprocessing.Process(target=start_mouse_listener,
                                                         args=(
                                                             mouse_position,
                                                             mouse_position_lock,
                                                             click_position,
                                                             click_position_lock
                                                         ))

        # Create a multiprocessing Process for the WebSocket server
        websocket_server_process = multiprocessing.Process(target=start_websocket_server,
                                                           args=(
                                                               mouse_position,
                                                               mouse_position_lock,
                                                               click_position,
                                                               click_position_lock
                                                           ))

        # Start the mouse listener process and the WebSocket server process
        mouse_listener_process.start()
        websocket_server_process.start()

        # Wait for both processes to finish
        mouse_listener_process.join()
        websocket_server_process.join()
