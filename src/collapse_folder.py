import sublime
import sublime_plugin
from .utils import is_setting_enabled, collapse_folder, get_expanded_folders, get_project_data

class TweaksCollapseFolderCommand(sublime_plugin.WindowCommand):
    def is_enabled(self) -> bool:
        return is_setting_enabled('expand_sidebar_folder')

    def run(self):
        expanded_folders = get_expanded_folders()
        project_data = get_project_data(self.window)
        folders = []

        for i,v in enumerate(expanded_folders):
            for f in project_data['folders']:
                if f['path'] == v:
                    folders.append(v)

        self.window.show_quick_panel(folders, lambda index: self.on_done(index, folders))

    def on_done(self, index, folders):
        if index < 0:
            return

        sublime.set_timeout_async(lambda: collapse_folder(self.window, folders[index]))


