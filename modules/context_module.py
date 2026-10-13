"""
Context Module
Evaluates patient clinical context including duration acuity, severity scale,
comorbidities, concurrent medications, known allergies, and contextual notes.
"""
import re
from typing import Dict, Any


class ContextModule:
    @staticmethod
    def evaluate_acuity(duration_str: str) -> str:
        """
        Determines whether the condition is Acute (< 1 week), Subacute (1-4 weeks), or Chronic (> 4 weeks).
        """
        lower = str(duration_str).lower().strip()
        
        # Check for weeks or months or years
        if any(w in lower for w in ["month", "year", "chronic"]):
            return "Chronic"
        
        match_week = re.search(r'(\d+)\s*week', lower)
        if match_week:
            num = int(match_week.group(1))
            return "Subacute" if num <= 4 else "Chronic"
            
        match_day = re.search(r'(\d+)\s*day', lower)
        if match_day:
            num = int(match_day.group(1))
            if num <= 7:
                return "Acute"
            elif num <= 28:
                return "Subacute"
            else:
                return "Chronic"

        if any(w in lower for w in ["today", "yesterday", "hour", "hours", "acute", "sudden"]):
            return "Acute"

        return "Indeterminate / Ongoing"

    @classmethod
    def analyze_context(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes and aggregates clinical context factors.
        """
        duration = data.get("duration", "Not specified")
        severity = data.get("severity", "Moderate")
        previous_conditions = data.get("previous_conditions", "None")
        medications = data.get("medications", "None")
        allergies = data.get("allergies", "None")
        additional_info = data.get("additional_info", "None")

        acuity = cls.evaluate_acuity(duration)

        # Evaluate risk multipliers based on medical history
        high_risk_comorbidities = []
        hist_lower = previous_conditions.lower()
        if any(c in hist_lower for c in ["asthma", "copd", "emphysema"]):
            high_risk_comorbidities.append("Respiratory Comorbidity (Asthma/COPD)")
        if any(c in hist_lower for c in ["heart", "cardiac", "hypertension", "coronary"]):
            high_risk_comorbidities.append("Cardiovascular Risk Factor")
        if any(c in hist_lower for c in ["diabetes", "diabetic"]):
            high_risk_comorbidities.append("Metabolic Risk Factor (Diabetes)")
        if any(c in hist_lower for c in ["immuno", "cancer", "chemo", "transplant", "hiv"]):
            high_risk_comorbidities.append("Immunocompromised State")

        return {
            "duration": duration,
            "acuity": acuity,
            "severity": severity,
            "previous_conditions": previous_conditions,
            "high_risk_comorbidities": high_risk_comorbidities,
            "medications": medications,
            "allergies": allergies,
            "additional_info": additional_info,
            "summary_sentence": (
                f"Patient presents with {acuity.lower()} symptoms lasting {duration}, "
                f"rated as {severity.lower()} severity. "
                f"Underlying conditions: {previous_conditions}. "
                f"Current medications: {medications}. "
                f"Known allergies: {allergies}."
            )
        }
