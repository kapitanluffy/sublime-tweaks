import sublime
import sublime_plugin
from .utils import is_setting_enabled

class QolKeybindContextListener(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        if key == "qol_noop_escape" and operator == sublime.OP_EQUAL and operand is True:
            return is_setting_enabled("prevent_console_when_escape")

        if key == "qol_force_escape" and operator == sublime.OP_EQUAL and operand is True:
            return is_setting_enabled("enable_force_close_panel")

        if key == "qol_pair_backticks" and operator == sublime.OP_EQUAL and operand is True:
            return is_setting_enabled("enable_backtick_pairing")

        if key == "qol_indent_square_brackets" and operator == sublime.OP_EQUAL and operand is True:
            return is_setting_enabled("enable_square_bracket_indent")

        if key == "qol_indent_curved_brackets" and operator == sublime.OP_EQUAL and operand is True:
            return is_setting_enabled("enable_curved_bracket_indent")
