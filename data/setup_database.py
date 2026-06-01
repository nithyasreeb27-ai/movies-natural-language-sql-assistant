
import sqlite3  # tool to create and talk to SQLite database
import pandas as pd # tool to read and clean data files
import os # tool to build file paths for any computer

# ── File Paths ──────────────────────────────────────────────
HERE          = os.path.dirname(__file__)                    # current folder = data/
DB_PATH       = os.path.join(HERE, "..", "movies.db")       # movies_nl2sql/movies.db
BASICS_PATH   = os.path.join(HERE, "title.basics.tsv.gz")  # IMDb movies file
USERS_PATH    = os.path.join(HERE, "u.user")               # MovieLens users file
RATINGS_PATH  = os.path.join(HERE, "u.data")               # MovieLens ratings file

# ── Step 1: Load and Clean IMDb Movies ─────────────────────
def load_movies():
    print("Loading movies from IMDb...")

    # Read IMDb file (tab separated, compressed)
    df = pd.read_csv(BASICS_PATH, sep="\t", low_memory=False)

    # Keep only movies in titleType column (remove TV shows, shorts etc.)
    df = df[df["titleType"] == "movie"]

    # Keep only columns we need
    df = df[["tconst", "primaryTitle", "startYear", "genres", "runtimeMinutes"]]

    # Remove rows with missing values (\N means null in IMDb)
    df = df[df["startYear"]      != "\\N"]
    df = df[df["runtimeMinutes"] != "\\N"]
    df = df[df["genres"]         != "\\N"]

    # Convert year and duration from text to numbers
    df["startYear"]      = df["startYear"].astype(int)
    df["runtimeMinutes"] = df["runtimeMinutes"].astype(int)

    # Keep only movies from 2010 onwards
    df = df[df["startYear"] >= 2010]

    # Keep first genre only (IMDb gives multiple like "Action,Comedy")
    df["genres"] = df["genres"].str.split(",").str[0]
    
    # Take first 100 movies and add clean movie_id
    df = df.head(100).reset_index(drop=True) # make index created by pandas for each reset again
    df["movie_id"] = df.index + 1 # index 0 = movie id 1

    print(f"✅ Movies loaded: {len(df)}")
    return df

# ── Step 2: Load Real Users from MovieLens ─────────────────
def load_users():
    print("Loading users from MovieLens...")

    # MovieLens u.user columns
    df = pd.read_csv(
        USERS_PATH,
        sep="|",
        names=["user_id", "age", "gender", "occupation", "zip_code"]
    )

    # Keep only what we need
    df = df[["user_id", "age", "gender", "occupation"]]

    # Take first 50 users
    df = df.head(50)

    print(f"✅ Users loaded: {len(df)}") #50 users
    return df

# ── Step 3: Load Real Ratings from MovieLens ───────────────
def load_ratings(movies_df, users_df):
    print("Loading ratings from MovieLens...")

    # MovieLens u.data columns
    df = pd.read_csv(
        RATINGS_PATH,
        sep="\t",
        names=["user_id", "movie_id", "rating", "timestamp"]
    )

    # Keep only ratings from our 50 users
    df = df[df["user_id"].isin(users_df["user_id"])]

    # Keep only ratings from our 100 movies
    # MovieLens movie_ids match our movie_ids (both 1-100)
    df = df[df["movie_id"].isin(movies_df["movie_id"])]

    # Add rating_id column
    df = df.reset_index(drop=True)
    df["rating_id"] = df.index + 1

    # Reorder columns to match our schema
    df = df[["rating_id", "movie_id", "user_id", "rating", "timestamp"]]

    print(f"✅ Ratings loaded: {len(df)}")
    return df

# ── Step 4: Create Database and Insert Data ─────────────────
def create_database(movies_df, users_df, ratings_df):
    print("Creating database...")

    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # Create 3 tables (drop old ones if exist)
    cur.executescript("""
        PRAGMA foreign_keys = ON;
        DROP TABLE IF EXISTS ratings;
        DROP TABLE IF EXISTS movies;
        DROP TABLE IF EXISTS users;

        CREATE TABLE movies (
            movie_id     INTEGER PRIMARY KEY,
            title        TEXT    NOT NULL,
            release_year INTEGER NOT NULL,
            genre        TEXT    NOT NULL,
            duration     INTEGER NOT NULL
        );

        CREATE TABLE users (
            user_id    INTEGER PRIMARY KEY,
            age        INTEGER,
            gender     TEXT,
            occupation TEXT
        );

        CREATE TABLE ratings (
            rating_id  INTEGER PRIMARY KEY,
            movie_id   INTEGER NOT NULL REFERENCES movies(movie_id),
            user_id    INTEGER NOT NULL REFERENCES users(user_id),
            rating     REAL    NOT NULL CHECK(rating BETWEEN 1 AND 5),
            timestamp  INTEGER NOT NULL
        );
    """)

    # Insert movies from IMDb
    for _, row in movies_df.iterrows():
        cur.execute("INSERT INTO movies VALUES (?,?,?,?,?)", (
            int(row["movie_id"]),
            row["primaryTitle"],
            int(row["startYear"]),
            row["genres"],
            int(row["runtimeMinutes"])
        ))

    # Insert users from MovieLens
    for _, row in users_df.iterrows():
        cur.execute("INSERT INTO users VALUES (?,?,?,?)", (
            int(row["user_id"]),
            int(row["age"]),
            row["gender"],
            row["occupation"]
        ))

    # Insert ratings from MovieLens
    for _, row in ratings_df.iterrows():
        cur.execute("INSERT INTO ratings VALUES (?,?,?,?,?)", (
            int(row["rating_id"]),
            int(row["movie_id"]),
            int(row["user_id"]),
            float(row["rating"]),
            int(row["timestamp"])
        ))

    conn.commit() #Saves to disk
    conn.close()
    print(f"✅ Database created: {DB_PATH}")

# ── Main: Run All Steps ──────────────────────────────────────
if __name__ == "__main__": # runs only when we
    movies  = load_movies()
    users   = load_users()
    ratings = load_ratings(movies, users)
    create_database(movies, users, ratings)

    print("\n🎬 Database ready!")
    print(f"   Movies  : {len(movies)}")
    print(f"   Users   : {len(users)}")
    print(f"   Ratings : {len(ratings)}")