import sublime
import sublime_plugin

class GetLocationCurrentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        file_name = self.view.file_name() or "Untitled"
        cursor_pos = self.view.sel()[0].begin()
        row, col = self.view.rowcol(cursor_pos)
        sublime.set_clipboard(f"{file_name}:{row + 1}:{col + 1}")
