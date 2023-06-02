import sublime
import sublime_plugin
import os
import ast
from typing import Dict, Any, cast
from dataclasses import dataclass
import tokenize
import io
import re
from pprint import pprint

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
    settings = sublime.load_settings("QualityOfLife.sublime-settings")
    settings = settings.to_dict()

    return settings[key] is True


class QolRemoveSidebarFolderCommand(sublime_plugin.WindowCommand):
    def is_enabled(self) -> bool:
        return is_setting_enabled('remove_sidebar_folder')

    def run(self):
        folders = self.window.folders()
        self.window.show_quick_panel(folders, lambda index: self.on_done(index, folders))

    def on_done(self, index, folders):
        if index < 0:
            return

        folder = folders[index]
        self.window.run_command("remove_folder", {"dirs": [folder]})


class QolOpenRecentFileCommand(sublime_plugin.WindowCommand):
    def is_enabled(self) -> bool:
        return is_setting_enabled('open_recent_file')

    def run(self):
        files = self.window.file_history()
        self.window.show_quick_panel(files, lambda index: self.on_done(index, files))

    def on_done(self, index, files):
        if index < 0:
            return

        file = files[index]
        self.window.run_command("open_file", {"file": file})


class QolToggleGutterCommand(sublime_plugin.WindowCommand):
    def is_enabled(self) -> bool:
        return is_setting_enabled('toggle_gutter')

    def run(self):
        view = self.window.active_view()

        if view is None:
            return

        settings = view.settings()
        settings.set('gutter', (not settings.get('gutter')))


class QolToggleLineNumbersCommand(sublime_plugin.WindowCommand):
    def is_enabled(self) -> bool:
        return is_setting_enabled('toggle_line_numbers')

    def run(self):
        view = self.window.active_view()

        if view is None:
            return

        settings = view.settings()
        settings.set('line_numbers', (not settings.get('line_numbers')))


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


class QolExpandFolderCommand(sublime_plugin.WindowCommand):
    def is_enabled(self) -> bool:
        return is_setting_enabled('expand_folder')

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

        expand_folders(self.window, [folders[index]])


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


class QolAddToSelectionCommand(sublime_plugin.WindowCommand):
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


class QolSetTabWidthCommand(sublime_plugin.WindowCommand):
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


PYTHON_TAB_SIZE = 4
START_BLOCK = "START_BLOCK"
IN_BLOCK = "IN_BLOCK"
END_BLOCK = "END_BLOCK"
END_BLOCK = "END_BLOCK"

class QolReindentPythonCommand(sublime_plugin.TextCommand):
    block_stack = []

    def replace_line(self, edit, line_no, indent, content):
        replace = "%s%s" % (" " * indent, content.lstrip())
        _line = self.view.line(self.view.text_point(line_no, 0))
        self.view.replace(edit, _line, replace)

    def get_block_type(self, line):
        keywords = {
            'def': 'function',
            'async def': 'function',
            'class': 'class',
            'if': 'condition',
            'elif': 'condition',
            'else': 'condition',
            'while': 'loop',
            'for': 'loop',
            'async for': 'loop',
            'try': 'try_except',
            'except': 'try_except',
            'with': 'with',
            'async with': 'with',
            'import': 'import',
            'from': 'import'
        }

        match = re.match(r'^\s*(?P<keyword>[a-zA-Z]+)\b', line)
        if match is None:
            return None

        keyword = match.group('keyword')

        if keyword not in keywords:
            return None

        return keywords[keyword]

    def fix1(self, edit, key, curr_state, prev_line):
        if curr_state["indent_size"] == 0 and curr_state["block_state"] == END_BLOCK:
            curr_state["indent_size"] = PYTHON_TAB_SIZE
            self.replace_line(edit, key, curr_state["indent_size"], curr_state["content"])
            return True

        return False

    def fix2(self, edit, key, curr_state, prev_line):
        if curr_state["indent_size"] >= prev_line['indent_size'] and prev_line['block_state'] == END_BLOCK:
            curr_state["indent_size"] = (prev_line['indent_size'] - PYTHON_TAB_SIZE)
            self.replace_line(edit, key, curr_state["indent_size"], curr_state["content"])
            return True

        return False

    def fix3(self, edit, key, curr_state, prev_line):
        if curr_state["indent_size"] <= prev_line['indent_size'] and prev_line['block_state'] == START_BLOCK:
            curr_state["indent_size"] = (prev_line['indent_size'] + PYTHON_TAB_SIZE)
            self.replace_line(edit, key, curr_state["indent_size"], curr_state["content"])
            return True

        return False

    def fix4(self, edit, key, curr_state, prev_line):
        if curr_state["indent_size"] > prev_line["indent_size"] and prev_line['block_state'] == IN_BLOCK:
            curr_state["indent_size"] = prev_line['indent_size']
            self.replace_line(edit, key, curr_state["indent_size"], curr_state["content"])
            return True

        return False

    def fix5(self, edit, key, curr_state, prev_line):
        if curr_state["indent_size"] > (prev_line["indent_size"] + PYTHON_TAB_SIZE) and prev_line['block_state'] == START_BLOCK:
            print("fix 5", curr_state["content"], curr_state, prev_line)
            curr_state["indent_size"] = prev_line['indent_size'] + PYTHON_TAB_SIZE
            self.replace_line(edit, key, curr_state["indent_size"], curr_state["content"])
            print(self.get_line_state(key, prev_line))
            return True

        return False

    def get_line_state(self, line_no, prev_line):
        line = self.view.line(self.view.text_point(line_no, 0))

        # remove newlines & empty spaces
        line_str = self.view.substr(line).rstrip("\n ")

        # count indent size
        match = re.match(r'^(\s+)', line_str)
        indent_size = len(match.group(1)) if match is not None else 0

        # check if line start / end
        is_start = self.view.substr(line.end()-1) == ":"
        is_end = re.match(r"^\s*(pass|return|yield|continue|break)", line_str) is not None
        block_type = self.get_block_type(line_str)
        block_state = None
        is_empty = False

        # if line is indented, it means it is inside a block
        if indent_size > 0:
            block_state = IN_BLOCK

        # if line has a "end" keyword, it means it is the end of a block
        if is_end:
            block_state = END_BLOCK

        # if line has a colon, it meants it is the start of a block
        if is_start:
            block_state = START_BLOCK

        # skip if empty line
        if line.size() <= 0:
            is_empty = True

        if block_state == END_BLOCK and len(self.block_stack) > 0:
            self.block_stack.pop()

        # if block_type is None and len(self.block_stack) > 0 and block_state != START_BLOCK:
        #     block_type = self.block_stack[-1]

        state = {
            "indent_size": indent_size,
            "block_state": block_state,
            "is_empty": is_empty,
            "content": line_str,
            "block_type": block_type,
        }

        if block_state == START_BLOCK:
            self.block_stack.append(state)

        return state

    def run(self, edit):
        prev_line = { "block_state": None, "indent_size": 0, "block_type": None, "is_empty": None, "content": None }
        lines = self.view.split_by_newlines(sublime.Region(0, self.view.size()))

        for key,_ in enumerate(lines):
            curr_state = self.get_line_state(key, prev_line)

            if curr_state["is_empty"]:
                continue

            for fix in ['fix1', 'fix2', 'fix3', 'fix4', 'fix5']:
                if getattr(self, fix)(edit, key, curr_state, prev_line) is True:
                    break

            prev_line = curr_state.copy()

            print("<<")


class QolUntitledSheetsListener(sublime_plugin.EventListener):
    RESERVED_VIEW_NAMES = ["Find Results"]

    def get_first_line(self, view: sublime.View):
        for line in view.lines(sublime.Region(0, view.size())):
            if not line.empty():
                return line
        return None

    def generate_view_name(self, view: sublime.View):
        line = self.get_first_line(view)
        name = view.name()

        if name == "":
            name = "Untitled #%s" % view.id()

        if line is None:
            view.set_name(name)
            return

        selection = view.sel()

        if selection.__len__() > 0 and line.contains(selection[0].a) is False:
            return

        name = view.substr(line).strip()
        name = (name[:10] + '..') if len(name) > 10 else name

        view.set_name(name)

    def on_load_async(self, view: sublime.View):
        if view.element() is not None:
            return

        if view.file_name() is None and view.name() not in QolUntitledSheetsListener.RESERVED_VIEW_NAMES:
            self.generate_view_name(view)

    def on_activated_async(self, view: sublime.View):
        if view.element() is not None:
            return

        if view.file_name() is None and view.name() not in QolUntitledSheetsListener.RESERVED_VIEW_NAMES:
            self.generate_view_name(view)

    def on_modified_async(self, view: sublime.View):
        if view.element() is not None:
            return

        if view.file_name() is None and view.name() not in QolUntitledSheetsListener.RESERVED_VIEW_NAMES:
            self.generate_view_name(view)


class QolEventListener(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        if key == "qol_noop_escape" and operator == sublime.OP_EQUAL and operand is True:
            return is_setting_enabled("prevent_console_when_escape")

        if key == "qol_pair_backticks" and operator == sublime.OP_EQUAL and operand is True:
            return is_setting_enabled("enable_backtick_pairing")

        if key == "qol_indent_square_brackets" and operator == sublime.OP_EQUAL and operand is True:
            return is_setting_enabled("enable_square_bracket_indent")

        if key == "qol_indent_curved_brackets" and operator == sublime.OP_EQUAL and operand is True:
            return is_setting_enabled("enable_curved_bracket_indent")

