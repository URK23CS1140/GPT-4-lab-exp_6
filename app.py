"""
AI-Powered Medical Symptom Assistant using GPT-4
Main Application Module (app.py)

Coordinates Flask web application startup, registers REST API endpoints,
and orchestrates the multi-stage clinical symptom analysis pipeline.
"""
import os
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
import requests

from config import Config
from modules.input_module import InputModule
from modules.profile_module import ProfileModule
from modules.symptom_module import SymptomModule
from modules.context_module import ContextModule
from modules.safety_module import SafetyModule
from modules.analysis_module import AnalysisModule
from modules.save_module import SaveModule

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("medical_assistant")

app = Flask(__name__)
app.config.from_object(Config)


def detect_provider_status():
    """Determines the current LLM connection status for the UI indicator."""
    if Config.OPENAI_API_KEY:
        return {
            "status": "connected",
            "provider": f"Connected to {Config.OPENAI_MODEL or 'gpt-4o-mini'}",
            "type": "openai",
            "color": "#10b981"  # Emerald green
        }

    # Check Ollama
    try:
        ollama_url = f"{Config.OLLAMA_BASE_URL.rstrip('/')}/api/tags"
        resp = requests.get(ollama_url, timeout=1.5)
        if resp.status_code == 200:
            return {
                "status": "connected",
                "provider": f"Connected to Ollama ({Config.OLLAMA_MODEL})",
                "type": "ollama",
                "color": "#3b82f6"  # Blue
            }
    except Exception:
        pass

    return {
        "status": "fallback",
        "provider": "Clinical Rule Engine (Active Fallback)",
        "type": "fallback",
        "color": "#0ea5e9"  # Cyan/Sky
    }


@app.route("/", methods=["GET"])
def index():
    """Renders the main dashboard interface."""
    provider_info = detect_provider_status()
    return render_template("index.html", provider=provider_info)


@app.route("/api/status", methods=["GET"])
def get_status():
    """Returns the live connection status."""
    return jsonify({"success": True, "provider": detect_provider_status()})


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Main clinical analysis pipeline:
    User Input -> Profile -> Symptom Extraction -> Context -> Red Flag Scan -> Analysis Engine -> Save Report -> Output
    """
    try:
        req_data = request.get_json(silent=True) or request.form.to_dict()
        if not req_data:
            return jsonify({"success": False, "error": "No input data provided."}), 400

        # Step 1: Input Module
        is_valid, input_data, err_msg = InputModule.collect_and_validate(req_data)
        if not is_valid:
            return jsonify({"success": False, "error": err_msg}), 400

        # Step 2: Profile Module
        is_profile_valid, profile, prof_err = ProfileModule.validate_and_create_profile(
            input_data["age_raw"], input_data["sex"]
        )
        if not is_profile_valid:
            return jsonify({"success": False, "error": prof_err}), 400

        # Step 3: Symptom Module (Discrete clinical entity extraction)
        extracted_symptoms = SymptomModule.extract_symptoms(input_data["symptoms_raw"])

        # Step 4: Context Module (Acuity, comorbidity, severity analysis)
        context = ContextModule.analyze_context(input_data)

        # Step 5: Safety Module (Pre-inference Red Flag screening)
        red_flags = SafetyModule.scan_red_flags(
            input_data["symptoms_raw"], extracted_symptoms, input_data.get("additional_info", "")
        )

        # Step 6: Analysis Module (GPT-4 / Ollama / Clinical Engine)
        analysis_result, engine_name = AnalysisModule.analyze(
            profile=profile,
            extracted_symptoms=extracted_symptoms,
            context=context,
            raw_text=input_data["symptoms_raw"],
            red_flags=red_flags,
        )

        # Step 7: Save Module (Auto-persist timestamped report)
        save_success, report_id, json_path, txt_path = SaveModule.save_report(
            analysis_data=analysis_result,
            profile=profile,
            context=context,
            raw_symptoms=input_data["symptoms_raw"],
            engine_name=engine_name,
        )

        return jsonify({
            "success": True,
            "report_id": report_id,
            "engine": engine_name,
            "profile": profile,
            "context": context,
            "analysis": analysis_result,
            "report_files": {
                "json_filename": os.path.basename(json_path) if save_success else None,
                "txt_filename": os.path.basename(txt_path) if save_success else None,
            }
        })

    except Exception as e:
        logger.exception("Unexpected error in /analyze endpoint")
        return jsonify({
            "success": False,
            "error": "A system error occurred while processing the clinical analysis. Please verify your inputs and try again."
        }), 500


@app.route("/save-report", methods=["POST"])
def save_report_explicit():
    """Explicitly save a report or export specific content."""
    try:
        req_data = request.get_json(silent=True)
        if not req_data:
            return jsonify({"success": False, "error": "No report data provided."}), 400

        analysis = req_data.get("analysis", {})
        profile = req_data.get("profile", {})
        context = req_data.get("context", {})
        raw_symptoms = req_data.get("raw_symptoms", "")
        engine = req_data.get("engine", "Clinical Engine")

        success, report_id, json_path, txt_path = SaveModule.save_report(
            analysis, profile, context, raw_symptoms, engine
        )

        if success:
            return jsonify({
                "success": True,
                "report_id": report_id,
                "json_filename": os.path.basename(json_path),
                "txt_filename": os.path.basename(txt_path)
            })
        else:
            return jsonify({"success": False, "error": txt_path}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/reports/<path:filename>", methods=["GET"])
def download_report(filename):
    """Allows downloading or viewing generated reports."""
    return send_from_directory(Config.REPORTS_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    logger.info(f"Starting Medical Symptom Assistant on http://{Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
