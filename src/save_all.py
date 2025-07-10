import sublime_plugin

class TweaksSaveAllCommand(sublime_plugin.WindowCommand):
    def run(self):
        [v.run_command("save") for v in self.window.views() if v.file_name()]

