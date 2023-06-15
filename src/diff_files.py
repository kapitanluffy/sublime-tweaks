import sublime
import sublime_plugin
from .utils import is_setting_enabled, get_all_sheets


class QolDiffFilesCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        return len(self.window.sheets()) > 1 and is_setting_enabled('diff_files')

    def run(self):
        sheets = get_all_sheets(self.window)

        if len(sheets) < 2:
            sublime.error_message("You need to have at least 2 open files to join.")
            return

        active_sheet = self.window.active_sheet()
        items = []

        for v in sheets:
            view = v.view()
            view_name = view.name() if view is not None else None
            name = v.file_name() or view_name or "Untitled Sheet #%s" % (v.id())
            items.append(sublime.QuickPanelItem(trigger=name))

        self.window.show_quick_panel(
            items=items,
            on_select=lambda index: self.on_select_view(index, sheets, active_sheet),
            on_highlight=lambda index: self.on_highlight(index, sheets),
            placeholder="Select a file to diff against.."
        )

    def on_highlight(self, index, sheets):
        self.window.focus_view(sheets[index].view())

    def on_select_view(self, index, all_views, focused_view):
        if index < -1 or index == -1:
            self.window.focus_view(focused_view.view())
            return

        selected_views = all_views[index]
        sheets = self.window.selected_sheets()
        views_to_select = [focused_view, selected_views] + sheets

        # Select the views.
        self.window.focus_group(self.window.active_group())
        self.window.focus_view(focused_view.view())
        self.window.select_sheets(views_to_select)
        self.window.run_command("diff_views", {"group": 0, "index": index})
