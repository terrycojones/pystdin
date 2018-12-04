# Wrapping command-line Python in a loop over standard input

The `pystdin.py` script in this repo can be used to quickly run Python code
on standard input.  This is inspired by perl's `-p` and `-a` options and
the `BEGIN` and `END` blocks of awk (and perl).

Runs on (at least) Python 2.7.15 and 3.6 (and probably all versions of
Python 3).

## Installation

```sh
$ pip install pystdin
```

## Trivial examples

```sh
# Emulate cat.
$ pystdin.py -e 'print(line)'

# Print the third field.
$ pystdin.py -e 'print(F[2])'

# Print the third field, or the whole line if an IndexError occurs.
$ pystdin.py -e 'print(F[2])' --indexError print

# Change the second field to '*'.
$ pystdin.py -e 'F[1] = "*"'

# Add the first fields and print their sum.
$ pystdin.py --begin 'x = 0' -e 'x += int(F[0])' --end 'print(x)' --noPrint

# Print the first 5 fields, leaving out lines with fewer fields.
$ pystdin.py -e 'F = F[:5]'
```

### Command arguments

Multiple command arguments may be given to `--loop` (aka `-e`), `--begin`,
and `--end`.


Use `+` and `-` as arguments to manually increase or decrease indentation
(but see below for indentation detection).


### Dry run

Use `-n` (or `--dryRun`) to not run the code, just print what would be
run. E.g.,

```sh
$ pystdin.py -n -e 'F = F[:5]'
import sys

# No initial code.

for line in sys.stdin:
    line = line.rstrip('\r\n')
    F = line.split(None, -1)
    try:
        F = F[:5]
    except IndexError:
        raise
    print(' '.join(F))

# No final code.
```

### Splitting input lines

Use `--splitStr` to set the string that fields are split with at the start
of the loop.

### Joining the output fields

Use `--joinStr` to set the string that fields are joined with before
printing. E.g.:

```sh
# Split the first two fields on whitespace, print them TAB-separated.
$ pystdin.py -n --joinStr "'\\t'" -e 'F = F[:2]'
import sys

# No initial code.

for line in sys.stdin:
    line = line.rstrip('\r\n')
    F = line.split(None, -1)
    try:
        F = F[:2]
    except IndexError:
        raise
    print('\t'.join(F))

# No final code.
```

Or equivalently:

```sh
# Split the first two fields on whitespace, print them TAB-separated.
$ pystdin.py --joinStr "'\\t'" -e 'print(F[:2])' --noPrint
```

## Indentation detection

If an argument ends in `:` the following Python code will be indented by
one level (use `--noAutoIndent` to disable this).  So these two are
equivalent:

```sh
$ pystdin.py -e 'if F[0] == "x":' 'print(F[1])'
$ pystdin.py -e --noAutoIndent 'if F[0] == "x":' + 'print(F[1])'
```

As mentioned above you can also use `+` and `-` as commands to manually
increase or decrease indentation:

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
    print(' '.join(F))

# No final code.
```

A more complex example of indentation being taken care of:

```sh
$ pystdin.py -n -e try: 'x = int(F[0])' 'except ValueError:' \
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

Of course by that stage you might just want to write a Python script
instead of using the command line.

## Full usage

```
usage: pystdin.py [-h] [--loop STATEMENT [STATEMENT ...]]
                  [--begin [STATEMENT [STATEMENT ...]]]
                  [--end [STATEMENT [STATEMENT ...]]]
                  [--lineVar VARIABLE-NAME] [--splitVar VARIABLE-NAME]
                  [--joinStr STRING] [--indexError {pass,raise,print}]
                  [--splitStr STRING] [--maxSplit N] [--dryRun] [--noPrint]
                  [--noChomp] [--noSplit] [--noAutoIndent] [--indent N]

Wrap Python in a loop over on stdin.

optional arguments:
  -h, --help            show this help message and exit
  --loop STATEMENT [STATEMENT ...], -e STATEMENT [STATEMENT ...]
                        Python commands to run on each input line. (default:
                        None)
  --begin [STATEMENT [STATEMENT ...]]
                        Python commands to run before looping over stdin.
                        (default: None)
  --end [STATEMENT [STATEMENT ...]]
                        Python commands to run after looping over stdin.
                        (default: None)
  --lineVar VARIABLE-NAME
                        The name of the variable to read input lines into.
                        (default: line)
  --splitVar VARIABLE-NAME
                        The name of the variable to split input lines into
                        (ignored if --noSplit is used) (default: F)
  --joinStr STRING      The string to join fields on before printing at the
                        end of the loop (ignored if --noPrint is used).
                        (default: ' ')
  --indexError {pass,raise,print}
                        What to do if the processing of a line results in an
                        IndexError. (default: raise)
  --splitStr STRING     The string to split lines on (default is whitespace)
                        (ignored if --noSplit is used). (default: None)
  --maxSplit N          The maximum number of fields to split (ignored if
                        --noSplit is used). (default: -1)
  --dryRun, -n          Print the code that would be run, without running it.
                        (default: False)
  --noPrint             Do not print the re-joined (by the --joinString
                        string) split input after processing each line.
                        (default: False)
  --noChomp             Do not remove the final character (typically a
                        newline) from each input line. (default: False)
  --noSplit             Do not split input lines on whitespace. Implies
                        --noPrint. (default: False)
  --noAutoIndent        Do not automatically indent code following commands
                        ending in a colon. (default: False)
  --indent N            The number of spaces of indentation to use. (default:
                        4)
```
