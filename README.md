# NMCM - NotMyCommitMessage

Generate commit messages using [Ollama](https://ollama.com/).


https://github.com/user-attachments/assets/69d2f627-2ca3-4b20-bf32-e4bdf5cd1cbc



### Quick Start

1.  Open the Command Palette and run `Package Control: Install Package` and install `NotMyCommitMessage`.
2.  Install either [Git](https://packagecontrol.io/packages/Git) or [GitSavvy](https://packagecontrol.io/packages/GitSavvy). This enables the `Git: Commit` command in the Command Palette.
3.  Install [Ollama](https://ollama.com/). Once installed, Ollama should be running at `http://localhost:11434`. Open this link in your browser to verify.
4.  Download an Ollama model (e.g. `qwen2.5-coder:7b`) by running:
    ```bash
    ollama run qwen2.5-coder:7b
    ```
    You can find more models on the [Ollama website](https://ollama.com/search).
5.  Open the Command Palette and run `Preferences: Settings`. Add the following to your settings, replacing `"qwen2.5-coder"` with your chosen model:
    ```js
    {
        "nmcm.ollama": {
            "model": "qwen2.5-coder"
        //  "url": "http://localhost:11434"
        }
        // Optional settings:
        // "nmcm.active_in_selector": "text.git-commit | git-savvy.make-commit",
        // "nmcm.commit_message_prompt": "Generate a short, concise and correct git commit message."
    }
    ```

### How to Use

1.  Make your code changes in a Git repository.
2.  Open the Command Palette and stage changes with `Git: Add`.
3.  Open the Command Palette, select `Git: Commit` to open the commit message view.
4.  In the commit message view, trigger autocomplete (`Ctrl+Space` or `Cmd+Space`). You should see `"Generate Message"`.
5.  Select `"Generate Message"` to have NMCM create a commit message for you based on the diff.
6.  To stop the message generation, press `Ctrl+C` (or `Cmd+C` on macOS).

> [!TIP]
> If your Git branch name includes a ticket ID (like `feature/ABC-123`), NMCM will also suggest the ticket ID in the autocomplete.


