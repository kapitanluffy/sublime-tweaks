import os
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

        window_variables = self.window.extract_variables()
        project_path = window_variables["project_path"]

        for i,v in enumerate(expanded_folders):
            for f in project_data['folders']:
                project_folder_path = f['path']
                if not os.path.isabs(project_folder_path):
                    project_folder_path = os.path.abspath(os.path.join(project_path, project_folder_path))
                if project_folder_path == v:
                    folders.append(f['path'])

        self.window.show_quick_panel(folders, lambda index: self.on_done(index, folders))

    def on_done(self, index, folders):
        if index < 0:
            return

        sublime.set_timeout_async(lambda: collapse_folder(self.window, folders[index]))


