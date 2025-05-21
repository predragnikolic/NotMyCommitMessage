from __future__ import annotations
from typing import Iterator, Literal
import sublime_plugin 
import sublime
import json
import threading

from .core.git_commands import Git
from .core.activity_indicator import ActivityIndicator
import requests


# Event to signal stopping the stream
stop_event = threading.Event()


class Ollama:
    url= "http://localhost:11434"
    model="qwen2.5-coder"
    is_installed= False


class IsOllamaInstalled(sublime_plugin.EventListener):
    def on_init(self, views):
        v = sublime.active_window().active_view()
        if not v:
            return
        ollama_settings: dict = v.settings().get("nmcm.ollama", {})
        Ollama.url = ollama_settings.get('url', "http://localhost:11434")
        Ollama.model = ollama_settings.get('model', '')
        res = requests.get(Ollama.url)
        if res.status_code != 200:
            print(f'NotMyCommitMessage: Ollama is not running on {Ollama.url}.')
            return
        print(f'NotMyCommitMessage: Ollama is running on {Ollama.url}.')
        # list models available locally
        res = requests.get(f"{Ollama.url}/api/tags")

        def strip_after_colon(input_string: str):
            """
             ['deepseek-r1:7b', 'qwen2.5-coder:latest', 'phi3.5:3.8b-mini-instruct-q8_0']
             ->
             ['deepseek-r1', 'qwen2.5-coder', 'phi3.5']
            """
            colon_index = input_string.find(':')
            if colon_index != -1:
                return input_string[:colon_index]
            else:
                return input_string

        available_models = [strip_after_colon(model['name']) for model in res.json()['models']]
        if Ollama.model not in available_models:
            print(f'NotMyCommitMessage: Model "{Ollama.model}" not found.\n\tUse one of the available models: {available_models}\n\tand set it in Preferences.sublime-settings: `"nmcm.ollama": {{ "model": "MODEL" }}`')
            return
        print(f'NotMyCommitMessage: Model "{Ollama.model} is used."')
        Ollama.is_installed = True


class NmcmCancelGenerateMessage(sublime_plugin.TextCommand):
    def run(self, edit):
        global stop_event
        # If a previous request is running, stop it
        if not stop_event.is_set():
            stop_event.set()


LAST_GENERATED_TEXT = ''


class NmcmGenerateMessageCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global stop_event, LAST_GENERATED_TEXT
        w = self.view.window()
        if not w:
            return
        git = Git(w)
        staged_diff = git.diff_staged() or git.diff_all_changes()
        added_files = git.diff_staged_file_names_by_filter('A')
        deleted_files = git.diff_staged_file_names_by_filter('D')
        renamed_files = git.diff_staged_file_names_by_filter('R')
        user_prompt = self.view.settings().get("nmcm.commit_message_prompt") or "Generate a short, concise and correct git commit message."
        prompt = f"""{user_prompt}
Added files:
{added_files or "/"}

Deleted files:
{deleted_files or '/'}

Renamed files:
{renamed_files or '/'}

Git diff of changed files is:
{staged_diff}
"""
        # If a previous request is running, stop it
        if not stop_event.is_set():
            stop_event.set()
        text_region = self.view.find(LAST_GENERATED_TEXT, 0, flags=sublime.FindFlags.LITERAL)
        if text_region:
            self.view.replace(edit, text_region, '')
        stop_event=threading.Event()
        t = threading.Thread(target=stream_response, args=(self.view, prompt, stop_event))
        t.start()

def stream_response(view:sublime.View, prompt: str, stop_event: threading.Event):
    global LAST_GENERATED_TEXT
    payload = {
        "model": Ollama.model,
        "prompt": prompt,
        "stream": True,
    }
    w = view.window()
    if not w:
        return
    try:
        LAST_GENERATED_TEXT = ''
        last_point = view.find_by_class(get_point(view) or 0, False, sublime.PointClassification.LINE_START)
        with ActivityIndicator(w, f'Generating commit message'):
            for text_chunk in stream('post', f"{Ollama.url}/api/generate", payload, stop_event):
                LAST_GENERATED_TEXT+=text_chunk
                view.run_command("nmcm_insert_text", {
                    'characters': text_chunk,
                    'last_point': last_point,
                })
                last_point += len(text_chunk)
    except requests.exceptions.RequestException as e:
        w.status_message(f'Generating commit message FAILED')
        return


class NmcmInsertTextCommand(sublime_plugin.TextCommand):
    def run(self, edit, characters: str, last_point: int):
        self.view.insert(edit, last_point, characters)


def stream(method: Literal['get', 'post'], url: str, data: dict, stop_event: threading.Event | None=None) -> Iterator[str]:
    headers = {"Content-Type": "application/json"}
    with requests.request(method, url, json=data, headers=headers, stream=True, timeout=10) as response:
        response.raise_for_status()
        for chunk in response.iter_lines():
            if stop_event and stop_event.is_set():
                return
            if chunk:
                try:
                    chunk_text = chunk.decode("utf-8")
                    chunk_json = json.loads(chunk_text)
                    text = chunk_json.get("response", "")  # Extract the text
                    yield text
                except json.JSONDecodeError:
                    print("Failed to decode JSON chunk:", chunk)
                    return


def get_point(view: sublime.View) -> int | None:
    sel = view.sel()
    if not sel:
        return None
    return sel[0].b
