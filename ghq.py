import os
import sublime
import sublime_plugin
import subprocess

def get_ghq_repositories():
    settings = sublime.load_settings('GHQ.sublime-settings')
    ghq_command = settings.get('ghq_command')

    stdout = subprocess.check_output([ghq_command, 'list', '--full-path'])
    repos = stdout.decode().rstrip('\n').split('\n')

    stdout = subprocess.check_output([ghq_command, 'root', '--all'])
    roots = stdout.decode().rstrip('\n').split('\n')
    roots.sort(reverse=True)

    home = os.path.join(os.path.expanduser('~'), '')
    def form_repo(path, roots):
        upath = os.path.join('~', os.path.relpath(path, home)) if path.startswith(home) else path

        for root in roots:
            if path.startswith(os.path.join(root, '')):
                return [os.path.relpath(path, root), upath]
        return [upath, upath]

    repos = [form_repo(path, roots) for path in repos]
    return repos


def close_all_views(window):
    window.run_command('close_all')
    return len(window.views()) == 0


def close_workspace(window):
    window.run_command('close_workspace')


def open_repository(window, repository_path):
    if not close_all_views(window):
        return

    close_workspace(window)

    folders = [{ 'path': repository_path }]
    window.set_project_data({ 'folders': folders })


class GhqOpenRepositoryCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            repositories = get_ghq_repositories()

            def on_repository_selected(index):
                if index >= 0:
                    [alias, path] =  repositories[index]
                    open_repository(self.window, os.path.expanduser(path))

            self.window.show_quick_panel(repositories, on_repository_selected)

        except Exception as e:
            sublime.error_message(str(e))
