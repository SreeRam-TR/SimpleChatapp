import os
from dotenv import load_dotenv
import asyncpg

load_dotenv()

async def get_connection():
    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise e