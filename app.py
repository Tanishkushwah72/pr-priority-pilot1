import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from environment import PrioritizerEnv, Action

app = FastAPI()
sessions = {}

# ---------- OpenEnv Endpoints ----------
@app.post("/reset")
def reset(session_id: str = None, task: str = "easy"):
    if not session_id or session_id not in sessions:
        session_id = session_id or str(uuid.uuid4())
        sessions[session_id] = PrioritizerEnv()
    sessions[session_id].set_task(task)
    obs = sessions[session_id].reset()
    return {"session_id": session_id, "observation": obs.dict()}

@app.post("/step")
def step(session_id: str, action: Action):
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")
    obs, reward, done, info = sessions[session_id].step(action)
    return {"observation": obs.dict(), "reward": reward, "done": done, "info": info}

@app.get("/state")
def state(session_id: str):
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")
    return {"state": sessions[session_id].state().dict()}

# ---------- Beautiful HTML/CSS/JS UI ----------
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PR Priority Pilot | AI Code Review Prioritizer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card {
            background: white;
            border-radius: 24px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        }
        .pr-card { background: linear-gradient(135deg, #fff, #f0f4ff); border-left: 8px solid #667eea; }
        .pr-title { font-size: 1.6rem; font-weight: bold; color: #1a202c; margin-bottom: 12px; }
        .pr-desc { color: #4a5568; line-height: 1.5; margin-bottom: 15px; }
        .pr-meta { display: flex; gap: 20px; margin-bottom: 15px; color: #718096; font-size: 0.9rem; }
        .badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            margin-right: 8px;
        }
        .task-options {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 20px;
        }
        .task-option {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 1rem;
            cursor: pointer;
            padding: 8px 16px;
            border-radius: 40px;
            background: #e2e8f0;
            transition: 0.2s;
        }
        .task-option.selected { background: #667eea; color: white; }
        .btn {
            border: none;
            padding: 8px 20px;
            border-radius: 30px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
        }
        .btn-primary { background: #4a5568; color: white; }
        .btn-warning { background: #ed8936; color: white; }
        .priority-buttons {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 20px 0;
        }
        .priority-btn {
            border: none;
            padding: 12px 30px;
            border-radius: 50px;
            font-weight: bold;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.1s;
        }
        .priority-btn:active { transform: scale(0.95); }
        .low { background: #48bb78; color: white; }
        .medium { background: #ed8936; color: white; }
        .high { background: #e53e3e; color: white; }
        .result {
            padding: 15px;
            border-radius: 15px;
            margin-top: 15px;
            font-weight: bold;
        }
        .reward-good { background: #c6f6d5; color: #22543d; }
        .reward-medium { background: #feebc8; color: #7b341e; }
        .reward-bad { background: #fed7d7; color: #742a2a; }
        .score-number { font-size: 2rem; font-weight: bold; }
        .progress-bar {
            background: #e2e8f0;
            border-radius: 20px;
            height: 20px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            background: #667eea;
            height: 100%;
            width: 0%;
            transition: width 0.3s;
        }
        .history-list {
            max-height: 150px;
            overflow-y: auto;
            font-size: 0.85rem;
        }
        .history-item {
            padding: 5px;
            border-bottom: 1px solid #e2e8f0;
        }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        .loading {
            display: inline-block;
            width: 14px;
            height: 14px;
            border: 2px solid #ccc;
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
            margin-left: 8px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .footer { text-align: center; color: white; margin-top: 30px; opacity: 0.8; }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🚀 PR Priority Pilot</h1>
        <p>AI-powered code review prioritizer – choose the right pull request first</p>
    </div>

    <div class="grid-2">
        <div>
            <div class="card">
                <div style="text-align: center; font-weight: bold; margin-bottom: 15px;">📌 Select Difficulty</div>
                <div class="task-options" id="taskOptions">
                    <div class="task-option" data-task="easy">📘 Easy</div>
                    <div class="task-option" data-task="medium">📙 Medium</div>
                    <div class="task-option" data-task="hard">📕 Hard</div>
                </div>
                <div style="display: flex; justify-content: center; gap: 10px;">
                    <button class="btn btn-primary" id="resetBtn">⟳ Reset (Score & PR)</button>
                    <button class="btn btn-warning" id="nextBtn">➡️ Next PR (No Reward)</button>
                </div>
            </div>
            <div class="card">
                <h3>🏆 Total Score</h3>
                <div class="score-number" id="totalScore">0.0</div>
                <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
                <div id="progressText">Reviewed 0 / 3 PRs</div>
            </div>
            <div class="card">
                <h3>📜 Reward History</h3>
                <div id="historyList" class="history-list">No actions yet.</div>
            </div>
        </div>
        <div class="card pr-card" id="prCard">
            <div style="text-align: center; color: #718096;">Click "Reset" to start</div>
        </div>
    </div>

    <div class="card">
        <div style="text-align: center; font-weight: bold; margin-bottom: 15px;">⚡ Assign Priority</div>
        <div class="priority-buttons">
            <button class="priority-btn low" data-priority="0">🐞 Low</button>
            <button class="priority-btn medium" data-priority="1">⚙️ Medium</button>
            <button class="priority-btn high" data-priority="2">🔥 High</button>
        </div>
        <div id="resultArea" style="display: none;" class="result"></div>
    </div>
    <div class="footer">
        💡 Reward: 1.0 (perfect) | 0.5 (off by one) | 0.0 (ignores security/critical)<br>
        Reset clears score & progress. Next PR loads new PR without reward.
    </div>
</div>

<script>
    let sessionId = null;
    let currentTask = "easy";
    let totalScore = 0.0;
    let reviewedCount = 0;
    let history = [];

    const taskOptions = document.querySelectorAll('.task-option');
    const resetBtn = document.getElementById('resetBtn');
    const nextBtn = document.getElementById('nextBtn');
    const prCard = document.getElementById('prCard');
    const resultDiv = document.getElementById('resultArea');
    const totalScoreSpan = document.getElementById('totalScore');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const historyDiv = document.getElementById('historyList');
    const priorityBtns = document.querySelectorAll('.priority-btn');

    function updateUI() {
        totalScoreSpan.innerText = totalScore.toFixed(1);
        const percent = (reviewedCount / 3) * 100;
        progressFill.style.width = percent + '%';
        progressText.innerText = `Reviewed ${reviewedCount} / 3 PRs`;
        if (history.length === 0) {
            historyDiv.innerHTML = 'No actions yet.';
        } else {
            historyDiv.innerHTML = history.slice().reverse().map(h => `<div class="history-item">${h}</div>`).join('');
        }
    }

    function addToHistory(reward, explanation, priorityName) {
        const timestamp = new Date().toLocaleTimeString();
        const icon = reward > 0.8 ? '✅' : (reward > 0.4 ? '⚠️' : '❌');
        history.unshift(`${timestamp} ${icon} ${priorityName} → ${reward.toFixed(2)} (${explanation})`);
        if (history.length > 10) history.pop();
        updateUI();
    }

    async function apiCall(endpoint, method, body = null) {
        const url = window.location.origin + endpoint;
        const options = { method, headers: { 'Content-Type': 'application/json' } };
        if (body) options.body = JSON.stringify(body);
        const res = await fetch(url, options);
        if (!res.ok) throw new Error(await res.text());
        return res.json();
    }

    async function loadPR(resetScore = false) {
        setButtonsDisabled(true);
        prCard.innerHTML = '<div style="text-align: center;">🔄 Loading PR... <span class="loading"></span></div>';
        resultDiv.style.display = 'none';
        try {
            const data = await apiCall('/reset', 'POST', { task: currentTask });
            sessionId = data.session_id;
            renderPR(data.observation);
            if (resetScore) {
                totalScore = 0.0;
                reviewedCount = 0;
                history = [];
                updateUI();
            }
        } catch (err) {
            prCard.innerHTML = `<div style="color: red;">Error: ${err.message}</div>`;
        } finally {
            setButtonsDisabled(false);
        }
    }

    function renderPR(obs) {
        const labelsHtml = (obs.labels || []).map(l => `<span class="badge">${escapeHtml(l)}</span>`).join('');
        prCard.innerHTML = `
            <div>
                <div class="pr-title">📌 ${escapeHtml(obs.title)}</div>
                <div class="pr-desc">${escapeHtml(obs.description)}</div>
                ${obs.files_changed ? `<div class="pr-meta"><span>📄 ${obs.files_changed} files changed</span></div>` : ''}
                <div>${labelsHtml}</div>
            </div>
        `;
    }

    function escapeHtml(str) {
        return str.replace(/[&<>]/g, function(m) {
            if (m === '&') return '&amp;';
            if (m === '<') return '&lt;';
            if (m === '>') return '&gt;';
            return m;
        });
    }

    async function takeAction(priority, priorityName) {
        if (!sessionId) { alert('Please reset first.'); return; }
        setPriorityBtnsDisabled(true);
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = '⏳ Processing... <span class="loading"></span>';
        resultDiv.className = 'result';
        try {
            const stepData = await apiCall(`/step?session_id=${sessionId}`, 'POST', { priority: priority });
            const reward = stepData.reward;
            const explanation = stepData.info?.explanation || (reward > 0.8 ? 'Perfect match!' : (reward > 0.4 ? 'Close enough' : 'Wrong priority'));
            totalScore += reward;
            reviewedCount++;
            addToHistory(reward, explanation, priorityName);
            let rewardClass = '';
            let rewardText = '';
            if (reward > 0.8) { rewardText = '🏆 Perfect!'; rewardClass = 'reward-good'; }
            else if (reward > 0.4) { rewardText = '⚠️ Close enough!'; rewardClass = 'reward-medium'; }
            else { rewardText = '❌ Wrong priority!'; rewardClass = 'reward-bad'; }
            resultDiv.innerHTML = `<strong>${rewardText}</strong><br>Reward: ${reward.toFixed(3)}<br>${explanation}`;
            resultDiv.className = `result ${rewardClass}`;
            setTimeout(() => {
                loadPR(false);
                resultDiv.style.display = 'none';
            }, 1200);
        } catch (err) {
            resultDiv.innerHTML = `<span style="color:red;">Error: ${err.message}</span>`;
            resultDiv.className = 'result reward-bad';
        } finally {
            setPriorityBtnsDisabled(false);
        }
    }

    function setButtonsDisabled(disabled) {
        resetBtn.disabled = disabled;
        nextBtn.disabled = disabled;
        setPriorityBtnsDisabled(disabled);
    }
    function setPriorityBtnsDisabled(disabled) {
        priorityBtns.forEach(btn => btn.disabled = disabled);
    }

    // Task selection
    taskOptions.forEach(opt => {
        opt.addEventListener('click', async () => {
            taskOptions.forEach(o => o.classList.remove('selected'));
            opt.classList.add('selected');
            currentTask = opt.getAttribute('data-task');
            await loadPR(true);
        });
    });
    resetBtn.addEventListener('click', () => loadPR(true));
    nextBtn.addEventListener('click', () => loadPR(false));
    priorityBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const priority = parseInt(btn.getAttribute('data-priority'));
            const name = btn.innerText.trim();
            takeAction(priority, name);
        });
    });

    // Initial load
    document.querySelector('.task-option[data-task="easy"]').classList.add('selected');
    loadPR(true);
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def root():
    return HTML_PAGE

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()