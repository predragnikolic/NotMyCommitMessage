from __future__ import annotations
from .ai import Ollama

from .core.git_commands import Git
import sublime
import sublime_plugin
import re


def extract_ticket_id(branch_name: str):
    match = re.search(r"[A-Za-z]+[-_]?\d+", branch_name)
    if match:
        return match.group(0)
    return None


class NmcmListener(sublime_plugin.ViewEventListener):
    def on_query_completions(self, prefix: str, locations: list[int]):
        selectors = self.view.settings().get("nmcm.active_in_selector") or "text.git-commit | git-savvy.make-commit"
        if not self.view.match_selector(0, str(selectors)):
            return
        w = self.view.window()
        items: list[sublime.CompletionValue] = []
        # add ticket id completion item
        if w:
            git = Git(w)
            ticket_id = extract_ticket_id(git.branch_name())
            if ticket_id:
                items.append(sublime.CompletionItem(ticket_id, annotation='NotMyCommitMessage'))
        # add generate message with AI
        if Ollama.is_installed:
            items.append(sublime.CompletionItem.command_completion("Generate Message", "nmcm_generate_message", {}, annotation='NotMyCommitMessage', kind=(sublime.KindId.SNIPPET, "AI", "")))
        cl = sublime.CompletionList()
        cl.set_completions(items, flags=sublime.AutoCompleteFlags.INHIBIT_WORD_COMPLETIONS)
        return cl

    def on_query_context(self, key: str, operator: int, operand, match_all: bool) -> bool | None:
        # You can filter key bindings by the precense of a provider,
        if key == "nmcm.is_active":
            selectors = self.view.settings().get("nmcm.active_in_selector") or "text.git-commit | git-savvy.make-commit"
            return self.view.match_selector(0, str(selectors))


