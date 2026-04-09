import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from environment import CodeReviewEnv, Action

app = FastAPI()
sessions = {}

# ── Request Model ─────────────────────────────────────────
class StepRequest(BaseModel):
    priority: int


# ── RESET ─────────────────────────────────────────
@app.post("/reset")
async def reset(session_id: str = None, task: str = "easy"):
    if not session_id or session_id not in sessions:
        session_id = session_id or str(uuid.uuid4())
        sessions[session_id] = CodeReviewEnv()

    sessions[session_id].set_task(task)
    obs = sessions[session_id].reset()

    return {
        "session_id": session_id,
        "observation": obs.dict()
    }


# ── STEP (FIXED) ─────────────────────────────────────────
@app.post("/step")
async def step(session_id: str, req: StepRequest):
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")

    action = Action(priority=req.priority)
    obs, reward, done, info = sessions[session_id].step(action)

    return {
        "observation": obs.dict() if obs else None,  # ✅ FIXED
        "reward": reward,
        "done": done,
        "info": info
    }


# ── STATE ─────────────────────────────────────────
@app.get("/state")
async def state(session_id: str):
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")

    return {
        "state": sessions[session_id].state().dict()
    }


# ── UI HTML ─────────────────────────────────────────
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>PR Priority Pilot</title>
    <style>
        body { font-family: Arial; background: #1e3c72; padding: 20px; }
        .container { max-width: 800px; margin: auto; background: white; border-radius: 20px; padding: 20px; }
        button { padding: 10px 20px; margin: 5px; border: none; border-radius: 30px; cursor: pointer; font-weight: bold; }
        .low { background: #48bb78; color: white; }
        .medium { background: #ed8936; color: white; }
        .high { background: #e53e3e; color: white; }
        .pr-card { background: #f0f4ff; padding: 15px; border-radius: 15px; margin: 15px 0; }
        .badge { background: #667eea; color: white; padding: 2px 8px; border-radius: 15px; font-size: 12px; margin-right: 5px; }
    </style>
</head>
<body>
<div class="container">
    <h1>🚀 PR Priority Pilot</h1>

    <div>
        <strong>Difficulty:</strong>
        <select id="task">
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
        </select>
        <button onclick="resetEnv()">Reset</button>
    </div>

    <div id="prCard">Click Reset</div>

    <div>
        <button onclick="takeAction(0)">Low</button>
        <button onclick="takeAction(1)">Medium</button>
        <button onclick="takeAction(2)">High</button>
    </div>

    <h3>Score: <span id="score">0</span></h3>
</div>

<script>
let sessionId = null;
let totalScore = 0;
let count = 0;

async function apiCall(endpoint, method, body=null) {
    const options = { method, headers: { "Content-Type": "application/json" } };
    if (body) options.body = JSON.stringify(body);

    const res = await fetch(endpoint + (sessionId ? `?session_id=${sessionId}` : ""), options);
    return await res.json();
}

async function resetEnv() {
    const task = document.getElementById("task").value;
    const data = await apiCall(`/reset?task=${task}`, "POST");

    sessionId = data.session_id;
    render(data.observation);

    totalScore = 0;
    count = 0;
    updateScore();
}

function render(obs) {
    document.getElementById("prCard").innerHTML = `
        <h3>${obs.pr_title}</h3>
        <p>${obs.pr_description}</p>
        <p>Files: ${obs.files_changed}</p>
        <p>Author: ${obs.author}</p>
        <p>Labels: ${obs.labels.join(", ")}</p>
    `;
}

async function takeAction(priority) {
    const data = await apiCall("/step", "POST", { priority });

    totalScore += data.reward;
    count++;
    updateScore();

    await resetEnv(); // next PR
}

function updateScore() {
    document.getElementById("score").innerText = (totalScore / (count || 1)).toFixed(2);
}
</script>

</body>
</html>
"""

# ── ROOT ─────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def root():
    return HTML


# ── MAIN ─────────────────────────────────────────
def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
