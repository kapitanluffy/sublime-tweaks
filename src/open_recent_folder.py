import sublime
import sublime_plugin
from .utils import is_setting_enabled, get_project_data, expand_folders, get_expanded_folders

class QolOpenRecentFolderCommand(sublime_plugin.WindowCommand):
    def is_enabled(self) -> bool:
        return is_setting_enabled('open_recent_folder')

    def run(self):
        folder_history = sublime.folder_history()
        project_data = get_project_data(self.window)

        for folder in project_data['folders']:
            folder_history.remove(folder['path'])

        self.window.show_quick_panel(folder_history, lambda index: self.on_done(index, folder_history))

    def on_done(self, index, folders):
        if index < 0:
            return

        folder = folders[index]
        project_data = get_project_data(self.window)
        project_data['folders'].append({ "path": folder })
        self.window.set_project_data(project_data)

        expanded_folders = get_expanded_folders()
        expanded_folders.append(folder)

        sublime.set_timeout(lambda: expand_folders(self.window, expanded_folders), 250)
