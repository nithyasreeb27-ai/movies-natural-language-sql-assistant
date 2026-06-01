from groq import Groq
import os

def format_table(columns: list, rows: list) -> str: #Convert database output into a readable table
    if not columns:
        return "(no results)"

    widths = [len(c) for c in columns] #This creates a list with the width of each column name

    # Is any value in this column longer than the column name?, If YES → increase the column width to create structure table
    for row in rows:
        for i, val in enumerate(row): # index, value will be given to a row i.e 0 sam and 1 100
            widths[i] = max(widths[i], len(str(val))) # width of 0th column, length of 0th row similary for 1st

    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+" #creates horizontal border creates~ +--------+------+
    header = "|" + "|".join(f" {c:<{widths[i]}} " for i, c in enumerate(columns)) + "|" #:<{width} → left-align text inside fixed width. and creates~ | Name     | Age |

    # Each row is formatted like header.
    lines = [sep, header, sep]
    for row in rows:
        line = "|" + "|".join(f" {str(v):<{widths[i]}} " for i, v in enumerate(row)) + "|"
        lines.append(line)
    lines.append(sep)

    return "\n".join(lines)


def generate_summary(question: str, sql: str, columns: list, rows: list) -> str: #Convert raw SQL results → human-readable explanation using LLM
    if not rows:
        return "No results were found for that query."

    result_text = ", ".join(columns) + "\n"  # It combines all items in a list into one string, separated by ", " and \n makes this the header line
    for row in rows[:10]:
        result_text += "  " + " | ".join(str(v) for v in row) + "\n" # converts row elements to string and | between them and add indentation and new line
    if len(rows) > 10:
        result_text += f"  ... and {len(rows) - 10} more rows\n"

    prompt = f"""Question: {question}

SQL used:
{sql}

Result:
{result_text}

Write a concise 2-3 sentence plain English answer based on the results.
Be specific and mention actual values. Do not repeat the SQL."""

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256,
    )

    return response.choices[0].message.content.strip()