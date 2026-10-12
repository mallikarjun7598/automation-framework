/* To-Do app logic. State persists in the browser via localStorage, so no
   backend/database is needed — this keeps hosting free and the app usable
   offline once installed as a PWA. */
(function () {
  "use strict";

  const STORAGE_KEY = "todo.items.v1";
  const form = document.getElementById("todo-form");
  const input = document.getElementById("todo-input");
  const list = document.getElementById("todo-list");
  const empty = document.getElementById("todo-empty");
  const summary = document.getElementById("todo-summary");

  /** @typedef {{id: string, text: string, done: boolean}} Todo */

  /** @returns {Todo[]} */
  function load() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
    } catch {
      return [];
    }
  }

  /** @param {Todo[]} items */
  function save(items) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  }

  function uid() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  }

  function render() {
    const items = load();
    list.innerHTML = "";

    items.forEach(function (item) {
      const li = document.createElement("li");
      li.className = "list-item" + (item.done ? " done" : "");
      li.setAttribute("data-testid", "todo-item");
      li.setAttribute("data-id", item.id);

      const label = document.createElement("label");
      label.className = "item-main";

      const cb = document.createElement("input");
      cb.type = "checkbox";
      cb.checked = item.done;
      cb.setAttribute("data-testid", "todo-toggle");
      cb.addEventListener("change", function () {
        toggle(item.id);
      });

      const span = document.createElement("span");
      span.className = "item-text";
      span.setAttribute("data-testid", "todo-text");
      span.textContent = item.text;

      label.appendChild(cb);
      label.appendChild(span);

      const del = document.createElement("button");
      del.className = "icon-btn";
      del.setAttribute("data-testid", "todo-delete");
      del.setAttribute("aria-label", "Delete task");
      del.textContent = "✕";
      del.addEventListener("click", function () {
        remove(item.id);
      });

      li.appendChild(label);
      li.appendChild(del);
      list.appendChild(li);
    });

    const remaining = items.filter(function (i) { return !i.done; }).length;
    empty.style.display = items.length ? "none" : "block";
    summary.textContent = items.length
      ? remaining + " of " + items.length + " remaining"
      : "";
  }

  function add(text) {
    const trimmed = text.trim();
    if (!trimmed) return;
    const items = load();
    items.push({ id: uid(), text: trimmed, done: false });
    save(items);
    render();
  }

  function toggle(id) {
    const items = load().map(function (i) {
      if (i.id === id) i.done = !i.done;
      return i;
    });
    save(items);
    render();
  }

  function remove(id) {
    save(load().filter(function (i) { return i.id !== id; }));
    render();
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    add(input.value);
    input.value = "";
    input.focus();
  });

  render();
})();
