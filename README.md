# **NMCM** - NotMyCommitMessage

Generate commit messages with [Ollama](https://ollama.com/).

### Getting started

1. Open the command palette and run `Package Control: Install Package` and install `NotMyCommitMessage`.
1. Install [Git](https://packagecontrol.io/packages/Git) or [GitSavvy](https://packagecontrol.io/packages/GitSavvy). After this step, a `Git: Commit` command will be available in the command palette.
1. Install [Ollama](https://ollama.com/). After a successful installation Ollama will be running on `http://localhost:11434`. Open the link an verify that you see "Ollama is running".
1. Download an Ollama [model](https://ollama.com/search) by run `ollama run MODEL_NAME` in the terminal, (for example `ollama run qwen2.5-coder:7b`)
1. Open the command palette and run `Preferences: Settings`, and set the `MODEL_NAME` in the `"nmcm.ollama"`settings (other settings are optional):
```
{
    // The selector where the NMCM will be active.
    // [OPTIONAL] by default supports Git/GitSavvy commit view selectors
    "nmcm.active_in_selector": "text.git-commit | git-savvy.make-commit",

    // configure Ollama
    "nmcm.ollama": {
        // [REQUIRED] - The model name, like `qwen2.5-coder`, `phi3.5`
        "model": "qwen2.5-coder",
        // [OPTIONAL] default to - "http://localhost:11434". The url where Ollama is running
        "url": "http://localhost:11434",
    },

    // [OPTIONAL] default to - "Generate a short, concise and correct git commit message."
    "nmcm.commit_message_prompt": "Generate a short, concise and correct git commit message. Please.",
}
```

Done.

### Usage

1. Make a change in a get repo.
2. Select `Git: Commit` from the command palette.
3. Trigger autocomplete, you should see `"Generate Message"` completion item.
4. Select it and you should see the messege being generated.
5. To stop generating a commit message, press <kbd>primary</kbd> + <kbd>c</kbd>.

> [!TIP]
> If the git branch name contains a ticket id, NMCM will show the TICKET ID in the autocomplete as well.
