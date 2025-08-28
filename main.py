from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import os, uuid
from typing import Dict, Any

# Optional CrewAI imports
try:
    from crewai import Crew
    from agents import doctor
    from task import help_patients
    _HAVE_CREWAI = doctor is not None
except Exception:
    _HAVE_CREWAI = False
    doctor = None
    help_patients = None

from tools import BloodTestReportTool, simple_blood_analysis

app = FastAPI(title="Blood Test Report Analyser", version="1.0.0")

def run_pipeline(query: str, file_path: str) -> Dict[str, Any]:
    if _HAVE_CREWAI and callable(getattr(help_patients, 'execute', None)):
        crew = Crew(agents=[doctor], tasks=[help_patients])
        result = crew.kickoff(inputs={"query": query, "file_path": file_path})
        # Ensure JSON serializable
        return {"result": str(result)}
    elif callable(help_patients):
        # Fallback function-style task
        return help_patients(query=query, file_path=file_path)
    else:
        # Ultimate fallback: just parse text and run rule-based
        text = BloodTestReportTool.read_data_tool(file_path)
        return simple_blood_analysis(text)

@app.post("/analyze")
async def analyze(query: str = Form('Analyze blood report'), file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    os.makedirs("uploads", exist_ok=True)
    temp_path = os.path.join("uploads", f"{uuid.uuid4()}.pdf")
    data = await file.read()
    with open(temp_path, 'wb') as f:
        f.write(data)
    try:
        result = run_pipeline(query, temp_path)
        return JSONResponse(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {e}")
    finally:
        try:
            os.remove(temp_path)
        except Exception:
            pass

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
