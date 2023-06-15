import sublime
import sublime_plugin
from .utils import is_setting_enabled

class QolCopyLineUpCommand(sublime_plugin.TextCommand):
    def is_enabled(self) -> bool:
        return is_setting_enabled('enable_copy_line_up')

    def run(self, edit):
        self.view.run_command("duplicate_line")
        sublime.set_timeout_async(lambda: self.view.run_command("jump_back"))
