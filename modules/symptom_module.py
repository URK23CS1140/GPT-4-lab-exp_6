"""
Symptom Module
Parses conversational natural-language text to isolate discrete clinical
signs and chief complaints (e.g., Fever, Cough, Sore Throat, Headache).
"""
import re
from typing import List, Dict, Any


class SymptomModule:
    # Comprehensive lexicon of common medical symptoms, signs, and complaints
    COMMON_SYMPTOMS_MAP = {
        "sore throat": "Sore throat",
        "throat pain": "Sore throat",
        "throat irritation": "Sore throat",
        "throat": "Sore throat",
        "fever": "Fever",
        "high fever": "High fever",
        "mild fever": "Mild fever",
        "temperature": "Elevated temperature",
        "chills": "Chills",
        "shivering": "Chills",
        "cough": "Cough",
        "coughing": "Cough",
        "dry cough": "Dry cough",
        "wet cough": "Productive cough",
        "phlegm": "Sputum / Phlegm",
        "mucus": "Sputum / Phlegm",
        "headache": "Headache",
        "mild headache": "Mild headache",
        "severe headache": "Severe headache",
        "throbbing headache": "Throbbing headache",
        "migraine": "Migraine headache",
        "tired": "Fatigue / tiredness",
        "tiredness": "Fatigue / tiredness",
        "fatigue": "Fatigue / tiredness",
        "exhaustion": "Fatigue / tiredness",
        "body ache": "Body aches",
        "body aches": "Body aches",
        "muscle ache": "Myalgia (muscle ache)",
        "muscle aches": "Myalgia (muscle ache)",
        "joint pain": "Arthralgia (joint pain)",
        "runny nose": "Rhinorrhea (runny nose)",
        "blocked nose": "Nasal congestion",
        "stuffy nose": "Nasal congestion",
        "nasal congestion": "Nasal congestion",
        "sneezing": "Sneezing",
        "shortness of breath": "Shortness of breath (Dyspnea)",
        "difficulty breathing": "Difficulty breathing",
        "breathing difficulty": "Breathing difficulty",
        "wheezing": "Wheezing",
        "chest pain": "Chest pain",
        "pressure in chest": "Chest tightness / pressure",
        "chest tightness": "Chest tightness",
        "chest discomfort": "Chest discomfort",
        "nausea": "Nausea",
        "vomiting": "Vomiting",
        "diarrhea": "Diarrhea",
        "stomach pain": "Abdominal pain",
        "abdominal pain": "Abdominal pain",
        "stomach ache": "Abdominal discomfort",
        "dizziness": "Dizziness / Lightheadedness",
        "lightheaded": "Lightheadedness",
        "fainting": "Syncope (loss of consciousness)",
        "loss of consciousness": "Loss of consciousness",
        "numbness": "Numbness / Paresthesia",
        "weakness": "Generalized weakness",
        "facial drooping": "Facial droop / Asymmetry",
        "slurred speech": "Slurred speech",
        "confusion": "Altered mental status / Confusion",
        "vision changes": "Visual disturbance",
        "blurred vision": "Blurred vision",
        "loss of taste": "Ageusia (loss of taste)",
        "loss of smell": "Anosmia (loss of smell)",
        "rash": "Skin rash",
        "swelling": "Edema / Swelling",
        "itching": "Pruritus (itching)",
        "sweating": "Diaphoresis (profuse sweating)",
        "night sweats": "Night sweats"
    }

    @classmethod
    def extract_symptoms(cls, text: str) -> List[str]:
        """
        Extracts and normalizes discrete symptoms from natural language text.
        """
        if not text:
            return []

        lower_text = text.lower()
        extracted = []
        extracted_keys = set()

        # Sort map keys by length descending to match multi-word phrases first (e.g. 'sore throat' before 'throat')
        sorted_patterns = sorted(cls.COMMON_SYMPTOMS_MAP.keys(), key=len, reverse=True)

        for pattern in sorted_patterns:
            # Match pattern as word or phrase
            regex = r'\b' + re.escape(pattern) + r'\b'
            if re.search(regex, lower_text):
                canonical = cls.COMMON_SYMPTOMS_MAP[pattern]
                # Avoid duplicates
                if canonical not in extracted:
                    extracted.append(canonical)
                extracted_keys.add(pattern)

        # If no known symptom was caught in dictionary, attempt clause parsing
        if not extracted:
            # Split by punctuation or conjunctions
            clauses = re.split(r'[,;.!?\n]| and | as well as | with ', text, flags=re.IGNORECASE)
            for clause in clauses:
                clause = clause.strip()
                # Clean up introductory words like "I have", "I feel", "I am having"
                cleaned = re.sub(
                    r'^(i have had|i have|i feel|i am having|i am feeling|i get|patient has|feeling|suffering from)\s+',
                    '', clause, flags=re.IGNORECASE
                ).strip()
                if len(cleaned) > 2 and len(cleaned.split()) <= 6:
                    cap = cleaned.capitalize()
                    if cap not in extracted:
                        extracted.append(cap)

        # Fallback if still empty
        if not extracted and text.strip():
            extracted = [text.strip()[:60].capitalize()]

        return extracted
