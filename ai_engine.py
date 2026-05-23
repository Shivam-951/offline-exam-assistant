import requests 
import json 

SYSTEM_PROMPT = """You are an expert JEE and NEET science tutor.
When given a multiple choice question:
1. State the correct option clearly first
2. Explain why that option id correct in simple steps
Breifly explain why the other options are wrong
Keep explanation concise and accurate.
Never guess. If unsure, say so."""


def get_answer(question_text):
    url = "http://localhost:11434/api/chat"
    
    payload = {
        "model": "llama3.2",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question_text},
        ],
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
            
        # Debug — let's see exact response structure
            
        # Handle both possible response formats
        if "message" in data:
            return data["message"]["content"]
        elif "response" in data:
            return data["response"]
        else:
            return f"Unexpected response format: {data}"
    
    except Exception as e:
        return f"Error: {str(e)}"
    
if __name__ == "__main__":
    test_question = """Which of the following statements is true about 
    5dm3 of hydrogen and 5dm3 of oxygen at 0°C and 101 kPa?
    A) They react to produce 5dm3 of water
    B) They react completely with each other
    C) They contain the same number of molecules
    D) They possess the same amount of kinetic energy"""
    
    print("Sending question to AI...")
    print("-" * 40)
    answer = get_answer(test_question)
    print(answer)