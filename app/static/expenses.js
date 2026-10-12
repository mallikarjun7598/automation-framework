/* Expense Tracker logic. Like the To-Do app, all state lives in localStorage
   so there is no backend or database to pay for. Amounts are stored in cents
   (integers) to avoid floating-point rounding errors in the running total. */
(function () {
  "use strict";

  const STORAGE_KEY = "expenses.items.v1";
  const form = document.getElementById("expense-form");
  const descInput = document.getElementById("expense-desc");
  const amountInput = document.getElementById("expense-amount");
  const list = document.getElementById("expense-list");
  const empty = document.getElementById("expense-empty");
  const totalEl = document.getElementById("expense-total");
  const errorEl = document.getElementById("expense-error");

  /** @typedef {{id: string, desc: string, cents: number}} Expense */

  /** @returns {Expense[]} */
  function load() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
    } catch {
      return [];
    }
  }

  /** @param {Expense[]} items */
  function save(items) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  }

  function uid() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  }

  function formatMoney(cents) {
    return "$" + (cents / 100).toFixed(2);
  }

  function showError(msg) {
    errorEl.textContent = msg;
    errorEl.style.display = msg ? "block" : "none";
  }

  function render() {
    const items = load();
    list.innerHTML = "";
    let totalCents = 0;

    items.forEach(function (item) {
      totalCents += item.cents;

      const li = document.createElement("li");
      li.className = "list-item";
      li.setAttribute("data-testid", "expense-item");
      li.setAttribute("data-id", item.id);

      const main = document.createElement("div");
      main.className = "item-main";

      const desc = document.createElement("span");
      desc.className = "item-text";
      desc.setAttribute("data-testid", "expense-item-desc");
      desc.textContent = item.desc;

      const amount = document.createElement("span");
      amount.className = "item-amount";
      amount.setAttribute("data-testid", "expense-item-amount");
      amount.textContent = formatMoney(item.cents);

      main.appendChild(desc);
      main.appendChild(amount);

      const del = document.createElement("button");
      del.className = "icon-btn";
      del.setAttribute("data-testid", "expense-delete");
      del.setAttribute("aria-label", "Delete expense");
      del.textContent = "✕";
      del.addEventListener("click", function () {
        remove(item.id);
      });

      li.appendChild(main);
      li.appendChild(del);
      list.appendChild(li);
    });

    totalEl.textContent = formatMoney(totalCents);
    empty.style.display = items.length ? "none" : "block";
  }

  function add(desc, amountStr) {
    showError("");
    const trimmed = desc.trim();
    const amount = parseFloat(amountStr);

    if (!trimmed) {
      showError("Please enter a description.");
      return false;
    }
    if (!amountStr || isNaN(amount) || amount <= 0) {
      showError("Please enter a valid amount greater than 0.");
      return false;
    }

    const cents = Math.round(amount * 100);
    const items = load();
    items.push({ id: uid(), desc: trimmed, cents: cents });
    save(items);
    render();
    return true;
  }

  function remove(id) {
    save(load().filter(function (i) { return i.id !== id; }));
    render();
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (add(descInput.value, amountInput.value)) {
      descInput.value = "";
      amountInput.value = "";
      descInput.focus();
    }
  });

  render();
})();
