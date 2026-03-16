from fastapi import FastAPI
import numpy as np

app = FastAPI()

database = {}

@app.post("/enroll")
def enroll(user_id: str, embedding: list):
    database[user_id] = np.array(embedding)
    return {"status": "enrolled"}

@app.post("/verify")
def verify(user_id: str, embedding: list):
    if user_id not in database:
        return {"status": "not found"}

    stored = database[user_id]
    query = np.array(embedding)

    similarity = np.dot(stored, query) / (
        np.linalg.norm(stored) * np.linalg.norm(query)
    )

    return {"similarity": float(similarity)}
