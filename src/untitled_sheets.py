import sublime
import sublime_plugin
from .utils import is_setting_enabled


class TweaksUntitledSheetsListener(sublime_plugin.ViewEventListener):
    RESERVED_VIEW_NAMES = ["Find Results"]

    @classmethod
    def is_applicable(cls, settings) -> bool:
        return is_setting_enabled("autoname_untitled_sheets")

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

    def on_load_async(self):
        if self.view.element() is not None:
            return

        if self.view.file_name() is None and self.view.name() not in TweaksUntitledSheetsListener.RESERVED_VIEW_NAMES:
            self.generate_view_name(self.view)

    def on_activated_async(self):
        if self.view.element() is not None:
            return

        if self.view.file_name() is None and self.view.name() not in TweaksUntitledSheetsListener.RESERVED_VIEW_NAMES:
            self.generate_view_name(self.view)

    def on_modified_async(self):
        if self.view.element() is not None:
            return

        if self.view.file_name() is None and self.view.name() not in TweaksUntitledSheetsListener.RESERVED_VIEW_NAMES:
            self.generate_view_name(self.view)
