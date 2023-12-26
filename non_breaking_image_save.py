import cv2
import asyncio
import threading
from pynput import mouse

# Global variable to store mouse coordinates
mouse_coordinates = [0, 0]
img_num = 0


async def capture_and_save_image():
    global img_num
    cap = cv2.VideoCapture(0)  # Zero defines main webcam
    ret, frame = cap.read()

    img_num += 1
    image_filename = f"captured_image_{img_num}.png"
    cv2.imwrite(image_filename, frame)
    print(f"Image saved as {image_filename}")

    cap.release()  # Stopping capture


def on_move(x, y):
    mouse_coordinates[0], mouse_coordinates[1] = x, y
    print(f"Mouse moved to ({x}, {y})")


def on_click(x, y, button, pressed):
    if pressed:
        print(f"Mouse clicked at ({x}, {y}) with {button}")
        threading.Thread(target=asyncio.run, args=(capture_and_save_image(),)).start()


def handle_mouse_events():
    with mouse.Listener(on_move=on_move, on_click=on_click) as listener:
        listener.join()


async def main():
    # Run mouse event handling in a separate thread
    threading.Thread(target=handle_mouse_events).start()


if __name__ == "__main__":
    asyncio.run(main())
