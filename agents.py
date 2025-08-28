import os
from dotenv import load_dotenv
load_dotenv()

# Optional CrewAI agent definition (used only if crewai is installed)
try:
    from crewai.agents import Agent
    from crewai import LLM
    _HAVE_CREWAI = True
except Exception:
    _HAVE_CREWAI = False

from tools import search_tool, BloodTestReportTool

doctor = None

if _HAVE_CREWAI:
    # Configure LLM via environment; fall back to mock provider for safety
    # Example: export OPENAI_MODEL=gpt-4o-mini and OPENAI_API_KEY=...
    provider = os.getenv("OPENAI_MODEL", "mock")
    llm = LLM(model=provider) if provider != "mock" else None

    doctor = Agent(
        role="Board-certified Internal Medicine Physician",
        goal=(
            "Analyze the uploaded blood test report accurately and safely, "
            "explain key markers, flag abnormalities with ranges, and suggest next steps. "
            "Never fabricate values; if unsure, say so."
        ),
        backstory=(
            "You are a careful, evidence-based clinician focused on patient safety. "
            "You avoid hallucinations and always cite the exact values from the report text."
        ),
        verbose=True,
        llm=llm,
        max_iter=3,
        max_rpm=5,
        allow_delegation=False
    )
