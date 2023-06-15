import sublime_plugin
from .utils import is_setting_enabled

class QolRevealInSidebarCommand(sublime_plugin.WindowCommand):
    def is_enabled(self) -> bool:
        return is_setting_enabled('enable_reveal_in_sidebar')

    def run(self):
        self.window.run_command('reveal_in_side_bar')
