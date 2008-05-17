#!/usr/bin/env python

'''
Shoebox console runner

Copyright 2007, 2008 Ricardo Lafuente 
Developed at the Piet Zwart Institute, Rotterdam

This file is part of Shoebox.
'''

import sys
import os
import re

import shoebox

#------------------------------------------------------
# command-line option-parsing functions
# taken from code by Ed Halley (http://halley.cc/code)

def boolify(value):
    '''Take a friendly user input value, and turn it into True or False.'''
    if value in (True, 1, 'y', 'yes', 'on', 'enable'):
        return True
    if value in (None, False, 0, 'n', 'no', 'off', 'disable'):
        return False
    return True

def getopt(arg, tail, opt, default):
    '''Super-lightweight implementation of one --option=value parsing.
    Supports:
        -o       / --option        (returns True if default is a bool)
        -o=value / --option=value  (returns value in same type as default)
        -o value / --option value  (returns value in same type as default)
    Pops values from tail (usually remainder of argv list) only if required.
    '''
    value = None
    o = opt[0]
    opt = opt.lower()
    match = re.match(r"^(-%s|--%s)$" % (o, opt), arg)
    if match:
        if isinstance(default, (bool, type(None))):
            return True
        if not len(tail):
            raise ValueError, 'Option %s needs an argument.'
        value = tail.pop(0)
    else:
        match = re.match(r"^(-%s|--%s)=(.*)$" % (o, opt), arg)
        if match:
            value = match.group(2)
    if value is None:
        return default
    if isinstance(default, bool):
        return boolify(value.lower())
    if isinstance(default, int):
        return int(value)
    if isinstance(default, float):
        return float(value)
    return value

usage_header = """Shoebox console runner

    Usage: python console.py <inputscript> <outputfile> [options]
    Accepted output extensions: svg, ps, pdf, png

    """

def usage(this, options):
    '''Super-lightweight implementation of command-line usage help.
    Does not have anything particularly wordy about the meanings of each
    option and inputfiles.
    '''
    print usage_header
#    print 'usage:', this, '<options>', '<inputfiles>'
    print '    options and (default) values:'
    for option in options:
        print '\t--%-15s\t(%s)' % (option, repr(options[option]))
    sys.exit(1)

def getopts(argv, options):
    '''Super-lightweight implementation of command-line argument parsing.
    Give it the sys.argv list (without the script name), and a dict of
    default values, like:
        options = { 'flag': False,   # -f,--flag,--flag=Yes,-f False
                    'number': 3,     # -n 2, -n=4, --number=6,-n 5
                    'Name': 'Sally', # -N Mary,--name John,--name=Bill
                    }
    Assumes initial letters are unique and --options are lowercase.
    (Especially note the -n/--number and -N/--name examples above.)
    Does no fancy unique-prefix magic to determine useful options.
    Does no list or increment handling for -n=3 -n=4 or +v +v +v.
    Does not indicate any ordering of options received; last value wins.
    Returns list of all non-option arguments in order found, including
    any lone - argument.  Anything after a -- are non-option arguments.
    '''
    others = [ ]
    this = argv.pop(0)
    while argv:
        arg = argv.pop(0)
        if arg == '--':
            others.extend(argv)
            argv[:] = []
        if arg in ('-h', '-?', '--help'):
            usage(this, options)
        elif len(arg) and arg[0] == '-' and arg != '-':
            for opt in options:
                options[opt] = getopt(arg, sys.argv, opt, options[opt])
        else:
            others.append(arg)
    return others


#------------------------------------------------------

default_inputscript = 'shoebox/examples/blocks_neat.py'
default_gtk_inputscript = 'letters.py'
default_outputfile = 'output.png'

if __name__ == '__main__':

    # process CLI options
    options = { 'verbose': False,
                'debug': False,
                
                'gtk': False,
                'socketserver': False,
                'inputscript': default_inputscript,
                'outputfile': default_outputfile,
                }
    this = sys.argv[0]
    files = getopts(sys.argv, options)                
    
    if not options['gtk']:
        # Command line oneshot mode
    
        # check for extraneous options
        if options['socketserver']:
            print 'Socketserver is only available on GTK mode.'
            usage(this, options)
        if not options['inputscript']:
            print 'No input script specified, defaulting to demo...'
            options['inputscript'] = default_inputscript
        if not options['outputfile']:
            print 'No output file specified, defaulting to output.png...'
            options['outputfile'] = default_outputfile
        # start one-shot commandline processing
        box = shoebox.Box(outputfile = options['outputfile'])
        box.run(options['inputscript'])
#        IMAGE OUTPUT NEEDS THIS LINE
        if 'setup' in box.namespace:
            box.setup()
        if 'draw' in box.namespace:
            box.draw()
        box.finish()
    else:
        # GTK frontend
        import sys
        import gtkui
        if options['outputfile'] is not default_outputfile:
            print 'GTK mode does not take an output file argument.'
            usage(this, options)
        if options['inputscript'] == default_inputscript:
            print 'No input script specified, defaulting to GTK demo...'
            win = gtkui.MainWindow(default_gtk_inputscript)
        else:
            win = gtkui.MainWindow(options['inputscript'])
        if options['socketserver']:
            win.server('',7777)
        win.run()
        

