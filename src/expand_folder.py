import os
import sublime_plugin
from .utils import is_setting_enabled, get_project_data, expand_folders, get_expanded_folders

class TweaksExpandFolderCommand(sublime_plugin.WindowCommand):
    def is_enabled(self) -> bool:
        return is_setting_enabled('expand_sidebar_folder')

    def run(self):
        expanded_folders = get_expanded_folders()
        project_data = get_project_data(self.window)
        folders = []

        for folder in project_data['folders']:
            if folder['path'] in expanded_folders:
                continue
            folders.append(folder['path'])

        self.window.show_quick_panel(folders, lambda index: self.on_done(index, folders))

    def on_done(self, index, folders):
        if index < 0:
            return

        selected_folder = folders[index]

        if not os.path.isabs(selected_folder):
            window_variables = self.window.extract_variables()
            project_path = window_variables["project_path"]
            selected_folder = os.path.abspath(os.path.join(project_path, selected_folder))

        # @todo rework, conversion to abs should be handled inside
        expand_folders(self.window, [selected_folder])
