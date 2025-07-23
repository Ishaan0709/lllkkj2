import os
import sqlite3
import logging
from datetime import datetime
from openai import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
import rag_utils  # Your custom RAG module

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MedMentor")

# ===== Configuration =====


# Initialize OpenAI
client = OpenAI()
llm = ChatOpenAI(model_name="gpt-4-turbo", temperature=0.3)

# User session management
user_sessions = {}

def get_user_data(user_id: str):
    """Fetch user data from database"""
    conn = sqlite3.connect('medmentor.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user_data = c.fetchone()
    conn.close()
    
    if user_data:
        return {
            "user_id": user_data[0],
            "name": user_data[1],
            "college": user_data[2],
            "specialization": user_data[3],
            "simulations_completed": user_data[4],
            "total_simulations": user_data[5],
            "best_performance": user_data[6],
            "surgeries_this_week": user_data[7],
            "avg_score": user_data[8],
            "feedback": user_data[9],
            "weak_areas": user_data[10].split(',')
        }
    return None

def save_chat(user_id: str, message: str, reply: str):
    """Save conversation to database"""
    conn = sqlite3.connect('medmentor.db')
    c = conn.cursor()
    c.execute('''INSERT INTO chat_history (user_id, message, reply) 
               VALUES (?, ?, ?)''', (user_id, message, reply))
    conn.commit()
    conn.close()

def is_performance_query(message: str):
    """Detect performance-related questions"""
    keywords = [
        "performance", "progress", "stats", "score", 
        "simulation", "surgery", "feedback", "weak",
        "how many", "completion", "done", "attempted",
        "my results", "how am i doing"
    ]
    return any(kw in message.lower() for kw in keywords)

def generate_medical_response(user_data, message, memory):
    """Generate medical expert response"""
    context = rag_utils.retrieve_context(message) if hasattr(rag_utils, 'retrieve_context') else ""
    
    prompt = f"""
    You are Dr. {user_data['name']}'s surgical mentor at {user_data['college']} with 30 years experience.
    Student specializes in {user_data['specialization']}. Respond as a medical professor guiding a resident.
    
    Medical Context:
    {context}
    
    Conversation History:
    {memory.buffer}
    
    Current Question: {message}
    
    Guidelines:
    1. Be authoritative but supportive
    2. Relate answers to surgical practice
    3. Suggest practical exercises when relevant
    4. Use medical terminology appropriately
    5. Reference real-world surgical cases
    """
    
    chain = ConversationChain(llm=llm, memory=memory)
    return chain.run(prompt)

def generate_reply(user_id: str, message: str) -> str:
    try:
        user_id = user_id.lower()
        message = message.strip()
        
        # Initialize user session
        if user_id not in user_sessions:
            user_sessions[user_id] = {
                "memory": ConversationBufferMemory(return_messages=True),
                "last_interaction": datetime.now()
            }
        
        session = user_sessions[user_id]
        memory = session["memory"]
        memory.save_context({"input": message}, {"output": ""})
        
        # Get user profile
        user_data = get_user_data(user_id)
        if not user_data:
            return "⚠️ User profile not found. Please contact support."
        
        # Handle performance queries
        if is_performance_query(message):
            # Prevent access to other users' data
            if ("jyotika" in message.lower() and user_id != "jyotika") or \
               ("ishaan" in message.lower() and user_id != "ishaan"):
                return "🔒 You're not authorized to view other students' data"
            
            # Generate performance report
            reply = (
                f"📊 **Performance Report for {user_data['name']}**\n"
                f"🏥 {user_data['college']} | {user_data['specialization']}\n\n"
                f"⭐ Best Performance: {user_data['best_performance']}\n"
                f"📅 Simulations This Week: {user_data['surgeries_this_week']}\n"
                f"✅ Completed: {user_data['simulations_completed']}/{user_data['total_simulations']}\n"
                f"📈 Average Score: {user_data['avg_score']}/5\n"
                f"🧠 Areas Needing Improvement: {', '.join(user_data['weak_areas'])}\n"
                f"💡 Feedback: {user_data['feedback']}\n\n"
                f"Want personalized training suggestions?"
            )
            save_chat(user_id, message, reply)
            return reply
        
        # Handle greetings
        if any(kw in message.lower() for kw in ["hi", "hello", "hey", "namaste"]):
            if user_data['weak_areas']:
                reply = (f"👋 Welcome back {user_data['name']}! Ready to work on " 
                        f"**{user_data['weak_areas'][0]}** today?")
            else:
                reply = (f"👋 Hello Dr. {user_data['name']}! How can I assist with "
                        f"your {user_data['specialization']} training today?")
            save_chat(user_id, message, reply)
            return reply
        
        # Handle training requests
        if any(kw in message.lower() for kw in ["train", "practice", "improve", "weakness"]):
            if user_data['weak_areas']:
                area = user_data['weak_areas'][0]
                reply = (
                    f"🧠 **Focused Training Plan for {area}**\n\n"
                    "1. Review 3D anatomy module (15 min)\n"
                    "2. Practice in VR simulator (Module 7)\n"
                    "3. Watch expert video demonstration\n"
                    "4. Attempt guided simulation with real-time feedback\n\n"
                    "Start now? [Yes/No]"
                )
                save_chat(user_id, message, reply)
                return reply
        
        # Medical knowledge response
        reply = generate_medical_response(user_data, message, memory)
        save_chat(user_id, message, reply)
        return reply
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return "⚠️ Our medical team is currently busy. Please try again later."