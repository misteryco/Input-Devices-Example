import asyncio
import websockets


async def run_websocket_client():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received message: {message}")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run_websocket_client())
