import sublime_plugin
from .utils import is_setting_enabled

class TweaksOpenRecentFileCommand(sublime_plugin.WindowCommand):
    def is_enabled(self) -> bool:
        return is_setting_enabled('open_recent_file')

    def run(self):
        files = self.window.file_history()
        self.window.show_quick_panel(files, lambda index: self.on_done(index, files))

    def on_done(self, index, files):
        if index < 0:
            return

        file = files[index]
        self.window.run_command("open_file", {"file": file})
