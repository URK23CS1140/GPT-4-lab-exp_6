/**
 * AI-Powered Medical Symptom Assistant using GPT-4
 * Frontend Application Controller
 * Experiment 6 / 24CS2506
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const form = document.getElementById('symptomForm');
    const symptomInput = document.getElementById('symptomDescription');
    const ageInput = document.getElementById('patientAge');
    const sexInput = document.getElementById('patientSex');
    const durationInput = document.getElementById('symptomDuration');
    const severityInput = document.getElementById('reportedSeverity');
    const medHistoryInput = document.getElementById('medicalHistory');
    const medsInput = document.getElementById('currentMedications');
    const allergiesInput = document.getElementById('knownAllergies');
    const addInfoInput = document.getElementById('additionalInformation');

    const btnAnalyze = document.getElementById('btnAnalyze');
    const analyzeSpinner = document.getElementById('analyzeSpinner');
    const btnText = btnAnalyze.querySelector('.btn-text');

    const emptyStateView = document.getElementById('emptyStateView');
    const reportResultsView = document.getElementById('reportResultsView');

    // Report Display Elements
    const displayReportId = document.getElementById('displayReportId');
    const displayEngineTag = document.getElementById('displayEngineTag');
    const triageBanner = document.getElementById('triageBanner');
    const triageTitle = document.getElementById('triageTitle');
    const triageGuidance = document.getElementById('triageGuidance');
    const redFlagAlertBox = document.getElementById('redFlagAlertBox');
    const redFlagsList = document.getElementById('redFlagsList');
    const reportedSymptomsList = document.getElementById('reportedSymptomsList');
    const displayDuration = document.getElementById('displayDuration');
    const possibleConditionsList = document.getElementById('possibleConditionsList');
    const displayWhyConsidered = document.getElementById('displayWhyConsidered');
    const additionalInfoNeededList = document.getElementById('additionalInfoNeededList');
    const followUpQuestionsList = document.getElementById('followUpQuestionsList');
    const displayMedicalAttention = document.getElementById('displayMedicalAttention');
    const displayDisclaimer = document.getElementById('displayDisclaimer');

    // Action Buttons
    const btnCopyReport = document.getElementById('btnCopyReport');
    const btnDownloadTxt = document.getElementById('btnDownloadTxt');
    const btnDownloadJson = document.getElementById('btnDownloadJson');
    const btnPrintReport = document.getElementById('btnPrintReport');

    // Preset Buttons
    const btnPresetRespiratory = document.getElementById('btnPresetRespiratory');
    const btnPresetMigraine = document.getElementById('btnPresetMigraine');
    const btnPresetEmergency = document.getElementById('btnPresetEmergency');
    const btnClearForm = document.getElementById('btnClearForm');

    // Severity Pills
    const severityPills = document.querySelectorAll('.severity-pill');

    // Current State Cache
    let currentReportData = null;

    // Toast helper
    function showToast(message, duration = 3000) {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.classList.remove('hidden');
        setTimeout(() => {
            toast.classList.add('hidden');
        }, duration);
    }

    // Set Severity Pill selection
    function setSeverity(val) {
        severityInput.value = val;
        severityPills.forEach(pill => {
            if (pill.dataset.severity.toLowerCase() === val.toLowerCase()) {
                pill.classList.add('active');
            } else {
                pill.classList.remove('active');
            }
        });
    }

    severityPills.forEach(pill => {
        pill.addEventListener('click', () => {
            setSeverity(pill.dataset.severity);
        });
    });

    // Populate Presets
    btnPresetRespiratory.addEventListener('click', () => {
        symptomInput.value = "I've had a fever and cough since yesterday. I also feel tired and have a mild headache, and have a sore throat when swallowing.";
        ageInput.value = "22";
        sexInput.value = "Male";
        durationInput.value = "2 days";
        setSeverity("Moderate");
        medHistoryInput.value = "None";
        medsInput.value = "None";
        allergiesInput.value = "None";
        addInfoInput.value = "Body temperature feels slightly elevated. No shortness of breath.";
        symptomInput.focus();
        showToast("Loaded Respiratory Lab Example preset");
    });

    btnPresetMigraine.addEventListener('click', () => {
        symptomInput.value = "Throbbing headache on the right temple with nausea and sensitivity to bright lights and loud sounds.";
        ageInput.value = "28";
        sexInput.value = "Female";
        durationInput.value = "1 day";
        setSeverity("Moderate");
        medHistoryInput.value = "Occasional stress headaches";
        medsInput.value = "None";
        allergiesInput.value = "None";
        addInfoInput.value = "Pain began gradually after prolonged screen work; partially relieved by resting in a dark room.";
        symptomInput.focus();
        showToast("Loaded Tension & Migraine preset");
    });

    btnPresetEmergency.addEventListener('click', () => {
        symptomInput.value = "Crushing chest pain radiating to left arm and jaw with severe shortness of breath, sudden cold sweats, and dizziness.";
        ageInput.value = "54";
        sexInput.value = "Male";
        durationInput.value = "45 minutes";
        setSeverity("Severe");
        medHistoryInput.value = "Hypertension";
        medsInput.value = "Amlodipine 5mg";
        allergiesInput.value = "Penicillin";
        addInfoInput.value = "Started abruptly while sitting down. Heavy pressure on chest.";
        symptomInput.focus();
        showToast("Loaded Emergency Red Flag preset");
    });

    btnClearForm.addEventListener('click', () => {
        form.reset();
        medHistoryInput.value = "None";
        medsInput.value = "None";
        allergiesInput.value = "None";
        setSeverity("Moderate");
        currentReportData = null;
        reportResultsView.classList.add('hidden');
        emptyStateView.classList.remove('hidden');
        showToast("Form cleared");
    });

    // Render Analysis Result
    function renderAnalysis(data) {
        currentReportData = data;
        const analysis = data.analysis;
        const profile = data.profile;

        // Meta info
        displayReportId.textContent = data.report_id || "#REPORT_LIVE";
        displayEngineTag.textContent = data.engine || "Clinical Engine";

        // Triage Banner
        const triage = (analysis.triage_level || "MODERATE").toUpperCase();
        triageBanner.className = 'triage-banner'; // reset classes

        if (triage === 'EMERGENCY') {
            triageBanner.classList.add('triage-emergency');
            triageTitle.textContent = "🚨 TRIAGE LEVEL: EMERGENCY";
        } else if (triage === 'HIGH') {
            triageBanner.classList.add('triage-high');
            triageTitle.textContent = "TRIAGE LEVEL: HIGH";
        } else if (triage === 'LOW') {
            triageBanner.classList.add('triage-low');
            triageTitle.textContent = "TRIAGE LEVEL: LOW";
        } else {
            triageBanner.classList.add('triage-moderate');
            triageTitle.textContent = "TRIAGE LEVEL: MODERATE";
        }
        triageGuidance.textContent = analysis.medical_attention || "Routine Consultation / Monitored Self-Care";

        // Red Flags
        redFlagsList.innerHTML = '';
        if (analysis.red_flags && analysis.red_flags.length > 0) {
            analysis.red_flags.forEach(flag => {
                const li = document.createElement('li');
                li.textContent = flag;
                redFlagsList.appendChild(li);
            });
            redFlagAlertBox.classList.remove('hidden');
        } else {
            redFlagAlertBox.classList.add('hidden');
        }

        // Reported Symptoms
        reportedSymptomsList.innerHTML = '';
        const symptoms = analysis.reported_symptoms || [];
        symptoms.forEach(sym => {
            const li = document.createElement('li');
            li.textContent = sym;
            reportedSymptomsList.appendChild(li);
        });

        // Duration
        displayDuration.textContent = analysis.duration || "2 days";

        // Possible Conditions
        possibleConditionsList.innerHTML = '';
        const conditions = analysis.possible_conditions || [];
        conditions.forEach(cond => {
            const li = document.createElement('li');
            const nameEl = document.createElement('strong');
            nameEl.textContent = cond.name || "Condition";
            li.appendChild(nameEl);

            if (cond.explanation) {
                const descEl = document.createElement('div');
                descEl.className = 'condition-desc';
                descEl.textContent = cond.explanation;
                li.appendChild(descEl);
            }
            possibleConditionsList.appendChild(li);
        });

        // Why Considered
        displayWhyConsidered.textContent = analysis.why_considered || "Reported symptoms match typical clinical patterns.";

        // Additional Information Needed
        additionalInfoNeededList.innerHTML = '';
        const addNeeded = analysis.additional_information_needed || [];
        addNeeded.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            additionalInfoNeededList.appendChild(li);
        });

        // Follow-up Questions
        followUpQuestionsList.innerHTML = '';
        const questions = analysis.follow_up_questions || [];
        questions.forEach(q => {
            const li = document.createElement('li');
            li.textContent = q;
            followUpQuestionsList.appendChild(li);
        });

        // Medical Attention
        displayMedicalAttention.textContent = analysis.medical_attention || "Seek professional medical evaluation if symptoms are severe, worsening, or persist.";

        // Disclaimer
        displayDisclaimer.textContent = analysis.disclaimer || "This is an informational AI analysis and not a medical diagnosis.";

        // Show Results view
        emptyStateView.classList.add('hidden');
        reportResultsView.classList.remove('hidden');

        // Smooth scroll on small screens
        if (window.innerWidth < 1024) {
            reportResultsView.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Form Submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const payload = {
            symptoms: symptomInput.value.trim(),
            age: ageInput.value.trim(),
            sex: sexInput.value,
            duration: durationInput.value.trim(),
            severity: severityInput.value,
            previous_conditions: medHistoryInput.value.trim() || "None",
            medications: medsInput.value.trim() || "None",
            allergies: allergiesInput.value.trim() || "None",
            additional_info: addInfoInput.value.trim() || "None"
        };

        if (!payload.symptoms) {
            showToast("Please enter a description of symptoms.");
            return;
        }

        // Set UI loading state
        btnAnalyze.disabled = true;
        analyzeSpinner.classList.remove('hidden');
        btnText.textContent = "Analyzing Symptoms...";

        try {
            const resp = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await resp.json();

            if (data.success) {
                renderAnalysis(data);
                showToast("Clinical analysis generated successfully!");
            } else {
                showToast(data.error || "An error occurred during analysis.");
            }
        } catch (err) {
            console.error("Analysis Request Error:", err);
            showToast("Network connection error. Please ensure the backend is running.");
        } finally {
            btnAnalyze.disabled = false;
            analyzeSpinner.classList.add('hidden');
            btnText.textContent = "✨ Analyze Symptoms with GPT-4";
        }
    });

    // Copy to clipboard
    btnCopyReport.addEventListener('click', () => {
        if (!currentReportData) return;
        const analysis = currentReportData.analysis;
        const profile = currentReportData.profile;

        let conditionsText = "";
        (analysis.possible_conditions || []).forEach((c, idx) => {
            conditionsText += `${idx + 1}. ${c.name}\n   ${c.explanation || ''}\n`;
        });

        const copyText = `
MEDICAL SYMPTOM ANALYSIS REPORT
Report ID: ${currentReportData.report_id}
Engine: ${currentReportData.engine}

Age: ${profile.age} | Sex: ${profile.sex}
TRIAGE LEVEL: ${analysis.triage_level}
Duration: ${analysis.duration}
Severity: ${analysis.severity}

REPORTED SYMPTOMS:
${(analysis.reported_symptoms || []).map(s => '• ' + s).join('\n')}

POSSIBLE CONDITIONS:
${conditionsText}
WHY THESE WERE CONSIDERED:
${analysis.why_considered}

ADDITIONAL INFORMATION NEEDED:
${(analysis.additional_information_needed || []).map(a => '• ' + a).join('\n')}

FOLLOW-UP QUESTIONS:
${(analysis.follow_up_questions || []).map(q => '• ' + q).join('\n')}

MEDICAL ATTENTION:
${analysis.medical_attention}

DISCLAIMER:
${analysis.disclaimer}
`.trim();

        navigator.clipboard.writeText(copyText).then(() => {
            showToast("Report copied to clipboard! 📋");
        }).catch(() => {
            showToast("Failed to copy report.");
        });
    });

    // Download TXT
    btnDownloadTxt.addEventListener('click', () => {
        if (!currentReportData) return;
        const filename = currentReportData.report_files?.txt_filename;
        if (filename) {
            window.location.href = `/reports/${encodeURIComponent(filename)}`;
        } else {
            showToast("Report file not available for direct download.");
        }
    });

    // Download JSON
    btnDownloadJson.addEventListener('click', () => {
        if (!currentReportData) return;
        const filename = currentReportData.report_files?.json_filename;
        if (filename) {
            window.location.href = `/reports/${encodeURIComponent(filename)}`;
        } else {
            // Client-side fallback download
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentReportData, null, 2));
            const downloadAnchor = document.createElement('a');
            downloadAnchor.setAttribute("href", dataStr);
            downloadAnchor.setAttribute("download", `medical_report_${Date.now()}.json`);
            document.body.appendChild(downloadAnchor);
            downloadAnchor.click();
            downloadAnchor.remove();
        }
    });

    // Print Report
    btnPrintReport.addEventListener('click', () => {
        window.print();
    });
});
