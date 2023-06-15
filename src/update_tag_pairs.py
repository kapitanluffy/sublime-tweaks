# @source: https://ptb.discord.com/channels/280102180189634562/280157067396775936/1103576275655860255
# @author: https://github.com/predragnikolic

# the code in this file is mostly crappy
from typing import List, Optional, Literal,Tuple
import sublime
import sublime_plugin
import re
from .utils import is_setting_enabled


class TweaksUpdateTagPairsListener(sublime_plugin.TextChangeListener):
    @classmethod
    def is_applicable(cls, buffer: sublime.Buffer) -> bool:
        v = buffer.primary_view()
        is_normal_view = v.element() is None

        # this feature is really laggy, disable in larger files
        return is_setting_enabled('enable_update_tag_pairs') and is_normal_view and v is not None and v.size() < 3963

    def on_text_changed(self, changes: List[sublime.TextChange]):
        if not self.buffer:
            return
        view = self.buffer.primary_view()
        if not view:
            return
        for c in changes:
            sublime.set_timeout(lambda: view.run_command('tweaks_side_update_tag'))


class EL(sublime_plugin.EventListener):
    was_undo = False
    def on_post_text_command(self, view, command_name, args):
        if (command_name == "undo"):
            EL.was_undo = True
            def reset():
                EL.was_undo = False
            sublime.set_timeout(reset)


class TweaksSideUpdateTagCommand(sublime_plugin.TextCommand):
    """ This command is guaranteed to executed when { is pressed """
    def run(self, edit):
        v = self.view
        point = get_cursor_point(v)
        if not point:
            return
        # this feature is really laggy, disable in larger files
        if v.size() > 3963:
            return
        if not is_in_tag(v, point):
            return None
        tags = get_tags(v)
        tag = next(filter(lambda tag: tag.in_tag_name(point), tags), None)
        if not tag:
            return
        if tag.open_and_close_tag_names_are_same():
            return
        if not tag.in_tag_name(point):
            return
        if EL.was_undo:
            sublime.set_timeout(lambda: v.run_command("undo"))
            return
        if tag.end_tag.contains(point):
            new_name = tag.end_tag_name()
            update_region = tag.start_tag_name()
            v.replace(edit, update_region, v.substr(new_name))
        if tag.start_tag.contains(point):
            new_name = tag.start_tag_name()
            update_region = tag.end_tag_name()
            v.replace(edit, update_region, v.substr(new_name))


def get_tags(v):
    regions = v.find_by_selector('meta.tag')
    if not regions:
        return []
    new_regions = []
    for r in regions:
        text = v.substr(r)
        indexes = find(text, r'>')
        if len(indexes) == 1:
            new_regions.append(r)
        elif len(indexes) > 1:
            start = r.begin()
            for i in indexes:
                new_regions.append(sublime.Region(start, r.begin() + i + 1))
                start = r.begin() + i + 1
    tags = []
    open_tags_count = 0
    close_tags_count = 0
    for i, open_tag in enumerate(new_regions):
        type = tag_type(v, open_tag)
        if type == 'close_tag':
            close_tags_count += 1
        if type == 'open_tag':
            open_tags_count += 1
            close_tag = find_closing(v, new_regions[i:])
            if close_tag:
                tags.append(Tag(v, open_tag, close_tag))
                # print('SIDE: matching closing', v.substr(open_tag), v.substr(close_tag))
    if close_tags_count != open_tags_count:
        print('SIDE: something is off') # bail out
        print('SIDE: count', open_tags_count, close_tags_count)
        return []
    return tags


class Tag:
    def __init__(self, v, start_tag, end_tag):
        self.view = v
        self.start_tag = start_tag
        self.end_tag = end_tag

    def contains(self, point):
        return self.start_tag.contains(point) or self.end_tag.contains(point)

    def in_tag_name(self, point):
        return self.start_tag_name().contains(point) or self.end_tag_name().contains(point)

    def start_tag_name(self):
        word_end = self.view.find("(<| |>)", self.start_tag.begin() + 1)
        return sublime.Region(self.start_tag.begin() + 1, word_end.end() - 1)


    def get_name(self, point):
        if self.start_tag_name().contains(point):
            return self.view.substr(self.start_tag_name())
        if self.end_tag_name().contains(point):
            return self.view.substr(self.end_tag_name())
        return ""

    def open_and_close_tag_names_are_same(self):
        return self.view.substr(self.start_tag_name()) == self.view.substr(self.end_tag_name())

    def end_tag_name(self):
        word_end = self.view.find("(<| |>)", self.end_tag.begin() + 2)
        return sublime.Region(self.end_tag.begin() + 2, word_end.end() -1)


def tag_type(v, r):
    tag_text = v.substr(r).replace('\n', '')
    is_jsx = v.match_selector(r.begin(), "meta.jsx")
    if re.search("^<.+/>", tag_text):
        return 'self_closing_tag'
    elif not is_jsx and re.search("^<(area|base|basefont|br|col|embed|frame|hr|img|input|isindex|keygen|link|meta|param|source|track|wbr).+>", tag_text):
        return 'self_closing_tag'
    elif re.search("^</.+\s*>", tag_text):
        return 'close_tag'
    elif re.search("^</\s*>", tag_text):
        return 'close_tag'
    elif re.search("^<!.+>", tag_text):
        return 'doctype_tag'
    elif re.search("^<.+>", tag_text):
        return 'open_tag'
    elif re.search("^<\s*>", tag_text):
        return 'open_tag'
    print('SIDE: oh no', v.substr(r), v.rowcol(r.a))
    return 'oh_no'

def find_closing(v, regions):
    counter = -1
    for r in regions:
        type = tag_type(v, r)
        if type == "open_tag":
            counter += 1
        if type == "close_tag":
            counter -= 1
        if counter == -1: # found closing tag
            return r
    return None


def is_in_tag(v, p):
    return v.match_selector(p, 'meta.tag')


def get_cursor_point(v):
    sel = v.sel()
    if len(sel) == 1: # this functonality only works with one cursor, don't want to deal with multiple cursors
        return sel[0].b
    return None


def find(text, ch):
    return [i for i, ltr in enumerate(text) if ltr == ch and text[i-1] != '=']  # the check for text[i-1] != '=' is to not match '=>'... arrow function in jsx can break autorename
