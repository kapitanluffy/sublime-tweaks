import sublime
import sublime_plugin

class TweaksReverseCharactersCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if region.empty():
                continue
            original_text = self.view.substr(region)
            reversed_text = original_text[::-1]
            self.view.replace(edit, region, reversed_text)
