from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from passlib.hash import bcrypt
import asyncpg
import os
from database import get_connection
from typing import List

router = APIRouter()

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str

@router.post("/signup")
async def signup(data: SignupRequest):
    conn = await get_connection()
    try:
        hashed_password = bcrypt.hash(data.password)
        await conn.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES ($1, $2, $3)
        """, data.username, data.email, hashed_password)
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    finally:
        await conn.close()
    return {"message": "Signup successful"}

@router.post("/login")
async def login(data: LoginRequest):
    conn = await get_connection()
    user = await conn.fetchrow("SELECT * FROM users WHERE username = $1", data.username)
    await conn.close()
    if not user or not bcrypt.verify(data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Login successful", "user_id": str(user['id'])}

@router.get("/users/search", response_model=List[UserResponse])
async def search_users(query: str):
    conn = await get_connection()
    try:
        users = await conn.fetch("""
            SELECT id, username 
            FROM users 
            WHERE username ILIKE $1
            LIMIT 10
        """, f"%{query}%")
        return [{"id": str(user['id']), "username": user['username']} for user in users]
    finally:
        await conn.close()

@router.get("/messages/{sender_id}/{receiver_id}")
async def get_chat_history(sender_id: str, receiver_id: str):
    conn = await get_connection()
    try:
        messages = await conn.fetch("""
            SELECT id, sender_id, receiver_id, content, timestamp
            FROM messages
            WHERE (sender_id = $1 AND receiver_id = $2)
            OR (sender_id = $2 AND receiver_id = $1)
            ORDER BY timestamp ASC
        """, sender_id, receiver_id)
        
        return [
            {
                "id": str(msg['id']),
                "sender_id": str(msg['sender_id']),
                "receiver_id": str(msg['receiver_id']),
                "content": msg['content'],
                "timestamp": msg['timestamp'].isoformat()
            }
            for msg in messages
        ]
    finally:
        await conn.close()

@router.get("/recent-chats/{user_id}")
async def get_recent_chats(user_id: str):
    conn = await get_connection()
    try:
        recent_users = await conn.fetch("""
            SELECT DISTINCT 
                CASE 
                    WHEN sender_id = $1 THEN receiver_id 
                    ELSE sender_id 
                END as user_id,
                u.username
            FROM messages m
            JOIN users u ON u.id = 
                CASE 
                    WHEN sender_id = $1 THEN receiver_id 
                    ELSE sender_id 
                END
            WHERE sender_id = $1 OR receiver_id = $1
            ORDER BY MAX(m.created_at) DESC
            LIMIT 20
        """, user_id)
        return [{"id": str(user['user_id']), "username": user['username']} for user in recent_users]
    finally:
        await conn.close()