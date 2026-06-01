import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "modules")) # Adds the modules folder to Python’s import path

from llm_to_sql import natural_language_to_sql
from sql_executor import execute_query, ForbiddenQueryError, SQLExecutionError
from output_formatter import format_table, generate_summary


class MoviesAssistant:
    def __init__(self):
        self.history = [] # Stores conversation (for LLM context)
        self.query_log = [] # Stores past queries (for tracking/debugging)

    def ask(self, question: str) -> dict:
        result = {
            "question": question,
            "sql":      "",
            "columns":  [],
            "rows":     [],
            "table":    "",
            "summary":  "",
            "error":    "",
        }

        # Step 1 - NL to SQL
        try:
            sql = natural_language_to_sql(question, history=self.history)
        except Exception as exc:
            result["error"] = f"LLM error: {exc}"
            return result

        if sql == "CANNOT_ANSWER":
            result["error"] = "I can't answer that from the movies database."
            return result

        result["sql"] = sql

        # Step 2 - Execute SQL
        try:
            columns, rows = execute_query(sql)
        except ForbiddenQueryError as exc:
            result["error"] = f"Security error: {exc}"
            return result
        except SQLExecutionError as exc:
            result["error"] = f"SQL error: {exc}"
            return result

        result["columns"] = columns
        result["rows"]    = rows

        # Step 3 - Format table
        result["table"] = format_table(columns, rows)

        # Step 4 - Generate summary
        try:
            result["summary"] = generate_summary(question, sql, columns, rows)
        except Exception:
            result["summary"] = "(summary unavailable)"

        # Step 5 - Update history
        self.history.append({"role": "user",      "content": question})
        self.history.append({"role": "assistant",  "content": sql})
        if len(self.history) > 20:
            self.history = self.history[-20:]

        self.query_log.append({
            "question":  question,
            "sql":       sql,
            "row_count": len(rows),
        })

        return result


if __name__ == "__main__":
    assistant = MoviesAssistant()

    questions = [
        "Show me the top 5 highest rated movies",
        "Which genre has the highest average rating?",
        "How many movies were released after 2015?",
        "Who are the top 3 most active reviewers?",
    ]

    for q in questions:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        res = assistant.ask(q)
        if res["error"]:
            print(f"Error: {res['error']}")
        else:
            print(f"\nSQL: {res['sql']}")
            print(f"\n{res['table']}")
            print(f"\nAnswer: {res['summary']}")