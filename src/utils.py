import sublime
from typing import Dict, Any, cast
import os
import re


def get_all_sheets(window: sublime.Window, include_active_sheet=False):
    sheets = window.sheets()
    active_sheet = window.active_sheet()

    if include_active_sheet is False and active_sheet is not None:
        sheets.remove(active_sheet)

    return sheets


def get_project_data(window: sublime.Window):
    project_data = window.project_data()
    project_data = cast(Dict[str, Any], project_data)

    if project_data is None or (isinstance(project_data, Dict) and "folders" not in project_data):
        project_data = { "folders": [] }

    return project_data


def load_session_file():
    session_file = os.path.abspath(os.path.join(sublime.packages_path(), "..", "Local", "Auto Save Session.sublime_session"))
    sfh = open(session_file)
    session_file_contents = sfh.read()
    sfh.close()
    contents = sublime.decode_value(session_file_contents)
    return cast(Dict[str, Any], contents)


def is_windows_path_standard(path):
    # return True if os is not windows
    if sublime.platform() != "windows":
        return True

    match = re.match(r"/[A-Za-z]/", path)
    return match is None


def convert_path_to_windows(path):
    if sublime.platform() != "windows":
        raise Exception("Cannot convert path")

    drv = "%s:" % path[1:2]
    path = path[2:]
    return os.path.normpath(os.path.join(drv, path))


def expand_folder(window: sublime.Window, folder):
    if os.path.exists(folder) is False:
        print("Folder does not exist: %s" % folder)
        return False

    if is_windows_path_standard(folder) is False:
        folder = convert_path_to_windows(folder)

    items = os.listdir(folder)

    if len(items) <= 0:
        print("Cannot expand empty folder: %s" % folder)
        return False

    for item in items:
        item = os.path.join(folder, item)
        if os.path.isfile(item):
            window.open_file(item, flags=sublime.TRANSIENT)
            window.run_command('reveal_in_side_bar')
            return True


def collapse_folder(window: sublime.Window, folder):
    target = None
    folders = get_expanded_folders()
    project_data = get_project_data(window)
    folders.remove(folder)

    for i, f in enumerate(project_data['folders']):
        if f['path'] == folder:
            target = { "index": i, "folder": f }
            break

    if target is None:
        raise Exception("Folder is not in the sidebar")

    project_data['folders'].pop(target['index'])
    window.set_project_data(project_data)

    project_data['folders'].insert(target['index'], target['folder'])
    window.set_project_data(project_data)

    sublime.set_timeout_async(lambda: expand_folders(window, folders))


def expand_folders(window: sublime.Window, folders):
    initial_view = window.active_view()

    if initial_view is None:
        raise Exception("Cannot expand folders without active view")

    for folder in folders:
        if expand_folder(window, folder) is False:
            continue

    window.focus_view(initial_view)


def get_expanded_folders():
    session = load_session_file()
    folders_to_expand = []

    for w in session['windows']:
        if 'expanded_folders' not in w:
            continue

        for folder in w['expanded_folders']:
            if is_windows_path_standard(folder) is False:
                folder = convert_path_to_windows(folder)
            folders_to_expand.append(folder)

    return folders_to_expand


def is_setting_enabled(key):
    settings = sublime.load_settings("Tweaks.sublime-settings")
    settings = settings.to_dict()

    return settings[key] is True
