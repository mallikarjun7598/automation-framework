"""End-to-end tests for the To-Do app (localStorage-backed PWA)."""
from __future__ import annotations

import pytest

from .pages.todo_page import TodoPage

pytestmark = pytest.mark.web


@pytest.fixture()
def todo(page, base_url) -> TodoPage:
    tp = TodoPage(page, base_url)
    tp.load()
    # Each test starts with a clean slate: localStorage persists per browser
    # context, so clear it and reload to avoid cross-test leakage.
    page.evaluate("localStorage.clear()")
    tp.load()
    return tp


def test_empty_state_shown_initially(todo: TodoPage) -> None:
    assert todo.is_empty_state_visible()
    assert todo.items().count() == 0


def test_add_task(todo: TodoPage) -> None:
    todo.add("Buy groceries")
    assert todo.item_texts() == ["Buy groceries"]
    assert not todo.is_empty_state_visible()


def test_add_multiple_tasks_and_summary(todo: TodoPage) -> None:
    todo.add("Buy groceries")
    todo.add("Walk the dog")
    todo.add("Pay bills")
    assert todo.item_texts() == ["Buy groceries", "Walk the dog", "Pay bills"]
    assert todo.summary_text() == "3 of 3 remaining"


def test_complete_task_updates_summary(todo: TodoPage) -> None:
    todo.add("Buy groceries")
    todo.add("Walk the dog")
    todo.toggle("Buy groceries")
    assert todo.is_done("Buy groceries")
    assert todo.summary_text() == "1 of 2 remaining"


def test_delete_task(todo: TodoPage) -> None:
    todo.add("Buy groceries")
    todo.add("Walk the dog")
    todo.delete("Buy groceries")
    assert todo.item_texts() == ["Walk the dog"]


def test_delete_last_task_shows_empty_state(todo: TodoPage) -> None:
    todo.add("Only task")
    todo.delete("Only task")
    assert todo.is_empty_state_visible()


def test_tasks_persist_across_reload(todo: TodoPage, page, base_url) -> None:
    todo.add("Persisted task")
    todo.load()  # simulate reload / revisit
    assert todo.item_texts() == ["Persisted task"]


def test_blank_input_is_ignored(todo: TodoPage) -> None:
    todo.add("   ")
    assert todo.items().count() == 0
    assert todo.is_empty_state_visible()
