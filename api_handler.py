from flask import Flask, request, jsonify
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.llm_to_sql import nl_to_sql
from modules.sql_executor import execute_sql
from modules.output_formatter import format_output

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def query():
    try:
        data = request.json
        message = data.get('message', '')
        
        sql_query = nl_to_sql(message)
        result = execute_sql(sql_query)
        answer = format_output(result, message)
        
        return jsonify({
            "success": True,
            "question": message,
            "sql_query": sql_query,
            "answer": answer
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print('Starting Flask server on http://127.0.0.1:5000')
    app.run(host='127.0.0.1', port=5000, debug=False)