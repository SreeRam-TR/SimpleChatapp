from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
from database import get_connection
import json
from datetime import datetime

router = APIRouter()

# Store active connections
active_connections: Dict[str, WebSocket] = {}

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections[client_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Store message in database
            conn = await get_connection()
            try:
                await conn.execute("""
                    INSERT INTO messages (sender_id, receiver_id, content)
                    VALUES ($1, $2, $3)
                """, message_data['sender_id'], message_data['receiver_id'], message_data['content'])
                
                # Format message for sending
                message_to_send = {
                    'sender_id': message_data['sender_id'],
                    'receiver_id': message_data['receiver_id'],
                    'content': message_data['content'],
                    'timestamp': datetime.now().isoformat()
                }
                
                # Send to receiver if online
                if message_data['receiver_id'] in active_connections:
                    await active_connections[message_data['receiver_id']].send_text(
                        json.dumps(message_to_send)
                    )
                
                # Send back to sender for confirmation
                await websocket.send_text(json.dumps(message_to_send))
                
            finally:
                await conn.close()
                
    except WebSocketDisconnect:
        if client_id in active_connections:
            del active_connections[client_id]
    except Exception as e:
        print(f"Error: {e}")
        if client_id in active_connections:
            del active_connections[client_id]