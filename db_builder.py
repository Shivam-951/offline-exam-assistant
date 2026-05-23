import pdfplumber
import sqlite3
import json
import re 
import os 

# Database setup 
def create_database():
    conn = sqlite3.connect("questions.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL, 
            option_a TEXT, 
            option_b TEXT, 
            option_c TEXT, 
            option_d TEXT, 
            correct_answer TEXT, 
            explanation TEXT, 
            subject TEXT, 
            source TEXT
        )
    ''')
    conn.commit()
    return conn 

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text 

def parse_mcqs(text, source):
    questions = []
    
    # Split by question numbers 
    # Matches patterns like "1." "2." "31." etc
    pattern = r'\n\s*(\d{1,3})\.\s+'
    parts = re.split(pattern, text)
    
    i = 1 
    while i < len(parts) - 1:
        try:
            q_content = parts[i+1].strip()
            
            # Skip if too short 
            if len(q_content) < 20:
                i += 2 
                continue 
            
            # Get question stem 
            question_stem = re.split(r'\n\s*[(\[]?[1-4ABCDabcd][).\]]\s+', q_content)[0].strip()
            
            if len(question_stem) < 15:
                i += 2 
                continue 
        
            # Extract answer 
            ans_match = re.search(r'(?:Ans(?:wer)?[:\s]+|Answer\s*\()([1-4ABCDabcd])', q_content, re.IGNORECASE)
            correct = ans_match.group(1).upper() if ans_match else "A"
            
            # Extract explanation 
            sol_match = re.search(r'Sol[:\s]+(.+?)(?=\n\s*\d{1,3}\.|$)', q_content, re.DOTALL)
            explanation = sol_match.group(1).strip()[:500] if sol_match else""
            
            # Map options 
            opt_a = opt_b = opt_c = opt_d = ""
            opt_matches = re.findall(r'\n\s*[(\[]?([1ABCDabcd])[).\]]\s+(.+?)(?=\n\s*[(\[]?[1-4ABCDabcd][).\]]|\nAns|\nSol|$)', q_content, re.DOTALL)
            for label, text_val in opt_matches:
                label = label.upper()
                text_val = text_val.strip()[:200]
                if label in ['A', '1']:
                    opt_a = text_val
                elif label in ['B', '2']:
                    opt_b = text_val
                elif label in ['C', '3']:
                    opt_c = text_val
                elif label in ['D', '4']:
                    opt_d = text_val
                
            # Detect subject 
            subject = detect_subject(question_stem, source)
            
            questions.append({
                "question": question_stem[:500], 
                "option_a": opt_a,
                "option_b": opt_b,
                "option_c": opt_c,
                "option_d": opt_d,
                "correct_answer": correct, 
                "explanation": explanation,
                "subject": subject, 
                "source": source, 
            })
        
        except Exception as e:
            pass

        i += 2 
    
    return questions

def detect_subject(text, source):
    text_lower = text.lower()
    
    physics_words = [
        'force', 'velocity', 'acceleration', 'energy', 'wave', 'current',
        'magnetic', 'electric', 'circuit', 'lens', 'optics', 'nuclear',
        'quantum', 'momentum', 'gravity', 'friction', 'pressure', 'heat',
        'thermodynamic', 'capacitor', 'resistor', 'inductor', 'photon',
        'electron', 'proton', 'neutron', 'radiation', 'frequency', 'amplitude',
        'wavelength', 'refraction', 'reflection', 'diffraction', 'voltage',
        'resistance', 'power', 'work', 'torque', 'angular', 'oscillat',
        'pendulum', 'spring', 'collision', 'projectile', 'satellite', 'orbit',
        'doppler', 'interference', 'polariz', 'photoelectric', 'de broglie',
        'bohr', 'half life', 'radioactive', 'fission', 'fusion', 'transistor',
        'diode', 'semiconductor', 'logic gate', 'electromagnetic', 'flux',
        'solenoid', 'transformer', 'alternating', 'rectifier', 'modulation'
    ]
    
    chemistry_words = [
        'reaction', 'compound', 'element', 'molecule', 'acid', 'base',
        'oxidation', 'bond', 'organic', 'carbon', 'hydrogen', 'orbital',
        'valence', 'ionic', 'covalent', 'mole', 'molarity', 'solution',
        'solubility', 'equilibrium', 'catalyst', 'enthalpy', 'entropy',
        'gibbs', 'activation', 'rate constant', 'order of reaction',
        'titration', 'buffer', 'ph', 'hydrolysis', 'esterification',
        'aldehyde', 'ketone', 'alcohol', 'amine', 'benzene', 'alkane',
        'alkene', 'alkyne', 'polymer', 'monomer', 'isomer', 'chirality',
        'electrophile', 'nucleophile', 'substitution', 'elimination',
        'addition', 'oxidation state', 'coordination', 'ligand', 'complex',
        'crystal', 'lattice', 'unit cell', 'colloid', 'electrode',
        'electrolysis', 'galvanic', 'cell potential', 'faraday',
        'hybridization', 'vsepr', 'periodic', 'ionization', 'electron affinity',
        'electronegativity', 'atomic radius', 'noble gas', 'transition metal',
        'lanthanide', 'actinide', 'alloy', 'cement', 'glass', 'drug'
    ]
    
    biology_words = [
        'cell', 'dna', 'rna', 'protein', 'enzyme', 'photosynthesis',
        'mitosis', 'meiosis', 'chromosome', 'gene', 'evolution', 'ecology',
        'hormone', 'neuron', 'tissue', 'organ', 'organism', 'bacteria',
        'virus', 'fungi', 'algae', 'plant', 'animal', 'mammal', 'flower',
        'seed', 'fruit', 'root', 'stem', 'leaf', 'chlorophyll', 'mitochondria',
        'ribosome', 'nucleus', 'membrane', 'osmosis', 'diffusion', 'transport',
        'respiration', 'digestion', 'excretion', 'reproduction', 'heredity',
        'mutation', 'allele', 'genotype', 'phenotype', 'dominant', 'recessive',
        'monohybrid', 'dihybrid', 'linkage', 'crossing over', 'pedigree',
        'blood', 'heart', 'lung', 'kidney', 'liver', 'brain', 'spinal',
        'immune', 'antibody', 'antigen', 'vaccine', 'lymph', 'plasma',
        'haemoglobin', 'insulin', 'thyroid', 'pituitary', 'adrenal',
        'ecosystem', 'food chain', 'food web', 'biomass', 'productivity',
        'succession', 'biodiversity', 'conservation', 'pollution', 'biome',
        'taxonomy', 'classification', 'kingdom', 'phylum', 'class', 'order',
        'family', 'genus', 'species', 'binomial', 'neet', 'rubisco', 'atp',
        'nadh', 'krebs', 'calvin', 'mendelian', 'darwin', 'lamarck'
    ]
    
    mathematics_words = [
        'matrix', 'vector', 'integral', 'derivative', 'function', 'limit',
        'probability', 'determinant', 'circle', 'parabola', 'ellipse',
        'hyperbola', 'triangle', 'polygon', 'arithmetic', 'geometric',
        'harmonic', 'progression', 'series', 'sequence', 'binomial',
        'permutation', 'combination', 'complex number', 'real number',
        'polynomial', 'quadratic', 'linear equation', 'differential',
        'coordinate', 'slope', 'tangent', 'normal', 'area', 'volume',
        'surface area', 'trigonometry', 'sine', 'cosine', 'tangent',
        'logarithm', 'exponential', 'set theory', 'relation', 'domain',
        'range', 'inverse', 'continuity', 'differentiability', 'maxima',
        'minima', 'rolle', 'lagrange', 'statistics', 'mean', 'median',
        'mode', 'variance', 'standard deviation', 'bayes', 'conditional',
        'orthocenter', 'centroid', 'circumcenter', 'incenter', 'locus'
    ]
    
    # Count matches for each subject
    physics_score = sum(1 for w in physics_words if w in text_lower)
    chemistry_score = sum(1 for w in chemistry_words if w in text_lower)
    biology_score = sum(1 for w in biology_words if w in text_lower)
    mathematics_score = sum(1 for w in mathematics_words if w in text_lower)
    
    # Use source as hint
    if 'NEET' in source:
        biology_score += 0.5
        chemistry_score += 0.5
        physics_score += 0.5
    
    scores = {
        'Physics': physics_score,
        'Chemistry': chemistry_score,
        'Biology': biology_score,
        'Mathematics': mathematics_score
    }
    
    best_subject = max(scores, key=scores.get)
    best_score = scores[best_subject]
    
    # Only assign if score is meaningful
    if best_score > 0:
        return best_subject
    return "General"

def save_to_database(conn, questions):
    cursor = conn.cursor()
    saved = 0
    for q in questions:
        try:
            cursor.execute('''
                INSERT INTO questions 
                (question, option_a, option_b, option_c, option_d, correct_answer, explanation, subject, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',(
                    q["question"], q["option_a"], q["option_b"],
                    q["option_c"], q["option_d"], q["correct_answer"],
                    q["explanation"], q["subject"], q["source"]
            ))
            saved += 1
        except Exception as e:
            print(f"Error saving question: {e}")
            print(f"Question data: {q['question'][:50]}")
    conn.commit()
    return saved 

def main():
    print("Creating database...")
    conn = create_database()
    
    # Add your PDF paths here
    # You can add as many papers as you want
    pdfs = [
        {
            "path": os.path.join(os.path.dirname(__file__), "papers", "NEET_2025.pdf"),
            "source": "NEET_2025"
        }, 
        {
            "path": os.path.join(os.path.dirname(__file__), "papers", "JEE_MAIN_2023.pdf"),
            "source": "JEE_MAIN_2023"
        }
    ]
    
    total_saved = 0
    
    for pdf_info in pdfs:
        print(f"\nProcessing {pdf_info['source']}...")
        
        if not os.path.exists(pdf_info["path"]):
            print(f"File not found: {pdf_info['path']}")
            continue 
        
        print("Extracting text...")
        text = extract_text_from_pdf(pdf_info["path"])
        print(f"Extracted {len(text)} characters")
        
        print("Parasig questions...")
        questions = parse_mcqs(text, pdf_info["source"])
        print(f"Found {len(questions)} questions")
        
        saved = save_to_database(conn, questions)
        print(f"saved {saved} questions to database")
        total_saved += saved 
        
    # Show summary 
    cursor = conn.cursor()
    cursor.execute("SELECT subject, count(*) FROM questions GROUP BY subject")
    results = cursor.fetchall()
        
    print(f"\n{'='*40}")
    print(f"Total questions saved: {total_saved}")
    print(f"Breakdown by subject:")
    for subject, count in results:
        print(f" {subject}: {count}")
            
    conn.close()
    print("\nDatabase built successfully!")
    print("File saved as: questions.db")
        
if __name__ == "__main__":
    main()