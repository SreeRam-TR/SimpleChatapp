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

@router.api_route("/signup", methods=["POST", "OPTIONS"], include_in_schema=False)
async def signup(data: SignupRequest):
    conn = await get_connection()
    try:
        hashed_password = bcrypt.hash(data.password)
        user_id = await conn.fetchval("""
            INSERT INTO users (username, email, password_hash)
            VALUES ($1, $2, $3)
            RETURNING id
        """, data.username, data.email, hashed_password)
        
        return {
            "message": "Signup successful",
            "user_id": str(user_id)
        }
    except asyncpg.UniqueViolationError:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )
    finally:
        await conn.close()

@router.api_route("/login", methods=["POST", "OPTIONS"], include_in_schema=False)
async def login(data: LoginRequest):
    conn = await get_connection()
    try:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE username = $1",
            data.username
        )
        
        if not user or not bcrypt.verify(data.password, user['password_hash']):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
            
        return {
            "message": "Login successful",
            "user_id": str(user['id'])
        }
    finally:
        await conn.close()

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

@router.get("/messages/{sender_id}/{receiver_id}", response_model=List[dict])
async def get_chat_history(sender_id: str, receiver_id: str):
    conn = await get_connection()
    try:
        messages = await conn.fetch("""
            SELECT sender_id, receiver_id, content, created_at
            FROM messages
            WHERE (sender_id = $1 AND receiver_id = $2)
            OR (sender_id = $2 AND receiver_id = $1)
            ORDER BY created_at ASC
        """, sender_id, receiver_id)
        return [
            {
                "sender_id": str(msg['sender_id']),
                "receiver_id": str(msg['receiver_id']),
                "content": msg['content'],
                "timestamp": msg['created_at'].isoformat()
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