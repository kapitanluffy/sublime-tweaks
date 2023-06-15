import sublime
import sublime_plugin
from .utils import is_setting_enabled, get_all_sheets

class TweaksAddToSelectionCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        return len(self.window.sheets()) > 1 and is_setting_enabled('add_to_selection')

    def run(self):
        sheets = get_all_sheets(self.window)
        selected_sheets = self.window.selected_sheets()
        active_sheet = self.window.active_sheet()
        items = []
        target_sheets = []

        for v in sheets:
            if v not in selected_sheets:
                view = v.view()
                view_name = view.name() if view is not None else None
                name = v.file_name() or view_name or "Untitled Sheet #%s" % (v.id())
                items.append(sublime.QuickPanelItem(trigger=name))
                target_sheets.append(v)

        print(selected_sheets, active_sheet)

        self.window.show_quick_panel(
            items=items,
            on_select=lambda index: self.on_select_view(index, target_sheets, active_sheet, selected_sheets),
            on_highlight=lambda index: self.on_highlight(index, target_sheets),
            placeholder="Select a file to diff against.."
        )

    def on_highlight(self, index, sheets):
        self.window.focus_view(sheets[index].view())

    def on_select_view(self, index, all_views, focused_view, selected_sheets):
        if index < -1 or index == -1:
            self.window.focus_view(focused_view.view())
            return

        selected_views = all_views[index]
        views_to_select = [focused_view, selected_views] + selected_sheets
        print(all_views, selected_views)
        print(focused_view, selected_sheets)
        print(views_to_select)

        # Select the views.
        self.window.focus_group(self.window.active_group())
        self.window.focus_view(focused_view.view())
        self.window.select_sheets(views_to_select)
