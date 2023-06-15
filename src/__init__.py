from ..quality_of_life import reload

reload("src", [
    "utils",
    "add_to_selection",
    "diff_files",
    # "double_click",
    "expand_folder",
    "collapse_folder",
    "keybind_context",
    "open_recent_file",
    "open_recent_folder",
    "reindent_python",
    "remove_sidebar_folder",
    "set_tab_width",
    "toggle_gutter",
    "toggle_line_numbers",
    "untitled_sheets",
    "update_tag_pairs",
    "reveal_in_sidebar",
    "copy_line_up",
])

from .utils import *
from .add_to_selection import *
from .diff_files import *
from .expand_folder import *
from .collapse_folder import *
from .keybind_context import *
from .open_recent_file import *
from .open_recent_folder import *
from .reindent_python import *
from .remove_sidebar_folder import *
from .set_tab_width import *
from .toggle_gutter import *
from .toggle_line_numbers import *
from .reveal_in_sidebar import *
from .copy_line_up import *
from .untitled_sheets import QolUntitledSheetsListener
from .update_tag_pairs import QolUpdateTagPairsListener, QolSideUpdateTagCommand

__all__ = [
    "get_all_sheets",
    "get_project_data",
    "load_session_file",
    "is_windows_path_standard",
    "convert_path_to_windows",
    "expand_folder",
    "expand_folders",
    "get_expanded_folders",
    "is_setting_enabled",
    "QolAddToSelectionCommand",
    "QolDiffFilesCommand",
    "QolExpandFolderCommand",
    "QolCollapseFolderCommand",
    "QolKeybindContextListener",
    "QolOpenRecentFileCommand",
    "QolOpenRecentFolderCommand",
    "QolReindentPythonCommand",
    "QolRemoveSidebarFolderCommand",
    "QolSetTabWidthCommand",
    "QolToggleGutterCommand",
    "QolToggleLineNumbersCommand",
    "QolUntitledSheetsListener",
    "QolUpdateTagPairsListener",
    "QolSideUpdateTagCommand",
    "QolRevealInSidebarCommand",
    "QolCopyLineUpCommand",
]
