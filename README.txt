cable2text.py
authors: henry case (henrycase@hush.com)
         wally (wally@hush.ai)
license: public domain
written: 2010-12-02

INTRODUCTION
processes the cable sub directory in the cablegate mirror.

dependencies:
    python >= 2.5
    BeautifulSoup (in debian / ubuntu, you can install the package
                   python-beautifulsoup. Using the easy_install utility in
                   the python setuptools, you can easy_install beautifulsoup.)

supported platforms:
    *should* work on any POSIX platform and possibly windows, though I have no
    windows machines to test the code on. Uses the OS separator for portability,
    ex. '/' in *nix and '\' in Windows.


RUNNING THE CODE
In the cablegate site, there is a sub directory called cable. This directory is
organized as cable/$YEAR/$MONTH/$CABLENAME.html. Unfortunately, HTML is
difficult to properly grep though, so I and several others were interested in
getting those HTML files into plain text. This is my solution to the problem.

There are two ways to use this code:
    1. The easiest and most straight-forward method is to run it from the
    command line. There are two options which may be specified on the command
    line:
        -h      display a brief summary of the program / options
        -s n    break columns at most n characters. see the SPLIT section.
    
    It requires two arguments: the path to the cable folder (including cable)
    and the path to save the output to. For example:
    
    $ cable2text ~/wikileaks/CableGate2010-11/cablegate.wikileaks.org/cable \
    ~/wikileaks/cablegate-text
    
    If the output directory does not exist, the software will attempt to create
    it. After the program has run, it will report how many cables it converted.
    In the example above, the cables will be in
    
    ~/wikileaks/cablegate-text/$YEAR/$MONTH/$CABLE.txt
    
    2. Another option is to run it from the REPL (or perhaps import it another
    bit of software). In this case, especially if you are using it from another
    bit of code, you may wish to peek under the hood. There are four main
    functions:
        err = write(...)
            write(str) -> None.  Write string str to file.
        
            Note that due to buffering, flush() or close() may be needed before
            the file on disk reflects the data written.
    
        help(error_code=0)
            Error code is the error code to pass to sys.exit at the end of the
            function.
            
            Prints a brief help message and exits.
    
        main(input_dir, output_dir)
            Runs process_dir(input_dir, output_dir) and reports number of
            cables processed.
    
        process_cable(filename, output_dir)
            When passed the filename and output dir, converts the filename from
            HTML -> plain text and stores in output_dir.
    
        process_dir(input_dir, output_dir)
            Walks through a directory, looking for HTML files. When it finds 
            an HTML file, it passes it to process_cable()
        
            Returns number of cables processed.

    By default, err is set to sys.stderr.write - if you wish to log errors to a
    file, for example, you can point err to another function that behaves like
    write( ).
    
    There is more documentation on specifics in the code. I specifically tried
    to maximize compatibility with python versions as old as 2.5 (though it was
    written in python 2.7) - for example, the code uses try-except-else for file
    I/O instead of with open as f. The decision to go with BeautifulSoup was
    solely to add fault-tolerant HTML processing to the code, something I had no
    desire to write on my own (why reinvent the wheel?).


ABOUT SPLIT
The global variable split sets the column break. This is the _maximum_ length
that a column can be. The split function works on spaces, i.e. words, and breaks
on whole words. Setting split to 0 (modify the code if you are running from the
command line) or set cable2text.split = 0 if using it as a module (i.e. from the
REPL).

UPCOMING FEATURES
For those without a local copy of the cables we're hoping to add a function that 
will grab cables directly off of the net and return the text version. Not only
will this make life a little easier but it will also give us a quick way to
download the cables in a clean format. 
