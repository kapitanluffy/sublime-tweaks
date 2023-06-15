import sys
import imp

def reload(prefix, modules=[""]):
    prefix = "Tweaks.%s." % prefix

    for module in modules:
        module = (prefix + module).rstrip(".")
        if module in sys.modules:
            imp.reload(sys.modules[module])

reload("src")

from .src import *
