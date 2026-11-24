const taskList = document.getElementById("task-list");
const form = document.getElementById("create-task-form");
const messageBox = document.getElementById("form-message");
const connection = document.getElementById("connection");
const count = document.getElementById("task-count");
let tasks = [];
const deletedTaskIds = new Set();

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}
function apiFetch(url, options = {}) {
  options.headers = {
    ...(options.headers || {}),
    "X-CSRFToken": getCookie("csrftoken") || "",
    "Content-Type": "application/json",
  };
  return fetch(url, { ...options, credentials: "same-origin" }).then(
    async (r) => {
      const data = r.status === 204 ? null : await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(data.detail || JSON.stringify(data));
      return data;
    },
  );
}
function renderTasks() {
  count.textContent = `(${tasks.length})`;
  if (!tasks.length) {
    taskList.innerHTML =
      '<div class="empty-state">No tasks yet. Create the first shared task above.</div>';
    return;
  }
  taskList.innerHTML = tasks
    .map(
      (t) => `<article class="task-card" data-id="${t.id}">
    <div><div class="task-title">${escapeHtml(t.task_name)}</div><div class="task-meta">📅 ${t.date} &nbsp; · &nbsp; ◷ ${String(t.time).slice(0, 5)} &nbsp; · &nbsp; Created by ${escapeHtml(t.created_by_username || "user")}</div>
    <div class="mt-2"><span class="status-chip ${t.status === "RUNNING" ? "status-running" : "status-stopped"}">${t.status}</span></div></div>
    <div class="task-actions">${t.status === "RUNNING" ? `<button class="btn btn-sm btn-outline-danger" onclick="changeStatus(${t.id},'stop')">Stop</button>` : `<button class="btn btn-sm btn-success" onclick="changeStatus(${t.id},'start')">Start</button>`}
    ${t.can_edit ? `<button class="btn btn-sm btn-light" onclick="editTask(${t.id})">Edit</button><button class="btn btn-sm btn-outline-danger" onclick="deleteTask(${t.id})">Delete</button>` : ""}
    ${t.can_view_history ? `<button class="btn btn-sm btn-outline-primary" onclick="viewTaskHistory(${t.id})">History</button>` : ""}</div></article>`,
    )
    .join("");
}
function escapeHtml(s) {
  return String(s).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
}
function enrich(task) {
  task.can_edit = task.created_by === window.CURRENT_USER_ID || window.IS_STAFF;
  task.can_view_history = task.created_by === window.CURRENT_USER_ID;
  return task;
}
async function loadTasks() {
  try {
    (await apiFetch(TASK_API_URL)).forEach(mergeTask);
    renderTasks();
  } catch (e) {
    taskList.innerHTML = `<div class="empty-state">${escapeHtml(e.message)}</div>`;
  }
}
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(form);
  const payload = Object.fromEntries(fd.entries());
  try {
    const task = await apiFetch(TASK_API_URL, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    form.reset();
    messageBox.textContent = "Task created.";
    messageBox.className = "small mt-2 text-success";
    upsert(task);
  } catch (err) {
    messageBox.textContent = err.message;
    messageBox.className = "small mt-2 text-danger";
  }
});
function mergeTask(raw) {
  if (deletedTaskIds.has(raw.id)) return;
  const task = enrich(raw);
  const index = tasks.findIndex((t) => t.id === task.id);
  if (index >= 0) {
    const currentUpdatedAt = Date.parse(tasks[index].updated_at);
    const incomingUpdatedAt = Date.parse(task.updated_at);
    if (incomingUpdatedAt < currentUpdatedAt) return;
    tasks[index] = task;
  } else {
    tasks.push(task);
  }
  tasks.sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at));
}
function upsert(raw) {
  mergeTask(raw);
  renderTasks();
}
async function changeStatus(id, action) {
  try {
    const task = await apiFetch(`${TASK_API_URL}${id}/${action}/`, {
      method: "POST",
      body: "{}",
    });
    upsert(task);
  } catch (e) {
    alert(e.message);
  }
}
async function deleteTask(id) {
  if (!confirm("Delete this task?")) return;
  try {
    await apiFetch(`${TASK_API_URL}${id}/`, { method: "DELETE" });
    deletedTaskIds.add(id);
    tasks = tasks.filter((t) => t.id !== id);
    renderTasks();
  } catch (e) {
    alert(e.message);
  }
}
async function viewTaskHistory(id) {
  const task = tasks.find((item) => item.id === id);
  if (!task || !task.can_view_history) return;
  const rows = document.getElementById("task-history-rows");
  const empty = document.getElementById("task-history-empty");
  rows.innerHTML = '<tr><td colspan="4" class="text-center muted">Loading history…</td></tr>';
  empty.classList.add("d-none");
  document.getElementById("task-history-title").textContent = task.task_name;
  bootstrap.Modal.getOrCreateInstance(
    document.getElementById("task-history-modal"),
  ).show();

  try {
    const data = await apiFetch(`${TASK_API_URL}${id}/history/`);
    const entries = data.results;
    if (!entries.length) {
      rows.innerHTML = "";
      empty.classList.remove("d-none");
      return;
    }
    rows.innerHTML = entries
      .map((entry) => {
        const changedAt = new Date(entry.changed_at);
        const started = entry.status === "RUNNING";
        return `<tr>
          <td><span class="status-chip ${started ? "status-running" : "status-stopped"}">${started ? "Started" : "Stopped"}</span></td>
          <td>${escapeHtml(entry.username)}</td>
          <td>${escapeHtml(changedAt.toLocaleDateString())}</td>
          <td>${escapeHtml(changedAt.toLocaleTimeString())}</td>
        </tr>`;
      })
      .join("");
  } catch (error) {
    rows.innerHTML = `<tr><td colspan="4" class="text-danger">${escapeHtml(error.message)}</td></tr>`;
  }
}
async function editTask(id) {
  const t = tasks.find((x) => x.id === id);
  if (!t) return;
  const name = prompt("Task name:", t.task_name);
  if (name === null) return;
  const date = prompt("Date (YYYY-MM-DD):", t.date);
  if (date === null) return;
  const time = prompt("Time (HH:MM):", String(t.time).slice(0, 5));
  if (time === null) return;
  try {
    const updated = await apiFetch(`${TASK_API_URL}${id}/`, {
      method: "PATCH",
      body: JSON.stringify({ task_name: name, date, time }),
    });
    upsert(updated);
  } catch (e) {
    alert(e.message);
  }
}
function connectSocket() {
  const socket = new WebSocket(WS_URL);
  socket.onopen = () => {
    connection.textContent = "● Live updates connected";
    connection.classList.add("online");
    loadTasks();
  };
  socket.onclose = () => {
    connection.textContent = "Reconnecting…";
    connection.classList.remove("online");
    setTimeout(connectSocket, 2500);
  };
  socket.onerror = () => socket.close();
  socket.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data.event === "task.deleted") {
      deletedTaskIds.add(data.task_id);
      tasks = tasks.filter((t) => t.id !== data.task_id);
      renderTasks();
    } else if (data.task) {
      upsert(data.task);
    }
  };
}
window.changeStatus = changeStatus;
window.editTask = editTask;
window.deleteTask = deleteTask;
window.viewTaskHistory = viewTaskHistory;
loadTasks();
connectSocket();
