"""
Prompt Module
Constructs clinical system and user prompts embedding safety guardrails,
scientific uncertainty, and strict JSON output schemas for GPT-4 or Ollama.
"""
import json
from typing import Dict, Any, List


class PromptModule:
    @staticmethod
    def get_system_prompt() -> str:
        return (
            "You are an AI-Powered Medical Symptom Assistant designed strictly for informational "
            "and educational preliminary triage. You are NOT a medical doctor and CANNOT diagnose conditions.\n\n"
            "MANDATORY CLINICAL GUARDRAILS:\n"
            "1. NEVER state or confirm a definitive diagnosis. Always speak of POSSIBLE conditions or differential possibilities.\n"
            "2. Communicate uncertainty explicitly using cautious clinical phrasing.\n"
            "3. If any red flags or life-threatening symptoms appear (e.g. chest pain radiating to arm, acute shortness of breath, "
            "loss of consciousness, stroke signs, anaphylaxis), immediately designate triage_level as 'EMERGENCY'.\n"
            "4. Strongly recommend professional in-person medical evaluation if symptoms worsen, are severe, or persist.\n"
            "5. OUTPUT FORMAT: You must respond ONLY with a valid JSON object matching the requested schema exactly. "
            "Do not output markdown code blocks (```json ... ```) or conversational preamble."
        )

    @staticmethod
    def get_user_prompt(
        profile: Dict[str, Any],
        extracted_symptoms: List[str],
        context: Dict[str, Any],
        raw_description: str
    ) -> str:
        schema_format = {
            "reported_symptoms": ["List of identified symptoms as strings"],
            "duration": "Duration string (e.g., 2 days)",
            "severity": "Mild | Moderate | Severe",
            "possible_conditions": [
                {
                    "name": "Condition Name",
                    "explanation": "Brief rationale why this condition is a possibility."
                }
            ],
            "why_considered": "A coherent explanatory paragraph describing why these candidate conditions were considered based on reported signs.",
            "additional_information_needed": [
                "List of specific clinical details or measurements needed (e.g., exact temperature, breathing difficulty)"
            ],
            "follow_up_questions": [
                "List of 2-4 clarifying questions to help the user reflect on symptoms"
            ],
            "triage_level": "LOW | MODERATE | HIGH | EMERGENCY",
            "medical_attention": "Specific guidance on when and where to seek professional medical evaluation.",
            "red_flags": ["List of any detected urgent red flag indicators, or empty list"],
            "disclaimer": "This is an informational AI analysis and not a medical diagnosis."
        }

        prompt_text = f"""Analyze the following patient intake case:

PATIENT DEMOGRAPHICS:
- Age: {profile.get('age')} years old ({profile.get('demographic_group', 'Adult')})
- Biological Sex: {profile.get('sex')}

CHIEF NATURAL LANGUAGE PRESENTATION:
"{raw_description}"

PRE-EXTRACTED SYMPTOMS:
{json.dumps(extracted_symptoms)}

CLINICAL CONTEXT:
- Duration: {context.get('duration')} (Acuity: {context.get('acuity')})
- Reported Severity: {context.get('severity')}
- Pre-existing Medical Conditions / Comorbidities: {context.get('previous_conditions')}
- Current Medications: {context.get('medications')}
- Known Allergies: {context.get('allergies')}
- Contextual / Additional Information: {context.get('additional_info')}

TASK:
Provide a structured clinical symptom analysis in strict JSON format.
Ensure you list 2 to 4 possible conditions with clinical reasoning.
Return ONLY valid JSON matching this schema:
{json.dumps(schema_format, indent=2)}
"""
        return prompt_text
