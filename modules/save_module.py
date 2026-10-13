"""
Save Module
Persists formatted clinical analysis to disk as timestamped .txt and .json files
in the reports/ directory.
"""
import datetime
import json
import os
import uuid
from typing import Dict, Any, Tuple

from config import Config


class SaveModule:
    @staticmethod
    def generate_report_id() -> str:
        """Generates a clinical report tracking identifier like #20261012_224500_ab1234."""
        now = datetime.datetime.now()
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        rand_suffix = uuid.uuid4().hex[:6]
        return f"{timestamp_str}_{rand_suffix}"

    @classmethod
    def save_report(
        cls,
        analysis_data: Dict[str, Any],
        profile: Dict[str, Any],
        context: Dict[str, Any],
        raw_symptoms: str,
        engine_name: str
    ) -> Tuple[bool, str, str, str]:
        """
        Saves both .json and .txt representations.
        Returns: (success, report_id, json_path, txt_path)
        """
        now = datetime.datetime.now()
        report_id = cls.generate_report_id()
        time_display = now.strftime("%Y-%m-%d %H:%M:%S")
        file_prefix = f"medical_report_{now.strftime('%Y-%m-%d_%H-%M-%S')}_{report_id[-6:]}"

        reports_dir = Config.REPORTS_DIR
        os.makedirs(reports_dir, exist_ok=True)

        json_filename = f"{file_prefix}.json"
        txt_filename = f"{file_prefix}.txt"

        json_path = os.path.join(reports_dir, json_filename)
        txt_path = os.path.join(reports_dir, txt_filename)

        # Build full structured JSON payload
        full_report_payload = {
            "report_id": f"#{report_id}",
            "timestamp": time_display,
            "engine": engine_name,
            "patient_profile": profile,
            "clinical_context": context,
            "raw_input_symptoms": raw_symptoms,
            "analysis": analysis_data,
            "disclaimer": analysis_data.get("disclaimer", "This is an informational AI analysis and not a medical diagnosis.")
        }

        try:
            # 1. Write JSON file
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(full_report_payload, jf, indent=2, ensure_ascii=False)

            # 2. Write Plaintext format
            possible_conditions_str = ""
            for idx, cond in enumerate(analysis_data.get("possible_conditions", []), start=1):
                name = cond.get("name", "Condition")
                expl = cond.get("explanation", "")
                possible_conditions_str += f"{idx}. {name}\n"
                if expl:
                    possible_conditions_str += f"   {expl}\n"

            reported_symps_str = "\n".join([f"• {s}" for s in analysis_data.get("reported_symptoms", [])])
            add_needed_str = "\n".join([f"• {a}" for a in analysis_data.get("additional_information_needed", [])])
            questions_str = "\n".join([f"• {q}" for q in analysis_data.get("follow_up_questions", [])])
            red_flags_str = "\n".join([f"⚠️ {r}" for r in analysis_data.get("red_flags", [])]) if analysis_data.get("red_flags") else "None detected."

            txt_content = f"""===================================================================
MEDICAL SYMPTOM ANALYSIS REPORT
Report ID: #{report_id}
Generated: {time_display}
Inference Engine: {engine_name}
===================================================================

PATIENT INFORMATION
-------------------------------------------------------------------
Age: {profile.get('age')} years ({profile.get('demographic_group', 'Adult')})
Sex: {profile.get('sex')}
Duration: {analysis_data.get('duration')}
Reported Severity: {analysis_data.get('severity')}
Medical History: {context.get('previous_conditions')}
Medications: {context.get('medications')}
Allergies: {context.get('allergies')}
Additional Information: {context.get('additional_info')}

TRIAGE ASSESSMENT
-------------------------------------------------------------------
TRIAGE LEVEL: {analysis_data.get('triage_level')}
Red Flag Alerts:
{red_flags_str}

MEDICAL SYMPTOM ANALYSIS
-------------------------------------------------------------------
Reported Symptoms:
{reported_symps_str}

Duration:
{analysis_data.get('duration')}

Possible Conditions:
{possible_conditions_str}
Why These Were Considered:
{analysis_data.get('why_considered')}

Additional Information Needed:
{add_needed_str}

Follow-up Clarifying Questions:
{questions_str}

Medical Attention:
{analysis_data.get('medical_attention')}

-------------------------------------------------------------------
DISCLAIMER:
{analysis_data.get('disclaimer')}
===================================================================
"""
            with open(txt_path, "w", encoding="utf-8") as tf:
                tf.write(txt_content)

            return True, f"#{report_id}", json_path, txt_path
        except Exception as e:
            return False, "", "", f"Failed to save report: {str(e)}"
