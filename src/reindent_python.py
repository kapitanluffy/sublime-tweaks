import sublime
import sublime_plugin
import re
from .utils import is_setting_enabled

PYTHON_TAB_SIZE = 4
START_BLOCK = "START_BLOCK"
IN_BLOCK = "IN_BLOCK"
END_BLOCK = "END_BLOCK"
END_BLOCK = "END_BLOCK"

class TweaksReindentPythonCommand(sublime_plugin.TextCommand):
    block_stack = []

    def is_enabled(self):
        return is_setting_enabled('reindent_python')

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
