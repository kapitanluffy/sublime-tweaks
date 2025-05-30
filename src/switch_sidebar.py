import sublime
import sublime_plugin

def is_sidebar_on_right():
    settings = sublime.load_settings("Preferences.sublime-settings")
    return settings.get("sidebar_on_right", False)

class TweaksSwitchSidebarRightCommand(sublime_plugin.WindowCommand):
    def is_enabled(self) -> bool:
        return is_sidebar_on_right() is False

    def run(self):
        settings = sublime.load_settings("Preferences.sublime-settings")
        settings.set("sidebar_on_right", True)
        sublime.save_settings("Preferences.sublime-settings")

class TweaksSwitchSidebarLeftCommand(sublime_plugin.WindowCommand):
    def is_enabled(self) -> bool:
        return is_sidebar_on_right()

    def run(self):
        settings = sublime.load_settings("Preferences.sublime-settings")
        settings.set("sidebar_on_right", False)
        sublime.save_settings("Preferences.sublime-settings")
