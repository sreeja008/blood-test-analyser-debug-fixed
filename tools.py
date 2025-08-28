import os
from typing import Dict, Any
from dotenv import load_dotenv
load_dotenv()

try:
    from crewai_tools.tools.serper_dev_tool import SerperDevTool
    search_tool = SerperDevTool()
except Exception:
    # Fallback if crewai_tools or key not present
    class _DummySearch:
        def run(self, query: str) -> str:
            return "Search disabled (no API key)."
    search_tool = _DummySearch()

from pypdf import PdfReader

class BloodTestReportTool:
    @staticmethod
    def read_data_tool(path: str = 'data/sample.pdf') -> str:
        """Read text from a PDF file at `path`. Returns extracted text."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"PDF not found at: {path}")
        try:
            reader = PdfReader(path)
            texts = []
            for page in reader.pages:
                txt = page.extract_text() or ''
                texts.append(txt)
            return "\n".join(texts).strip()
        except Exception as e:
            raise RuntimeError(f"Failed reading PDF: {e}")

def simple_blood_analysis(text: str) -> Dict[str, Any]:
    """Very simple rule-based analysis for common markers if LLMs are unavailable."""
    findings = []
    lower = text.lower()
    def find(marker, threshold_keyword):
        return marker in lower and threshold_keyword in lower

    if 'hemoglobin' in lower:
        findings.append("Hemoglobin value detected. Compare with normal ranges (F: 12–15 g/dL, M: 13–17 g/dL)."))
    if 'wbc' in lower or 'white blood cell' in lower:
        findings.append("WBC mentioned; check for signs of infection or inflammation.")
    if 'platelet' in lower:
        findings.append("Platelet count referenced; assess for bleeding risk if low.")
    if not findings:
        findings.append("No standard markers auto-detected; review manually.")
    return {
        "summary": "Rule-based analysis (fallback)",
        "findings": findings[:6]
    }
