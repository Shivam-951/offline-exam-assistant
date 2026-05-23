import easyocr
import cv2
import numpy as np 

# Initial reader once - English language 
reader = easyocr.Reader(['en'])

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    
    # Resize larger for better accuracy 
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    # Convert to grayscale 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Sharpen 
    kernel = np.array([[-1, -1, -1],
                       [-1, 9, -1],
                       [-1, -1, -1]
                       ])
    sharpened = cv2.filter2D(gray, -1, kernel)
    
    return sharpened

def extract_text(image_path):
        
        # Extract text using EasyOCR
        result = reader.readtext(image_path, detail=0, paragraph=False)
        
        # Join all text blocks 
        text = '\n'.join(result)
        
        return text.strip()
    
if __name__  == "__main__":
    image_path = "test_question.png"
    
    print("Initializing EasyOCR...")
    result = extract_text(image_path)
    
    print("Extracted Text: ")
    print("-"*40)
    print(result)