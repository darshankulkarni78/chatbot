import sqlite3
from flask import Flask, request, jsonify, session
from dotenv import load_dotenv
import os
import requests
from typing import List, Dict, Any
import pandas as pd
from flask_cors import CORS
from flask_session import Session
from collections import defaultdict

load_dotenv()

import pandas as pd
import numpy as np

session_history = defaultdict(list)

def reload_database():
    df = pd.read_csv("complex_business_data.csv")

    df.columns = [
        f"col_{i}" if not str(col).strip() or str(col).startswith("?")
        else str(col).strip().replace(" ", "_")
        for i, col in enumerate(df.columns)
    ]

    conn = sqlite3.connect("business_data.db")
    df.to_sql("raw_data", conn, if_exists="replace", index=False)
    conn.close()

def preprocess_csv(file_path: str, date_threshold: float = 0.5, num_threshold: float = 0.5):
    df = pd.read_csv(file_path)
    
    df.columns = df.columns.str.strip().str.replace('\n','').str.replace('\r','')
    for col in df.select_dtypes(include='object'):
        df[col] = df[col].str.strip()

    df.dropna(axis=1, how='all', inplace=True)
    df.dropna(axis=0, how='all', inplace=True)

    for col in df.columns:
        series = df[col]

        coerced_num = pd.to_numeric(series, errors='coerce')
        num_frac = coerced_num.notna().mean()

        coerced_date = pd.to_datetime(series, errors='coerce')
        date_frac = coerced_date.notna().mean()

        if series.dtype.kind in 'biufc':  
            continue
        elif date_frac >= date_threshold:
            df[col] = coerced_date
        elif num_frac >= num_threshold:
            df[col] = coerced_num


    for col in df.select_dtypes(include=['number','datetime']):
        df[col].ffill(inplace=True)
        df[col].bfill(inplace=True)

    return df

def summarize_dataframe(df: pd.DataFrame) -> str:
    summary = []
    summary.append(f"The dataset has {df.shape[0]} rows and {df.shape[1]} columns.")
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        unique_vals = df[col].nunique()
        example_vals = df[col].dropna().unique()[:3]

        summary.append(f"Column '{col}' is of type '{dtype}' with ~{unique_vals} unique values, e.g., {list(example_vals)}.")

    return "\n".join(summary)



df = preprocess_csv("complex_business_data.csv")
data_summary = summarize_dataframe(df)

db_path = "business_data.db"
conn = sqlite3.connect(db_path)
df.to_sql("raw_data", conn, if_exists="replace", index=False)
conn.close()

app = Flask(__name__)
CORS(app)

app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")  
Session(app)

class Llama33Agent:
    def __init__(self, api_key: str = "", model: str = "meta-llama/llama-3.3-8b-instruct:free"):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        if not self.api_key:
            raise ValueError("API key is required. Set OPENROUTER_API_KEY in your .env file or pass it explicitly.")

    def _build_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def ask(self, messages: List[Dict[str, str]]) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1024,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
        }

        try:
            response = requests.post(self.api_url, headers=self._build_headers(), json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            print(" OpenRouter API response:", data)  # ← ADD THIS LINE
            return data['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            print(" Request Error:", e)
            return f"Error communicating with OpenRouter API: {e}"
        except (KeyError, IndexError) as e:
            print(" Parsing Error:", e)
            return "Unexpected API response structure."

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    if not data or "question" not in data:
        return jsonify({"error": "No question provided"}), 400

    user_question = data["question"]
    session_id = data.get("session_id", "default")

    agent = Llama33Agent()

    if not session_history[session_id]:
        try:
            conn = sqlite3.connect("business_data.db")
            preview_df = pd.read_sql("SELECT * FROM raw_data LIMIT 10", conn)
            schema_preview = preview_df.to_string()
            conn.close()
        except Exception as e:
            schema_preview = f"(Error fetching from DB: {e})"

        session_history[session_id].append({
            "role": "system",
            "content": (
                "You are an intelligent data assistant. "
                "Here is a preview of the data from SQL:\n"
                f"{schema_preview}\n"
                "Answer questions by giving final answers or summaries. "
                "Do NOT provide raw SQL code or query snippets in your answer."
            )
        })

    session_history[session_id].append({"role": "user", "content": user_question})
    response = agent.ask(session_history[session_id])
    session_history[session_id].append({"role": "assistant", "content": response})

    table_df = None
    table_error = None
    if user_question.strip().lower().startswith("select"):
        try:
            conn = sqlite3.connect("business_data.db")
            table_df = pd.read_sql_query(user_question, conn)
            conn.close()
            if table_df.empty:
                table_error = "Query returned no rows."
                table_df = None
        except Exception as e:
            table_error = f"SQL error: {str(e)}"
            table_df = None

    return jsonify({
        "response": response,
        "table": table_df.to_dict(orient="records") if table_df is not None else None,
        "table_error": table_error
    })

@app.route('/reload-data', methods=['POST'])
def reload_data():
    try:
        reload_database()
        session.pop("conversation", None)
        return jsonify({"status": "success", "message": "Database updated from CSV and session cleared."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/reset-session', methods=['POST'])
def reset_session():
    session.pop("conversation", None)
    return jsonify({"status": "success", "message": "Session reset and memory cleared."})

if __name__ == "__main__":
    app.run(port=8000)