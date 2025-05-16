from __future__ import annotations
import subprocess
import sublime

class Git:
    def __init__(self, window: sublime.Window) -> None:
        self.window = window
        self.git_root_dir = None
        self.git_root_dir = str(self.run(['git rev-parse --show-toplevel']).strip())

    def branch_name(self):
        cmd = ['git rev-parse --abbrev-ref HEAD']
        return self.run(cmd).strip()

    def diff(self) -> str:
        cmd = ['git diff --name-only --cached']
        return self.run(cmd)

    def diff_all_changes(self) -> str:
        cmd = ['git diff']
        return self.run(cmd)

    def diff_staged(self) -> str:
        cmd = ['git diff --staged']
        return self.run(cmd)

    def run(self, cmd: list[str]) -> str:
        cwd = self.git_root_dir if self.git_root_dir else self.window.extract_variables()['folder']
        p = subprocess.Popen(cmd,
                             bufsize=-1,
                             cwd=cwd,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             shell=True)
        output, _ = p.communicate()
        if p.returncode == 1:
            decoded_error = output.decode('utf-8')
            print(f'NMCM: An error happened while running this command "{cmd}".', decoded_error)
            raise Exception(f'NMCM: An error happened while running this command "{cmd}". {decoded_error}')
        return output.decode('utf-8')
