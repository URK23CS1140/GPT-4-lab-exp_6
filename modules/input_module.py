"""
Input Module
Responsible for collecting, sanitizing, and validating raw input data
from the user interface or API request.
"""
from typing import Dict, Any, Tuple, Optional


class InputModule:
    @staticmethod
    def sanitize_string(val: Any, default: str = "") -> str:
        if val is None:
            return default
        cleaned = str(val).strip()
        return cleaned if cleaned else default

    @classmethod
    def collect_and_validate(cls, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validates incoming dictionary and extracts standardized fields.
        Returns: (is_valid, standardized_data, error_message)
        """
        if not isinstance(data, dict):
            return False, None, "Invalid request payload format. Expected JSON object."

        # Chief natural language symptom description
        raw_symptoms = cls.sanitize_string(
            data.get("symptoms") or data.get("natural_language_symptoms") or data.get("symptom_description")
        )
        if not raw_symptoms:
            return False, None, "Please provide a description of your symptoms."

        # Age
        raw_age = data.get("age")
        if raw_age is None or str(raw_age).strip() == "":
            return False, None, "Age is required."

        # Sex
        sex = cls.sanitize_string(data.get("sex"), "Other").capitalize()
        if sex not in ["Male", "Female", "Other"]:
            sex = "Other"

        # Duration
        duration = cls.sanitize_string(data.get("duration"), "Not specified")

        # Severity
        severity = cls.sanitize_string(data.get("severity"), "Moderate").capitalize()
        if severity not in ["Mild", "Moderate", "Severe"]:
            severity = "Moderate"

        # Medical History / Comorbidities
        previous_conditions = cls.sanitize_string(
            data.get("previous_conditions") or data.get("medical_history") or data.get("comorbidities"), 
            "None"
        )

        # Medications
        medications = cls.sanitize_string(
            data.get("medications") or data.get("current_medications"), 
            "None"
        )

        # Allergies
        allergies = cls.sanitize_string(
            data.get("allergies") or data.get("known_allergies"), 
            "None"
        )

        # Additional information
        additional_info = cls.sanitize_string(
            data.get("additional_info") or data.get("additional_information"), 
            "None"
        )

        collected = {
            "symptoms_raw": raw_symptoms,
            "age_raw": raw_age,
            "sex": sex,
            "duration": duration,
            "severity": severity,
            "previous_conditions": previous_conditions,
            "medications": medications,
            "allergies": allergies,
            "additional_info": additional_info
        }

        return True, collected, None
