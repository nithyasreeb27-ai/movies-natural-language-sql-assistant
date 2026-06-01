# 🎬 Movies NL→SQL Assistant

An AI assistant that converts natural language questions into SQL queries,
executes them on a real IMDb movies database, and returns results in plain English.

---

## Project Structure
```
movies_nl2sql/
├── data/
│   ├── setup_database.py        # Creates and populates movies.db
│   ├── title.basics.tsv.gz      # IMDb movies dataset
│   └── title.ratings.tsv.gz     # IMDb ratings dataset
├── modules/
│   ├── llm_to_sql.py            # NL → SQL using Groq (Llama3)
│   ├── sql_executor.py          # Safe SQL execution layer
│   └── output_formatter.py      # Table + plain English summary
├── streamlit_app/
│   └── app.py                   # Streamlit browser UI
├── assistant.py                 # Main orchestrator + CLI demo
├── requirements.txt             # Required libraries
└── README.md                    # This file
```

---

## Setup Instructions

### 1. Install dependencies
```
pip install -r requirements.txt
```

### 2. Set your Groq API key
```
$env:GROQ_API_KEY="gsk_your-key-here"
```

### 3. Create the database
```
python data/setup_database.py
```

### 4. Run CLI demo
```
python assistant.py
```

### 5. Run Streamlit UI
```
python -m streamlit run streamlit_app/app.py
```

---

## Database Schema
```
movies  (movie_id, title, release_year, genre, duration)
users   (user_id, name, location)
ratings (rating_id, movie_id, user_id, rating, timestamp)
```

- 100 real IMDb movies (2010 onwards)
- 15 users across different US cities
- 992 ratings generated

---

## Example Queries and Responses

### 1. Top 5 Highest Rated Movies
**Input:** Show me the top 5 highest rated movies

**Generated SQL:**
```sql
SELECT m.title, ROUND(AVG(r.rating), 2) AS avg_rating
FROM movies m JOIN ratings r ON m.movie_id = r.movie_id
GROUP BY m.title ORDER BY avg_rating DESC LIMIT 5
```

**Result:**
```
+------------------+------------+
| title            | avg_rating |
+------------------+------------+
| Tangled          | 4.42       |
| The Dark Knight  | 4.38       |
| Inception        | 4.35       |
+------------------+------------+
```
**Answer:** The highest rated movie is Tangled with an average rating of 4.42 out of 5.

---

### 2. Genre with Highest Average Rating
**Input:** Which genre has the highest average rating?

**Generated SQL:**
```sql
SELECT m.genre, ROUND(AVG(r.rating), 2) AS avg_rating
FROM movies m JOIN ratings r ON m.movie_id = r.movie_id
GROUP BY m.genre ORDER BY avg_rating DESC LIMIT 1
```

**Answer:** Animation has the highest average rating among all genres.

---

### 3. Movies Released After 2015
**Input:** How many movies were released after 2015?

**Generated SQL:**
```sql
SELECT COUNT(*) AS movie_count
FROM movies m WHERE m.release_year > 2015
```

**Answer:** There are 62 movies in the database released after 2015.

---

### 4. Most Active Reviewers
**Input:** Who are the top 3 most active reviewers?

**Generated SQL:**
```sql
SELECT u.name, COUNT(r.rating_id) AS review_count
FROM users u JOIN ratings r ON u.user_id = r.user_id
GROUP BY u.user_id ORDER BY review_count DESC LIMIT 3
```

**Answer:** The top 3 most active reviewers are Bob Smith, Karen Thomas and Emma Davis.

---

## Architecture
```
User Question (English)
        ↓
llm_to_sql.py  →  Groq API (Llama3) generates SQL
        ↓
sql_executor.py  →  Validates + runs SQL on movies.db
        ↓
output_formatter.py  →  ASCII table + plain English summary
        ↓
Streamlit UI  →  Displays results in browser
```

## Security
- Only SELECT queries allowed
- DROP, DELETE, UPDATE, INSERT are all blocked
- Results capped at 200 rows
```

---

Save with **`Ctrl + S`** ✅

---

## Your Final Project Structure:
```
MOVIES_NL2SQL/
├── data/
│   ├── setup_database.py
│   ├── title.basics.tsv.gz
│   └── title.ratings.tsv.gz
├── modules/
│   ├── llm_to_sql.py
│   ├── output_formatter.py
│   └── sql_executor.py
├── streamlit_app/
│   └── app.py
├── assistant.py
├── requirements.txt
└── README.md
