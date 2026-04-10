from fastapi import FastAPI
from backend.db.connection import get_connection

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API running successfully!"}

@app.get("/test-db")
def test_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1;")
        result = cursor.fetchone()

        conn.close()

        return {
            "db": "connected",
            "result": result
        }

    except Exception as e:
        return {"error": str(e)}