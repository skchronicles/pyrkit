#!/usr/bin/env bash

# Use python's argparse module in shell scripts
#
# The function `argparse` parses its arguments using
# argparse.ArgumentParser; the parser is defined in the function's
# stdin.
#
# Executing ``argparse.bash`` (as opposed to sourcing it) prints a
# script template.
#
# https://github.com/nhoffman/argparse-bash
# MIT License - Copyright (c) 2015 Noah Hoffman
# 
# Edited: Skyler Kuhn 2021
# Modified to add epilog and to reformat how short, long options
# are displayed in the help section. Metavar should only be displayed
# once in along with the short and long arg of a given option.

argparse(){
    argparser=$(mktemp 2>/dev/null || mktemp -t argparser)
    cat > "$argparser" <<EOF
from __future__ import print_function
import sys
import argparse
import os


def _center_metavar(options, metastr, linelength=80):
    """
    Center to the metavar to a unified position within the help line
    """

    center = linelength/2
    padding = " " * int(center - len(options))

    return "{}{}{}".format(options, padding, metastr)





class OptionsFormatter(argparse.HelpFormatter):
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
                #return '{} {}'.format(', '.join(parts), args_string)
                return _center_metavar(', '.join(parts), args_string)
            return ', '.join(parts)

    def _get_default_metavar_for_optional(self, action):
        return action.dest.upper()



class MyArgumentParser(argparse.ArgumentParser):
    def print_help(self, file=None):
        """Print help and exit with error"""
        super(MyArgumentParser, self).print_help(file=file)
        sys.exit(1)

parser = MyArgumentParser(prog=os.path.basename("$0"), add_help=False, formatter_class=OptionsFormatter,
            description="""$ARGPARSE_DESCRIPTION""", epilog="""$ARGPARSE_EPILOG""")
EOF

    # stdin to this function should contain the parser definition
    cat >> "$argparser"

    cat >> "$argparser" <<EOF
args = parser.parse_args()
for arg in [a for a in dir(args) if not a.startswith('_')]:
    key = arg.upper()
    value = getattr(args, arg, None)

    if isinstance(value, bool) or value is None:
        print('{0}="{1}";'.format(key, 'yes' if value else ''))
    elif isinstance(value, list):
        print('{0}=({1});'.format(key, ' '.join('"{0}"'.format(s) for s in value)))
    else:
        print('{0}="{1}";'.format(key, value))
EOF

    # Define variables corresponding to the options if the args can be
    # parsed without errors; otherwise, print the text of the error
    # message.
    if python "$argparser" "$@" &> /dev/null; then
        eval $(python "$argparser" "$@")
        retval=0
    else
        python "$argparser" "$@"
        retval=1
    fi

    rm "$argparser"
    return $retval
}
