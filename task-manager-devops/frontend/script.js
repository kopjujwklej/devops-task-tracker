// ============================================================
// DevOps Task Tracker — Frontend
// ------------------------------------------------------------
// Zwykły vanilla JS (bez frameworka), żeby na tym etapie
// skupić się na architekturze DevOps, a nie na Reakcie.
// ============================================================

// 🔴 MUST KNOW: adres backendu bierzemy z jednego miejsca.
// W prawdziwym projekcie ta wartość różni się między
// dev/staging/prod — tutaj na razie hardcodujemy localhost,
// w FAZIE 1.3 (Docker) nauczymy się to parametryzować.
const API_BASE = "http://localhost:5000";

const taskForm = document.getElementById("task-form");
const taskTitleInput = document.getElementById("task-title");
const taskList = document.getElementById("task-list");
const emptyState = document.getElementById("empty-state");
const statusDot = document.getElementById("status-dot");

// --- POBIERANIE ZADAŃ ----------------------------------------------------

async function fetchTasks() {
  try {
    const res = await fetch(`${API_BASE}/api/tasks`);
    if (!res.ok) throw new Error(`Backend odpowiedział ${res.status}`);
    const tasks = await res.json();
    renderTasks(tasks);
    setStatus(true);
  } catch (err) {
    // 🟡 NICE TO KNOW: w realnej appce tu poszedłby log do systemu
    // monitoringu (patrz FAZA 5 — Observability), a nie tylko console.error
    console.error("Nie udało się pobrać zadań:", err);
    setStatus(false);
  }
}

function setStatus(isUp) {
  statusDot.style.background = isUp ? "var(--accent)" : "var(--danger)";
  statusDot.style.boxShadow = isUp
    ? "0 0 8px var(--accent)"
    : "0 0 8px var(--danger)";
}

// --- RENDEROWANIE LISTY ---------------------------------------------------

function renderTasks(tasks) {
  taskList.innerHTML = "";
  emptyState.hidden = tasks.length > 0;

  for (const task of tasks) {
    const li = document.createElement("li");
    li.className = `task-item${task.is_done ? " done" : ""}`;

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = task.is_done;
    checkbox.addEventListener("change", () => toggleTask(task.id, checkbox.checked));

    const span = document.createElement("span");
    span.textContent = task.title;

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "usuń";
    deleteBtn.addEventListener("click", () => deleteTask(task.id));

    li.append(checkbox, span, deleteBtn);
    taskList.appendChild(li);
  }
}

// --- AKCJE CRUD -------------------------------------------------------

taskForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = taskTitleInput.value.trim();
  if (!title) return;

  await fetch(`${API_BASE}/api/tasks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });

  taskTitleInput.value = "";
  fetchTasks();
});

async function toggleTask(id, isDone) {
  await fetch(`${API_BASE}/api/tasks/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ is_done: isDone }),
  });
  fetchTasks();
}

async function deleteTask(id) {
  await fetch(`${API_BASE}/api/tasks/${id}`, { method: "DELETE" });
  fetchTasks();
}

// --- START ----------------------------------------------------------------

fetchTasks();
// Odświeżamy co 10s — prosty "polling". W realnym systemie monitoringu
// (FAZA 5) zamienilibyśmy to na coś mądrzejszego (WebSockety, SSE).
setInterval(fetchTasks, 10000);
