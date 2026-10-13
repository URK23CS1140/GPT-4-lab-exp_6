"""
Question Module
Generates targeted follow-up clarifying questions to collect missing
diagnostic parameters based on the identified symptom clusters.
"""
from typing import List, Dict, Any


class QuestionModule:
    @classmethod
    def generate_follow_up_questions(
        cls, 
        symptoms: List[str], 
        context: Dict[str, Any], 
        profile: Dict[str, Any]
    ) -> List[str]:
        """
        Generates clinical questions to help clarify the clinical picture.
        """
        questions = []
        symp_str = " ".join(symptoms).lower()
        add_info = str(context.get("additional_info", "")).lower()

        # Respiratory cluster questions
        if any(s in symp_str for s in ["fever", "cough", "throat", "congestion", "cold"]):
            if "temperature" not in add_info and "temp" not in add_info:
                questions.append("What is your exact measured body temperature (e.g., above 38°C / 100.4°F)?")
            if "cough" in symp_str:
                questions.append("Is your cough dry, or producing sputum/mucus (if so, what color)?")
            questions.append("Are you experiencing any shortness of breath or difficulty catching your breath?")
            if "contact" not in add_info and "exposure" not in add_info:
                questions.append("Have you had recent exposure to individuals with similar respiratory infections or recent travel?")

        # Headache / Neurological cluster
        if any(s in symp_str for s in ["headache", "migraine", "dizziness"]):
            questions.append("Is the headache throbbing, constant pressure, or sharp, and is it on one side or both sides?")
            questions.append("Do you experience sensitivity to light (photophobia), sound, or nausea alongside the headache?")
            questions.append("Did the headache start suddenly or develop gradually over several hours?")

        # Abdominal / GI cluster
        if any(s in symp_str for s in ["stomach", "abdominal", "nausea", "vomiting", "diarrhea"]):
            questions.append("Where exactly is the abdominal discomfort located (upper, lower, right, left)?")
            questions.append("Are you able to keep fluids down without vomiting?")

        # General / Baseline follow-ups
        if context.get("medications") in ["None", ""] and "remedy" not in add_info:
            questions.append("Have you taken any over-the-counter medications (e.g., paracetamol, ibuprofen), and did they relieve symptoms?")

        if not questions:
            questions = [
                "Have the symptoms been steadily improving, worsening, or staying the same?",
                "Are there any specific triggers or activities that make the discomfort worse?",
                "Are there any other unusual bodily sensations or changes you have noticed?"
            ]

        # Return top 3-4 targeted questions
        return questions[:4]
