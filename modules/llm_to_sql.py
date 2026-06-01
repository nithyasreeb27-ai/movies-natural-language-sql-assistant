import os
import re
from groq import Groq

DB_SCHEMA = """
Database: movies.db (SQLite)

Tables:
movies  (movie_id INTEGER PK, title TEXT, release_year INTEGER, genre TEXT, duration INTEGER)
users   (user_id INTEGER PK, name TEXT, location TEXT)
ratings (rating_id INTEGER PK, movie_id INTEGER FK→movies, user_id INTEGER FK→users,
         rating REAL 1-5, timestamp TEXT)
"""

SYSTEM_PROMPT = f"""You are an expert SQLite query generator for a movies database.

{DB_SCHEMA}

Rules:
1. Return ONLY the SQL query — no explanations, no markdown, no backticks
2. Always use table aliases: m for movies, r for ratings, u for users
3. Never use DROP, DELETE, UPDATE, INSERT, ALTER, CREATE
4. Use ROUND(AVG(r.rating), 2) for average ratings
5. Always use ORDER BY ... DESC LIMIT N for top N queries
6. If question cannot be answered from schema, output exactly: CANNOT_ANSWER
"""

def natural_language_to_sql(question: str, history: list = None) -> str: #Gets a question as string, "history: list = None" means the history parameter is optional (defaults to None if not provided), expects a list when given, and the function returns a string (-> str).
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=512,
        temperature=0, #Set to 0 = deterministic, always the same output for same input. 
    )

    sql = response.choices[0].message.content.strip()
    if sql.startswith("```"):
       sql = sql.split("\n", 1)[1]  # Remove first line having '''

    if sql.endswith("```"):
       sql = sql.rsplit("\n", 1)[0]  # Remove last line having '''
    return sql.strip()