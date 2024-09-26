from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import asyncio

app = FastAPI()

video_path = "Nightcore - My Forever.mp4"

# Список подключенных клиентов
clients = []

async def broadcast_video():
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        for client in clients:
            try:
                await client.send_bytes(frame_bytes)
            except WebSocketDisconnect:
                clients.remove(client)
                print("Client disconnected")

        await asyncio.sleep(1 / cap.get(cv2.CAP_PROP_FPS))

    cap.release()


@app.websocket("/ws/video")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)
        print("Client disconnected")


@app.on_event("startup")
async def start_video_broadcast():
    asyncio.create_task(broadcast_video())

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
