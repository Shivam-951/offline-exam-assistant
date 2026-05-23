import sqlite3 
from sentence_transformers import SentenceTransformer
import numpy as np 

# Load model once 
print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded.")

def get_all_questions():
    conn = sqlite3.connect("questions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, question, correct_answer, explanation, subject, source FROM questions")
    rows = cursor.fetchall()
    conn.close()
    return rows

def find_similar_question(query_text, threshold=0.6):
    questions = get_all_questions()
    
    if not questions:
        return None 
    
    # Embed the query 
    query_embedding = model.encode(query_text, convert_to_numpy=True)
    
    best_score = 0 
    best_match = None 
    
    for row in questions:
        q_id, question, correct_answer, explanation, subject, source = row
        
        # Embed store question 
        q_embedding = model.encode(question, convert_to_numpy=True)
        
        # Cosine similarity
        score = np.dot(query_embedding, q_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(q_embedding)
        )
        
        if score > best_score:
            best_score = score
            best_match = {
                "question": question, 
                "correct_answer": correct_answer, 
                "explanation": explanation, 
                "subject": subject, 
                "source": source, 
                "similarity": float(score)
            }
            
    print(f"Best Match similarity: {best_score:.3f}")
    
    if best_score >= threshold:
        return best_match
    return None

if __name__ == "__main__":
    # Test retrieval 
    test_query = "Which of the following statements about RuBisCo is true?"
    print(f"\nSearching for: {test_query}")
    result = find_similar_question(test_query)
    
    if result:
        print(f"\nMatch found! (similarity: {result['similarity']:.3f})")
        print(f"Question: {result['question'][:100]}")
        print(f"Answer: {result['correct_answer']}")
        print(f"Source: {result['source']}")
    else:
        print("No close match found.")