#!/usr/bin/env python
"""
Convert cable HTML files to plain text.
written by henrycase <henrycase@hush.com>
with minor tweaks by wally <wally@hush.ai>

public domain software to more usefully interact with public domain secrets.

a mirror of the cables can be found on thepiratebay.

if wikileaks is a terrorist organisation, why is an administration that leaked
a CIA operative's identity out of spite not a terrorist organisation?
"""

import getopt
import os
import re
import sys
from BeautifulSoup import BeautifulSoup

body_re     = '<code><pre>(.+)</pre></code>'    # match body of cable
link_re     = '(?:<a .+>(.+?)</a>)'  
                                                # scrub links in body text
base_re     = '.*cable%s(.+%s+.+%s)(.+)\\.html' % (os.sep, os.sep, os.sep)
                                                # used to keep the organisation
                                                # of the input dir
indir_re    = '^.*cable(%s|$)' % os.sep         # check output_dir sanity
file_re     = '^.+%s(.+)\\.html' % os.sep       # re.sub(file_re, '\\1.txt', fn)
newline_re  = '&#x000A;'                        # html newline
pilcrow_re  = u'\u00B6'                         # unicode for pilcrow character
err         = sys.stderr.write                  # simple error writing function
split       = 80

def process_dir(input_dir, output_dir):
    """
    walks through a directory, looking for html files. when it finds them, it
    runs them through the HTML processing code.
    
    returns number of cables processed.
    """
    cable_count         = 0
    
    # need a valid cable directory. if you customised or renamed files this
    # will be necessary.
    if not re.match(indir_re, input_dir):
        err('invalid path to cables top level directory, ')
        err('looking for directory \'cable\'\n')
        return cable_count
    
    # if the right directory is entered, make sure it actually exists
    if not os.access(input_dir, os.F_OK):
        err('the directory %s does not exist\n' % input_dir)
        return cable_count
    
    # let's get to it already, shall we?
    tree                = os.walk(input_dir)
    while True:
        try:
            (path, dirs, files) = tree.next()
        except StopIteration:
            print "finished!\n"
            break
        else:
            for file in files:
                filename = "%s/%s" % (path, file)
                if process_cable(filename, output_dir):
                    cable_count += 1

    return cable_count


def process_cable(filename, output_dir):
    # if the cable can't be opened, abort
    # using try-except so script will work in python-2.5
    try:
        f = open(filename)
    except:
        err('error opening %s!\n' % filename)
        sys.exit(1)

    page = f.read()
    f.close()
    
    # if an output directory has been specified, we need to change the filename
    # to reflect this for writing, as well as change the extension to properly
    # match the new format.
    save_sub    = str(output_dir) + '\\1'
    save_sub    = re.sub(base_re, save_sub, filename)
    
    if not os.access(save_sub, os.F_OK):
        try:
            os.makedirs(save_sub, 0700)
        except OSError:
            err('permission error on %s\n' % save_sub)
            raise
            return False
        else:
            if not os.access(save_sub, os.W_OK):
                err('no write permissions on %s!\n' % save_sub)
                return False

    
    filename    = re.sub(file_re, '\\1.txt', filename)
    filename    = save_sub + filename

    # HTML parsing section - this pulls the actual text and headers out of the
    # html files and does some basic processing
    parser      = BeautifulSoup(page)
    header_html = str(parser.findAll('table', { 'class':'cable' }).pop())
    h_parser    = BeautifulSoup(header_html)
    body_list   = re.findall(body_re, page, re.M)
    body        = ''

    # tidy up the body a little
    for line in body_list:
        line    = re.sub(newline_re, '\n', line)
        line    = re.sub(link_re, '\\1', line)
        line    = re.sub(pilcrow_re.encode('utf-8'), '', line)
        body += line
    
    # grab the cable's header section
    h_labels    = [ re.sub('<th>(.+)</th>', '\\1', str(h))
                    for h in h_parser.findAll('th') ]
    h_values    = [ re.sub('<a href=.+>(.+)</a>', '\\1', str(v))
                    for v in h_parser.findAll('a')  ]
    
    # here we go
    print "trying to write ", filename,    
    try:
        f   = open(filename, 'wb+')
    except:
        err('\ncould not open %s for writing!\n' % filename)
        return False
    
    # want to write headers in order
    for i in range(len(h_labels)):
        f.write('%s: %s\n' % (h_labels[i], h_values[i]))
    
    f.write('\n')
    
    # note the option (and default behaviour) of splitting into terminal-
    # readable column widths. 
    if split:
        s = body
        while len(s) > 0:
            fp  = s.rfind(' ', 0, split)
            if not fp == -1:
                f.write( s[:fp] )
                s   = s[fp + 1:]
            else:
                f.write( s )
                s = ''
    else:
        f.write(body)

    print ' ... success!'
    return True
    

def main(input_dir, output_dir):
    # using a main() function because it's easier to type cable2text.main() in
    # the REPL for debugging.
    cable_count = process_dir(input_dir, output_dir)
    print "converted %d cables" % cable_count


def help(error_code = 0):
    # don't panic
    print 'Usage:'
    print sys.argv[0] + ' [-s #] [-h] /path/to/cables /path/to/save'
    print ''
    print 'optional arguments:'
    print '\t\t-h\t\tshow program usage'
    print '\t\t-s #\t\t# will be the column break in the text files'
    print 'for more info, see the README.'
    print ''
    sys.exit(error_code)

if __name__ == '__main__':
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:')
    except getopt.GetoptError:
        help(error_code = 1)
        
    if not len(args) == 2:
        help(error_code = 2)
    
    for opt in opts:
        if opt[0] == '-s':
            split = int(opt[1])
        if opt[0] == '-h':
            help()
        
    
    # args[0] == input directory (path to cables), args[1] is output dir, path
    # to save translated cables into
    # I used input_dir and output_dir in case processing on the directory paths
    # proved to be necessary.
    input_dir   = args[0]
    output_dir  = args[1]
    
    if not output_dir[-1] == '/':
        output_dir += '/'
    
    main(input_dir, output_dir)
    
    
        
# Arise, you have nothing to lose but your barbed wire fences!

