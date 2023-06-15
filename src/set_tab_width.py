import sublime_plugin
from .utils import is_setting_enabled


class TweaksSetTabWidthCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        return len(self.window.sheets()) > 1 and is_setting_enabled('set_tab_width')

    def run(self):
        self.tab_widths = ['1', '2', '3', '4', '5', '6', '7', '8']
        self.window.show_quick_panel(self.tab_widths, self.on_done)

    def on_done(self, index):
        if index != -1:
            tab_width = self.tab_widths[index]
            self.window.run_command("set_setting",  { "setting": "tab_size", "value": int(tab_width) })
            view = self.window.active_view()

            if view:
                view.run_command("reindent",  { "single_line": False })
