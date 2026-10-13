"""
Unit and Integration Tests for AI-Powered Medical Symptom Assistant
Experiment 6 / 24CS2506
"""
import os
import unittest
import json

from modules.input_module import InputModule
from modules.profile_module import ProfileModule
from modules.symptom_module import SymptomModule
from modules.context_module import ContextModule
from modules.safety_module import SafetyModule
from modules.question_module import QuestionModule
from modules.analysis_module import AnalysisModule
from modules.save_module import SaveModule
from app import app


class TestMedicalAssistantModules(unittest.TestCase):

    def test_input_module_valid(self):
        payload = {
            "symptoms": "I have a sore throat, mild fever and cough.",
            "age": "22",
            "sex": "Male",
            "duration": "2 days",
            "severity": "Mild",
            "previous_conditions": "None",
            "medications": "None",
            "allergies": "None",
            "additional_info": "Body temp 99.8 F"
        }
        is_valid, data, err = InputModule.collect_and_validate(payload)
        self.assertTrue(is_valid)
        self.assertIsNone(err)
        self.assertEqual(data["sex"], "Male")
        self.assertEqual(data["severity"], "Mild")

    def test_input_module_missing_symptoms(self):
        payload = {"symptoms": "", "age": "22"}
        is_valid, data, err = InputModule.collect_and_validate(payload)
        self.assertFalse(is_valid)
        self.assertIn("symptoms", err.lower())

    def test_profile_module_valid_and_demographics(self):
        is_valid, profile, err = ProfileModule.validate_and_create_profile("22", "Male")
        self.assertTrue(is_valid)
        self.assertEqual(profile["age"], 22)
        self.assertEqual(profile["demographic_group"], "Adult")

        # Pediatric test
        is_valid, ped_profile, _ = ProfileModule.validate_and_create_profile("8", "Female")
        self.assertEqual(ped_profile["demographic_group"], "Pediatric")

        # Geriatric test
        is_valid, ger_profile, _ = ProfileModule.validate_and_create_profile("72", "Male")
        self.assertEqual(ger_profile["demographic_group"], "Geriatric")

    def test_profile_module_invalid_age(self):
        is_valid, _, err = ProfileModule.validate_and_create_profile("invalid_age", "Male")
        self.assertFalse(is_valid)
        self.assertIn("numeric", err.lower())

        is_valid, _, err = ProfileModule.validate_and_create_profile("-5", "Male")
        self.assertFalse(is_valid)
        self.assertIn("realistic", err.lower())

    def test_symptom_module_extraction(self):
        text = "I've had a fever and cough since yesterday. I also feel tired and have a mild headache, and have a sore throat when swallowing."
        extracted = SymptomModule.extract_symptoms(text)
        self.assertIsInstance(extracted, list)
        self.assertIn("Fever", extracted)
        self.assertIn("Cough", extracted)
        self.assertIn("Sore throat", extracted)
        self.assertIn("Fatigue / tiredness", extracted)

    def test_context_module(self):
        payload = {
            "duration": "2 days",
            "severity": "Mild",
            "previous_conditions": "Asthma",
            "medications": "Albuterol inhaler",
            "allergies": "None",
            "additional_info": "None"
        }
        context = ContextModule.analyze_context(payload)
        self.assertEqual(context["acuity"], "Acute")
        self.assertIn("Respiratory Comorbidity (Asthma/COPD)", context["high_risk_comorbidities"])

    def test_safety_module_normal_case(self):
        symptoms = ["Sore throat", "Fever", "Cough"]
        red_flags = SafetyModule.scan_red_flags("mild cough and fever", symptoms)
        self.assertEqual(len(red_flags), 0)

        triage, guidance, color = SafetyModule.evaluate_triage(
            red_flags, "Mild", symptoms, "Acute", 22
        )
        self.assertIn(triage, ["LOW", "MODERATE"])
        self.assertEqual(SafetyModule.DISCLAIMER_TEXT, "This is an informational AI analysis and not a medical diagnosis.")

    def test_safety_module_emergency_case(self):
        raw_text = "Crushing chest pain radiating to left arm and severe shortness of breath"
        symptoms = ["Chest pain", "Shortness of breath (Dyspnea)"]
        red_flags = SafetyModule.scan_red_flags(raw_text, symptoms)
        self.assertGreater(len(red_flags), 0)

        triage, guidance, color = SafetyModule.evaluate_triage(
            red_flags, "Severe", symptoms, "Acute", 54
        )
        self.assertEqual(triage, "EMERGENCY")
        self.assertIn("emergency", guidance.lower())
        self.assertEqual(color, "red")

    def test_question_module(self):
        symptoms = ["Fever", "Cough", "Sore throat"]
        context = {"additional_info": "", "medications": "None"}
        profile = {"age": 22}
        questions = QuestionModule.generate_follow_up_questions(symptoms, context, profile)
        self.assertIsInstance(questions, list)
        self.assertGreater(len(questions), 0)

    def test_save_module(self):
        profile = {"age": 22, "sex": "Male", "demographic_group": "Adult"}
        context = {"duration": "2 days", "severity": "Mild", "previous_conditions": "None", "medications": "None", "allergies": "None", "additional_info": "None"}
        analysis = {
            "reported_symptoms": ["Fever", "Cough", "Sore throat"],
            "duration": "2 days",
            "severity": "Mild",
            "possible_conditions": [{"name": "Common cold", "explanation": "Upper respiratory viral infection."}],
            "why_considered": "Symptoms match respiratory infection.",
            "additional_information_needed": ["Temperature"],
            "follow_up_questions": ["Is the cough dry?"],
            "triage_level": "MODERATE",
            "medical_attention": "Routine evaluation if persists.",
            "red_flags": [],
            "disclaimer": SafetyModule.DISCLAIMER_TEXT
        }

        success, report_id, json_path, txt_path = SaveModule.save_report(
            analysis, profile, context, "I have fever and cough", "Test Engine"
        )
        self.assertTrue(success)
        self.assertTrue(os.path.exists(json_path))
        self.assertTrue(os.path.exists(txt_path))

        # Check JSON integrity
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["analysis"]["triage_level"], "MODERATE")

    def test_flask_api_routes(self):
        client = app.test_client()

        # Test GET /
        resp = client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"AI-Powered Medical Symptom Assistant", resp.data)

        # Test GET /api/status
        status_resp = client.get("/api/status")
        self.assertEqual(status_resp.status_code, 200)
        status_data = status_resp.get_json()
        self.assertTrue(status_data["success"])

        # Test POST /analyze with respiratory example
        payload = {
            "symptoms": "I have a sore throat, mild fever and cough.",
            "age": "22",
            "sex": "Male",
            "duration": "2 days",
            "severity": "Mild",
            "previous_conditions": "None",
            "medications": "None",
            "allergies": "None",
            "additional_info": "None"
        }
        analyze_resp = client.post("/analyze", json=payload)
        self.assertEqual(analyze_resp.status_code, 200)
        res_json = analyze_resp.get_json()
        self.assertTrue(res_json["success"])
        self.assertIn("analysis", res_json)
        self.assertIn("possible_conditions", res_json["analysis"])
        self.assertEqual(res_json["analysis"]["duration"], "2 days")
        self.assertIn("Common cold", [c["name"] for c in res_json["analysis"]["possible_conditions"]])

        # Test POST /analyze with emergency red flag
        emerg_payload = {
            "symptoms": "Severe crushing chest pain radiating to left arm and jaw with severe shortness of breath",
            "age": "58",
            "sex": "Male",
            "duration": "30 minutes",
            "severity": "Severe",
            "previous_conditions": "Hypertension",
            "medications": "None",
            "allergies": "None",
            "additional_info": "None"
        }
        emerg_resp = client.post("/analyze", json=emerg_payload)
        self.assertEqual(emerg_resp.status_code, 200)
        emerg_json = emerg_resp.get_json()
        self.assertTrue(emerg_json["success"])
        self.assertEqual(emerg_json["analysis"]["triage_level"], "EMERGENCY")


if __name__ == "__main__":
    unittest.main()
