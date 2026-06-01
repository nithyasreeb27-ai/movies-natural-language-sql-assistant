import sys
import os
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "modules"))

from llm_to_sql import natural_language_to_sql
from sql_executor import execute_query, ForbiddenQueryError, SQLExecutionError
from output_formatter import generate_summary

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "movies.db")

st.set_page_config(
    page_title="Movies AI Assistant",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 Movies Natural Language Assistant")
st.caption("Ask anything about the movies database in plain English!")

# Session state
if "history" not in st.session_state:
    st.session_state.history = []
if "query_log" not in st.session_state:
    st.session_state.query_log = []
if "question" not in st.session_state:
    st.session_state.question = ""
if "run_query" not in st.session_state:
    st.session_state.run_query = False

# Sidebar 
with st.sidebar:
    st.title("💡 Example Questions")
    examples = [
        "Show me top 5 highest rated movies",
        "Which genre has the highest average rating?",
        "How many movies were released after 2015?",
        "Who are the top 3 most active reviewers?",
        "What is the average duration of Action movies?",
        "List all Drama movies with their ratings",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.question = ex
            st.session_state.run_query = True
            st.rerun()

    st.divider()
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.history.clear()
        st.session_state.query_log.clear()
        st.success("History cleared!")

#  Main input 
question = st.text_input(
    "Your Question:",
    value=st.session_state.question,
    placeholder="e.g. Which genre has the highest average rating?",
)

ask_clicked = st.button("🔍 Ask", type="primary")

# Run if Ask clicked OR example button was clicked
if ask_clicked:
    st.session_state.question = question
    st.session_state.run_query = True

if st.session_state.run_query and st.session_state.question.strip():
    st.session_state.run_query = False
    question = st.session_state.question

    # Step 1 - NL to SQL
    with st.spinner("Generating SQL..."):
        try:
            sql = natural_language_to_sql(
                question, history=st.session_state.history
            )
        except Exception as exc:
            st.error(f"LLM Error: {exc}")
            st.stop()

    if sql == "CANNOT_ANSWER":
        st.error("I can't answer that from the movies database.")
        st.stop()

    # Show SQL
    st.subheader("Generated SQL")
    st.code(sql, language="sql")

    # Step 2 - Execute
    with st.spinner("Running query..."): # adds a spinning symbol
        try:
            columns, rows = execute_query(sql, db_path=DB_PATH)
        except ForbiddenQueryError as exc:
            st.error(f"Security Error: {exc}")
            st.stop()
        except SQLExecutionError as exc:
            st.error(f"SQL Error: {exc}")
            st.stop()

    # Step 3 - Show results
    st.subheader(f"Results ({len(rows)} rows)")
    if rows:
        df = pd.DataFrame(rows, columns=columns)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No results found.")

    # Step 4 - Summary
    with st.spinner("Generating answer..."):
        try:
            summary = generate_summary(question, sql, columns, rows)
        except Exception:
            summary = None

    if summary:
        st.subheader("💬 Answer")
        st.success(summary)

    # Update history
    st.session_state.history.append({"role": "user", "content": question})
    st.session_state.history.append({"role": "assistant", "content": sql})
    if len(st.session_state.history) > 20:
        st.session_state.history = st.session_state.history[-20:]

    st.session_state.query_log.append({
        "question": question,
        "sql": sql,
        "row_count": len(rows),
    })


if st.session_state.query_log:
    st.divider() # adds a horizontal line in your app UI.
    with st.expander(f"🕑 Query History ({len(st.session_state.query_log)} queries)"):
        for i, entry in enumerate(reversed(st.session_state.query_log), 1):
            st.markdown(f"**Q{i}:** {entry['question']} `({entry['row_count']} rows)`")
            st.code(entry["sql"], language="sql")