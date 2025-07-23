from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from chat_logic import generate_reply
import sqlite3

app = FastAPI(
    title="MedMentor Surgical AI",
    description="AI Mentor for Medical Students",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        reply = generate_reply(request.user_id, request.message)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/user/{user_id}")
async def get_user(user_id: str):
    conn = sqlite3.connect('medmentor.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id.lower(),))
    user = c.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(404, "User not found")
    
    return {
        "user_id": user[0],
        "name": user[1],
        "college": user[2],
        "specialization": user[3],
        "progress": f"{user[4]}/{user[5]} simulations",
        "performance": user[6],
        "weekly_activity": user[7],
        "avg_score": user[8]
    }

@app.get("/history/{user_id}")
async def get_history(user_id: str, limit: int = 10):
    conn = sqlite3.connect('medmentor.db')
    c = conn.cursor()
    c.execute("SELECT message, reply, timestamp FROM chat_history WHERE user_id=? ORDER BY timestamp DESC LIMIT ?", 
              (user_id.lower(), limit))
    history = [{"message": row[0], "reply": row[1], "time": row[2]} for row in c.fetchall()]
    conn.close()
    return history

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)