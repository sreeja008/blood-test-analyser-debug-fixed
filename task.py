from typing import Dict, Any
try:
    from crewai import Task
    _HAVE_CREWAI = True
except Exception:
    _HAVE_CREWAI = False

from agents import doctor
from tools import BloodTestReportTool, simple_blood_analysis

if _HAVE_CREWAI and doctor is not None:
    help_patients = Task(
        description=(
            "Extract relevant metrics (e.g., Hemoglobin, RBC, WBC, Platelets, Glucose, Cholesterol) "
            "from the provided PDF at {file_path}. Use them to produce a clear, non-alarming summary. "
            "If a value is outside typical adult ranges, flag it and advise consulting a doctor. "
            "If a metric is not found, say 'not present in document'. "
            "Never invent values or diagnoses."
        ),
        expected_output=(
            "JSON with keys: summary, metrics (dict name->value), flags (list), recommendations (list)."
        ),
        agent=doctor,
        tools=[BloodTestReportTool.read_data_tool],
        async_execution=False
    )
else:
    # Fallback (no CrewAI): emulate the 'task' by calling our rule-based analyzer
    def help_patients(query: str, file_path: str) -> Dict[str, Any]:
        text = BloodTestReportTool.read_data_tool(file_path)
        out = simple_blood_analysis(text)
        out.update({"query": query})
        return out
