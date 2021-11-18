# Wrapping command-line Python in a loop over standard input

The `pystdin.py` script in this repo can be used to quickly run Python code
on lines of standard input.  This is inspired by perl's `-p` and `-a`
options and the `BEGIN` and `END` blocks of awk (and perl).

Runs on (at least) Python 2.7.15 and 3.6 through 3.9.

## Installation

```sh
$ pip install pystdin
```

## Overview

`pystdin.py` wraps your code into a simple loop that by default looks like
this:

```sh
$ pystdin.py -n
import sys

# No initial code.

for line in sys.stdin:
    line = line.rstrip('\r\n')
    F = line.split(None, -1)
    try:
        pass
    except IndexError:
        raise
    # No print.

# No final code.
```

You can use command line options `--begin`, `--loop` (or `-e`), and `--end`
to insert your own Python code into the initial section, into the loop
(where the `pass` is above), or into the final section, respectively.
Multiple arguments may be given to these options.

You can use `+` and `-` as arguments to easily specify increases or
decreases in the indentation of the generated Python (but see below for
automatic indentation detection).

The `--dryRun` (or `-n`) option used above tells `pystdin.py` to just print
the code that it would run and then exit without running the code.

## Trivial examples

```sh
# Emulate cat (more or less - see below)
$ pystdin.py -p

# Change the second field to '*' and print all fields space-separated.
$ pystdin.py -p -e 'F[1] = "*"'

# Print the first 5 fields of each line.
$ pystdin.py -p -e 'F = F[:5]'

# Print only the third field of each line (see IndexErrors below).
$ pystdin.py -e 'print(F[2])'

# Add the first fields and print their sum.
$ pystdin.py --begin 'x = 0' --loop 'x += int(F[0])' --end 'print(x)'

# Change the second field to 'xxx', using TABs as the separator.
$ pystdin.py --tabs --print --loop 'F[1] == "xxx"'
# Or, equivalently, with short option names:
$ pystdin.py -t -p -e 'F[1] == "xxx"'
```

## Splitting input lines

Use `--splitStr` to set the string that fields are split with at the start
of the loop.  The input lines are split into fields in a variable named `F`
(use `--splitVar` to change this), as in perl.  Use `--noSplit` (or `--ns`)
to turn off auto-splitting. The default is to split on whitespace, as
Python's string `split` function does when passed `None`. Use `--tabs` (or
`-t`) to split on (single) TAB characters. Note that the value you give on
the command line must be a valid Python string, including quotes. So you
should use things like, e.g., `--splitStr '"\t"'` and be aware of how your
shell deals with quotes before it passes the arguments you specify into the
arguments `pystdin.py` receives. If in doubt, use `-n` to examine the
Python that would be executed.

### Index errors

Because it will be common to want to work with automatically split input
lines and because you may not want to check if lines have the required
number of fields for proper processing, you can use `--indexError` to
either `pass` (i.e., ignore) or `print` any offending lines. E.g.:

```sh
# Print only the third field, or the whole line if there are not 3 fields.
$ pystdin.py -e 'print(F[2])' --indexError print

# As above, but skipping lines with fewer fields.
$ pystdin.py -n -e 'print(F[2])' --indexError pass
import sys

# No initial code.

for line in sys.stdin:
    line = line.rstrip('\r\n')
    F = line.split(None, -1)
    try:
        print(F[2])
    except IndexError:
        pass
    # No print.

# No final code.
```

## Automatically printing each line

The `--print` (or `-p`) option enables the automatic printing at the end of
the loop, as in perl.  If line splitting is enabled (the default), the `F`
variable is printed, joined by the value of the `--joinStr` (or `-j`)
option (the default is a single space). If line splitting is turned off
(via `--noSplit` (or `--ns`)), the `line` variable is printed (with a
trailing newline, unless `--noChomp` was used).

### Joining the output fields

When `-p` is used to print lines, you can use `--joinStr` (or `-j`) to set
the string that the fields are joined with. E.g.:

```sh
# Split the first two fields on whitespace, print them TAB-separated.
$ pystdin.py -n -p -j "'\\t'" -e 'F = F[:2]'
import sys

# No initial code.

for line in sys.stdin:
    line = line.rstrip('\r\n')
    F = line.split(None, -1)
    F = F[:2]
    print('\t'.join(F))

# No final code.
```

Or equivalently:

```sh
# Split the first two fields on whitespace, print them TAB-separated.
# Note: no use of -p here as the loop does its own printing.
$ pystdin.py -j "'\\t'" -e 'print(F[:2])'
```

Note that TAB-separated output (and splitting of input) can more easily
requested using `--tabs`.

## Automatic indentation detection

If a command argument ends in a colon, the subsequent Python code will be
indented by one level. The indentation continues until a command like `elif
...:` or `else:` is encountered or until you explicitly unindent using `-`
as an argument.

```sh
# Print the second field if the first is 'x' and then the whole line.
# Notice the manual indentation decrease via -.
$ pystdin.py -n -e 'if F[0] == "x":' 'print(F[1])' - 'print(line)'
import sys

# No initial code.

for line in sys.stdin:
    line = line.rstrip('\r\n')
    F = line.split(None, -1)
    try:
        if F[0] == "x":
            print(F[1])
        print(line)
    except IndexError:
        raise
    # No print.

# No final code.
```

You can use `--noAutoIndent` to disable the auto-indentation, so these two
are equivalent:

```sh
$ pystdin.py -e 'if F[0] == "x":' 'print(F[1])'
$ pystdin.py -e --noAutoIndent 'if F[0] == "x":' + 'print(F[1])'
```

You can use `--indent` to set the number of indentation spaces, if for some
reason you care.

A more complex example of indentation being taken care of:

```sh
$ pystdin.py -n -p -e try: 'x = int(F[0])' 'except ValueError:' \
    'print("Unrecognized line: %r" % line)' continue else: 'if x == 4:' \
    'print("four")' 'elif x > 10:' 'print("big")' else: 'print("unknown")'
import sys

# No initial code.

for line in sys.stdin:
    line = line.rstrip('\r\n')
    F = line.split(None, -1)
    try:
        try:
            x = int(F[0])
        except ValueError:
            print("Unrecognized line: %r" % line)
            continue
        else:
            if x == 4:
                print("four")
            elif x > 10:
                print("big")
            else:
                print("unknown")
    except IndexError:
        raise
    print(' '.join(F))

# No final code.
```

Of course by the stage you get to something that complicated you might just
want to write a Python script instead of using the command line.

## Emulating cat for fun and profit

This is a more accurate emulation of `cat` (just to show you how to turn
off some of the processing):

```sh
$ pystdin.py -n -p --noChomp --noSplit
import sys

# No initial code.

for line in sys.stdin:
    # No chomp.
    # No split.
    # No loop code.
    print(line, end="")

# No final code.
```

## Full usage

```sh
usage: pystdin.py [-h] [--loop STATEMENT [STATEMENT ...]]
                  [--begin [STATEMENT ...]] [--end [STATEMENT ...]]
                  [--lineVar VARIABLE-NAME] [--splitVar VARIABLE-NAME]
                  [--joinStr STRING] [--indexError {pass,raise,print}]
                  [--splitStr STRING] [--maxSplit N] [--dryRun] [--print]
                  [--tabs] [--noChomp] [--noSplit] [--noAutoIndent]
                  [--indent N]

Wrap Python in a loop over on stdin.

optional arguments:
  -h, --help            show this help message and exit
  --loop STATEMENT [STATEMENT ...], -e STATEMENT [STATEMENT ...]
                        Python commands to run on each input line. (default:
                        None)
  --begin [STATEMENT ...]
                        Python commands to run before looping over stdin.
                        (default: None)
  --end [STATEMENT ...]
                        Python commands to run after looping over stdin.
                        (default: None)
  --lineVar VARIABLE-NAME
                        The name of the variable to read input lines into.
                        (default: line)
  --splitVar VARIABLE-NAME
                        The name of the variable to split input lines into
                        (ignored if --noSplit is used) (default: F)
  --joinStr STRING, -j STRING
                        The string to join fields on before printing at the
                        end of the loop (ignored if --print is not used).
                        (default: None)
  --indexError {pass,raise,print}
                        What to do if the processing of a line results in an
                        IndexError. (default: raise)
  --splitStr STRING     The string to split lines on (default is whitespace)
                        (ignored if --noSplit is used). (default: None)
  --maxSplit N          The maximum number of fields to split (ignored if
                        --noSplit is used). (default: -1)
  --dryRun, -n          Print the code that would be run, without running it.
                        (default: False)
  --print, -p           Print the re-joined (using the --joinString string)
                        split input after processing each line. (default:
                        False)
  --tabs, -t            Make the default separator and joining string be a
                        TAB. (default: False)
  --noChomp             Do not remove the final character (typically a
                        newline) from each input line. (default: False)
  --noSplit, --ns       Do not split input lines on whitespace. (default:
                        False)
  --noAutoIndent        Do not automatically indent code following commands
                        ending in a colon. (default: False)
  --indent N            The number of spaces of indentation to use. (default:
                        4)
```
