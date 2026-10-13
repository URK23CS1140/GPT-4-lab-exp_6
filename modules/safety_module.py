"""
Safety Module
Scans for emergency clinical red flags, assigns validated triage categories
(EMERGENCY, HIGH, MODERATE, LOW), and enforces medical disclaimers.
"""
import re
from typing import List, Dict, Any, Tuple


class SafetyModule:
    # Emergency red flag definitions and keywords
    RED_FLAG_PATTERNS = [
        (r'chest pain|pain in chest|chest pressure|pressure in chest|squeezing chest', 
         "Chest pain or pressure (cardiac emergency risk)"),
        (r'radiat(ing|es)? to (arm|jaw|neck|back|shoulder)', 
         "Pain radiating to arm, jaw, neck, or back"),
        (r'cannot breathe|can\'t breathe|struggling to breathe|severe (shortness of breath|dyspnea)|gasping', 
         "Severe respiratory distress / acute shortness of breath"),
        (r'loss of consciousness|fainted|passed out|blacked out|unresponsive|syncope', 
         "Loss of consciousness or altered responsiveness"),
        (r'facial droop|face drooping|arm weakness|slurred speech|sudden numbness', 
         "Acute neurological symptoms / potential stroke indicators (FAST)"),
        (r'worst headache of (my )?life|thunderclap headache', 
         "Sudden severe headache (potential intracranial hemorrhage risk)"),
        (r'coughing (up )?blood|vomiting blood|severe bleeding|uncontrolled bleeding', 
         "Active acute hemoptysis or severe bleeding"),
        (r'throat swelling|tongue swell|cannot swallow|anaphylaxis|severe allergic reaction', 
         "Severe airway compromise or suspected anaphylaxis"),
        (r'suicid(e|al)|kill myself|end my life|self harm', 
         "Urgent crisis / psychiatric emergency")
    ]

    DISCLAIMER_TEXT = "This is an informational AI analysis and not a medical diagnosis."

    @classmethod
    def scan_red_flags(cls, free_text: str, symptoms: List[str], additional_info: str = "") -> List[str]:
        """
        Scans all patient text for clinical red flag indicators.
        """
        combined = f"{free_text} {' '.join(symptoms)} {additional_info}".lower()
        detected_flags = []

        for pattern, explanation in cls.RED_FLAG_PATTERNS:
            if re.search(r'\b(' + pattern + r')\b', combined):
                if explanation not in detected_flags:
                    detected_flags.append(explanation)

        return detected_flags

    @classmethod
    def evaluate_triage(
        cls, 
        red_flags: List[str], 
        severity: str, 
        symptoms: List[str], 
        duration_acuity: str,
        age: int
    ) -> Tuple[str, str, str]:
        """
        Calculates triage level and actionable clinical advisory.
        Returns: (triage_level, action_guidance, triage_badge_color)
        """
        if red_flags:
            return (
                "EMERGENCY",
                "Seek IMMEDIATE emergency medical attention. Call local emergency services (e.g., 911 / 112) or proceed to the nearest emergency department right away.",
                "red"
            )

        # High risk conditions: Severe reported intensity, high-risk age extremes, or acute chest/head complaints
        sev_upper = severity.upper()
        if sev_upper == "SEVERE":
            return (
                "HIGH",
                "Urgent medical evaluation recommended. Consult a physician or urgent care center today for prompt assessment.",
                "orange"
            )

        # Moderate risk conditions
        if sev_upper == "MODERATE" or len(symptoms) >= 3 or duration_acuity in ["Subacute", "Chronic"] or age >= 75:
            return (
                "MODERATE",
                "Routine Consultation / Monitored Self-Care. Seek professional medical evaluation if symptoms are severe, worsening, or persist beyond 3-5 days.",
                "yellow"
            )

        # Low risk / self care
        return (
            "LOW",
            "Self-Care & Observation. Rest, maintain hydration, and consult a healthcare professional if symptoms escalate or fail to improve.",
            "green"
        )
