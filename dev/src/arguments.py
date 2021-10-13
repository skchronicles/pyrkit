# Python standard library
from __future__ import print_function
import sys, os

# 3rd party imports from pypi
import argparse  # potential python3 3rd party package, added in python/3.5


def _center_metavar(options, metastr, linelength=80):
    """
    Centers to the metavar to a unified position within the help line.
    Before:
    -i, --input-directory INPUT_DIRECTORY
                          Brief description of command line option. More details
                          about what this option does and its usage and behavior.
    After:
    -i, --input-directory                   INPUT_DIRECTORY
                          Brief description of command line option. More details
                          about what this option does and its usage and behavior.
    """
    # Find the correct amount of padding based
    # on the length of the line wrapping and 
    # the length of the options flags
    center = linelength/2
    padding = " " * int(center - len(options))
    
    return "{}{}{}".format(options, padding, metastr)


class OptionsFormatter(argparse.RawDescriptionHelpFormatter):
    """
    Reformating how short and long options are displayed in the
    help section. The metavar should only be displayed once along with
    the short and long arg of a given option.
    Before:
        -i INPUT, --input INPUT
    After:
        -i, --input INPUT
    """
    def _format_action_invocation(self, action):
        if not action.option_strings:
            default = self._get_default_metavar_for_positional(action)
            metavar, = self._metavar_formatter(action, default)(1)
            return metavar
        else:
            parts = []
            if action.nargs == 0:
                # Option contains no values or arguments (i.e. boolean flag)
                parts.extend(action.option_strings)
            else:
                # Options with values to be reformatted (-i, --input INPUT)
                default = self._get_default_metavar_for_optional(action)
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append(option_string)
                return _center_metavar(', '.join(parts), args_string)

            return ', '.join(parts)

    def _get_default_metavar_for_optional(self, action):
        return action.dest.upper()
