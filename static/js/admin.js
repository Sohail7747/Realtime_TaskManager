function cookie(name) {
  const v = `; ${document.cookie}`;
  const p = v.split(`; ${name}=`);
  return p.length === 2 ? p.pop().split(";").shift() : "";
}
async function api(url, opts = {}) {
  opts.headers = {
    ...(opts.headers || {}),
    "X-CSRFToken": cookie("csrftoken"),
    "Content-Type": "application/json",
  };
  const r = await fetch(url, { ...opts, credentials: "same-origin" });
  const d = r.status === 204 ? null : await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.detail || JSON.stringify(d));
  return d;
}
function userModal() {
  return bootstrap.Modal.getOrCreateInstance(
    document.getElementById("userModal"),
  );
}
function openCreateUser() {
  document.getElementById("user-form").reset();
  document.getElementById("user-id").value = "";
  document.getElementById("user-modal-title").textContent = "Add user";
  document.getElementById("password-wrap").style.display = "block";
}
async function editUser(id) {
  try {
    const u = await api(`/api/admin/users/${id}/`);
    document.getElementById("user-id").value = u.id;
    document.getElementById("user-username").value = u.username;
    document.getElementById("user-email").value = u.email;
    document.getElementById("user-active").checked = u.is_active;
    document.getElementById("password-wrap").style.display = "none";
    document.getElementById("user-modal-title").textContent = "Edit user";
    userModal().show();
  } catch (e) {
    alert(e.message);
  }
}
document.getElementById("user-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = document.getElementById("user-id").value;
  const payload = {
    username: document.getElementById("user-username").value,
    email: document.getElementById("user-email").value,
    is_active: document.getElementById("user-active").checked,
  };
  try {
    if (id)
      await api(`/api/admin/users/${id}/`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
    else {
      payload.password = document.getElementById("user-password").value;
      await api("/api/admin/users/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    }
    location.reload();
  } catch (err) {
    alert(err.message);
  }
});
async function deleteUser(id) {
  if (!confirm("Delete this user? Their owned tasks will also be deleted."))
    return;
  try {
    await api(`/api/admin/users/${id}/`, { method: "DELETE" });
    location.reload();
  } catch (e) {
    alert(e.message);
  }
}
async function editAdminTask(id) {
  try {
    const t = await api(`/api/admin/tasks/${id}/`);
    document.getElementById("admin-task-id").value = id;
    document.getElementById("admin-task-name").value = t.task_name;
    document.getElementById("admin-task-date").value = t.date;
    document.getElementById("admin-task-time").value = String(t.time).slice(
      0,
      5,
    );
    bootstrap.Modal.getOrCreateInstance(
      document.getElementById("taskModal"),
    ).show();
  } catch (e) {
    alert(e.message);
  }
}
document
  .getElementById("admin-task-form")
  ?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("admin-task-id").value;
    try {
      await api(`/api/admin/tasks/${id}/`, {
        method: "PATCH",
        body: JSON.stringify({
          task_name: document.getElementById("admin-task-name").value,
          date: document.getElementById("admin-task-date").value,
          time: document.getElementById("admin-task-time").value,
        }),
      });
      location.reload();
    } catch (err) {
      alert(err.message);
    }
  });
async function deleteAdminTask(id) {
  if (!confirm("Permanently delete this task?")) return;
  try {
    await api(`/api/admin/tasks/${id}/`, { method: "DELETE" });
    location.reload();
  } catch (e) {
    alert(e.message);
  }
}
window.openCreateUser = openCreateUser;
window.editUser = editUser;
window.deleteUser = deleteUser;
window.editAdminTask = editAdminTask;
window.deleteAdminTask = deleteAdminTask;
