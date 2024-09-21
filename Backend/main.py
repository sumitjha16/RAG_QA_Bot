from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from worker import run_in_process
from fastapi.responses import JSONResponse

app = FastAPI()

class Question(BaseModel):
    question: str
    pdf: str

class PDFInput(BaseModel):
    pdf: str

@app.get("/")
def root():
    return {"status": "Server running."}

@app.post("/ask")
async def ask_question(question: Question):
    try:
        ans = run_in_process(question.pdf, question.question)
        return {"answer": ans}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize")
async def summarize_document(pdf_input: PDFInput):
    try:
        summary = run_in_process(pdf_input.pdf)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
async def reset_backend_state():
    return JSONResponse(content={"message": "Backend uses a new process for each request"}, status_code=200)