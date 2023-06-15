import sublime_plugin
from .utils import is_setting_enabled

class QolToggleLineNumbersCommand(sublime_plugin.WindowCommand):
    def is_enabled(self) -> bool:
        return is_setting_enabled('toggle_line_numbers')

    def run(self):
        view = self.window.active_view()

        if view is None:
            return

        settings = view.settings()
        settings.set('line_numbers', (not settings.get('line_numbers')))
