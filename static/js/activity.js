const historyList = document.getElementById("history-list");
const historyMessage = document.getElementById("history-message");
const historyMore = document.getElementById("history-more");
const connection = document.getElementById("history-connection");
const historyEntries = new Map();
let nextPage = window.HISTORY_API_URL;
let loading = false;

function escapeHtml(value) {
  return String(value).replace(
    /[&<>"']/g,
    (character) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      })[character],
  );
}

function renderHistory() {
  const entries = [...historyEntries.values()].sort(
    (a, b) => Date.parse(b.changed_at) - Date.parse(a.changed_at),
  );
  if (!entries.length) {
    historyList.innerHTML = "";
    historyMessage.textContent = "No task activity yet.";
    historyMessage.classList.remove("d-none");
  } else {
    historyMessage.classList.add("d-none");
    historyList.innerHTML = entries
      .map((entry) => {
        const changedAt = new Date(entry.changed_at);
        const started = entry.status === "RUNNING";
        return `<tr>
          <td class="fw-semibold">${escapeHtml(entry.task_name)}</td>
          <td><span class="status-chip ${started ? "status-running" : "status-stopped"}">${started ? "Started" : "Stopped"}</span></td>
          <td>${escapeHtml(entry.username)}</td>
          <td>${escapeHtml(changedAt.toLocaleDateString())}</td>
          <td>${escapeHtml(changedAt.toLocaleTimeString())}</td>
        </tr>`;
      })
      .join("");
  }
  historyMore.classList.toggle("d-none", !nextPage);
}

function addHistory(entry) {
  if (!entry || !entry.id) return;
  historyEntries.set(entry.id, entry);
  renderHistory();
}

async function loadHistory(url) {
  if (loading || !url) return;
  loading = true;
  historyMore.disabled = true;
  try {
    const response = await fetch(url, { credentials: "same-origin" });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || JSON.stringify(data));
    }
    data.results.forEach((entry) => historyEntries.set(entry.id, entry));
    nextPage = data.next;
    renderHistory();
  } catch (error) {
    historyList.innerHTML = "";
    historyMessage.textContent = error.message;
    historyMessage.classList.remove("d-none");
  } finally {
    loading = false;
    historyMore.disabled = false;
    historyMore.classList.toggle("d-none", !nextPage);
  }
}

historyMore.addEventListener("click", () => loadHistory(nextPage));

function connectSocket() {
  const socket = new WebSocket(window.WS_URL);
  socket.onopen = () => {
    connection.textContent = "● Live updates connected";
    connection.classList.add("online");
    loadHistory(window.HISTORY_API_URL);
  };
  socket.onclose = () => {
    connection.textContent = "Reconnecting…";
    connection.classList.remove("online");
    setTimeout(connectSocket, 2500);
  };
  socket.onerror = () => socket.close();
  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    addHistory(data.history);
  };
}

loadHistory(nextPage);
connectSocket();
