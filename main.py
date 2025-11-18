
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def load_questions():
    with open("questions.json", encoding="utf-8") as f:
        return json.load(f)

@app.get("/assessment")
async def assessment(request: Request):
    questions = load_questions()
    return templates.TemplateResponse("assessment.html", {"request": request, "questions": questions})


@app.post("/submit")
async def submit(request: Request):
    form = await request.form()
    questions = load_questions()
    score = 0
    for idx, q in enumerate(questions, start=1):
        correct = [c["text"] for c in q["choices"] if c["is_correct"]]
        field = f"answers{idx}"
        user_ans = form.getlist(field)
        # For single-select, user_ans is a list with one item
        if len(correct) == 1:
            if user_ans and user_ans[0] == correct[0]:
                score += 1
        else:
            # For multi-select, must match all correct and only correct
            if set(user_ans) == set(correct):
                score += 1
    return RedirectResponse(f"/result?score={score}", status_code=303)

@app.get("/result")
async def result(request: Request, score: int = 0):
    questions = load_questions()
    total = len(questions)
    return templates.TemplateResponse("result.html", {"request": request, "score": score, "total": total})
