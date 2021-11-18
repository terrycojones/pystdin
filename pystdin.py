#!/usr/bin/env python

import argparse
import re

elifExceptRegex = re.compile(r'''
    ^(
       elif\s.* | except(\s.*)?
     ):$
''', re.VERBOSE)

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description=('Wrap Python in a loop over on stdin.'))

parser.add_argument(
    '--loop', '-e', metavar='STATEMENT', nargs='+',
    help='Python commands to run on each input line.')

parser.add_argument(
    '--begin', metavar='STATEMENT', nargs='*',
    help='Python commands to run before looping over stdin.')

parser.add_argument(
    '--end', metavar='STATEMENT', nargs='*',
    help='Python commands to run after looping over stdin.')

parser.add_argument(
    '--lineVar', metavar='VARIABLE-NAME', default='line',
    help='The name of the variable to read input lines into.')

parser.add_argument(
    '--splitVar', metavar='VARIABLE-NAME', default='F',
    help=('The name of the variable to split input lines into (ignored '
          'if --noSplit is used)'))

parser.add_argument(
    '--joinStr', '-j', metavar='STRING',
    help=('The string to join fields on before printing at the end of the '
          'loop (ignored if --print is not used).'))

parser.add_argument(
    '--indexError', default='raise',
    choices=('pass', 'raise', 'print'),
    help=('What to do if the processing of a line results in an '
          'IndexError.'))

parser.add_argument(
    '--splitStr', metavar='STRING',
    help=('The string to split lines on (default is whitespace) (ignored if '
          '--noSplit is used).'))

parser.add_argument(
    '--maxSplit', default=-1, type=int, metavar='N',
    help=('The maximum number of fields to split (ignored if --noSplit '
          'is used).'))

parser.add_argument(
    '--dryRun', '-n', action='store_true',
    help='Print the code that would be run, without running it.')

parser.add_argument(
    '--print', '-p', action='store_true',
    help=('Print the re-joined (using the --joinString string) '
          'split input after processing each line.'))

parser.add_argument(
    '--tabs', '-t', action='store_true',
    help='Make the default separator and joining string be a TAB.')

parser.add_argument(
    '--noChomp', action='store_true',
    help=('Do not remove the final character (typically a newline) '
          'from each input line.'))

parser.add_argument(
    '--noSplit', '--ns', action='store_true',
    help='Do not split input lines on whitespace.')

parser.add_argument(
    '--noAutoIndent', action='store_true',
    help=('Do not automatically indent code following commands ending in '
          'a colon.'))

parser.add_argument(
    '--indent', default=4, type=int, metavar='N',
    help='The number of spaces of indentation to use.')

args = parser.parse_args()

indentStr = ' ' * args.indent


def makeCode(commands, indentInc, initialIndent=0):
    indent = initialIndent
    commandCode = []
    for command in commands or []:
        command = command.strip()
        if command == '+':
            indent += indentInc
        elif command == '-':
            if indent == initialIndent:
                raise SyntaxError('Cannot unindent for command %r' %
                                  command)
            else:
                indent -= indentInc
        else:
            if not args.noAutoIndent and (
                    command == 'else:' or elifExceptRegex.match(command)):
                if indent == initialIndent:
                    raise SyntaxError('Cannot unindent for command %r' %
                                      command)
                commandCode.append('%s%s' %
                                   (' ' * (indent - indentInc), command))
            else:
                commandCode.append('%s%s' % (' ' * indent, command))

                if not args.noAutoIndent and command.endswith(':'):
                    indent += indentInc

    return '\n'.join(commandCode)


initialCode = makeCode(args.begin, args.indent) or '# No initial code.'
loopCode = makeCode(args.loop or ['# No loop code.'], args.indent,
                    args.indent * (1 if args.indexError == 'raise' else 2))
endCode = makeCode(args.end, args.indent) or '# No final code.'

if args.joinStr is None:
    joinStr = "'\\t'" if args.tabs else "' '"
else:
    joinStr = args.joinStr

if args.splitStr is None:
    splitStr = "'\\t'" if args.tabs else None
else:
    splitStr = args.splitStr

if args.print:
    if args.noSplit:
        if args.noChomp:
            print_ = '%sprint(%s, end="")' % (indentStr, args.lineVar)
        else:
            print_ = '%sprint(%s)' % (indentStr, args.lineVar)
    else:
        print_ = '%sprint(%s.join(map(str, %s)))' % (
            indentStr, joinStr, args.splitVar)
else:
    print_ = '%s# No print.' % indentStr

split = '%s# No split.' % indentStr if args.noSplit else (
    '%s%s = %s.split(%s, %s)' %
    (indentStr, args.splitVar, args.lineVar, splitStr, args.maxSplit))

chomp = '%s# No chomp.' % indentStr if args.noChomp else (
    "%s%s = %s.rstrip('\\r\\n')" %
    (indentStr, args.lineVar, args.lineVar))

indexError = ('print(%s)' % args.lineVar
              if args.indexError == 'print' else args.indexError)

if args.indexError == 'raise':
    template = '''\
import sys

%(initialCode)s

for %(var)s in sys.stdin:
%(chomp)s
%(split)s
%(loopCode)s
%(print)s

%(endCode)s
'''

else:
    template = '''\
import sys

%(initialCode)s

for %(var)s in sys.stdin:
%(chomp)s
%(split)s
%(in)stry:
%(loopCode)s
%(in)sexcept IndexError:
%(in)s%(in)s%(indexError)s
%(print)s

%(endCode)s
'''

code = template % {
    'initialCode': initialCode,
    'var': args.lineVar,
    'chomp': chomp,
    'split': split,
    'in': indentStr,
    'loopCode': loopCode,
    'indexError': indexError,
    'print': print_,
    'endCode': endCode,
}


if args.dryRun:
    print(code, end='')
else:
    try:
        cc = compile(code, '<stdin>', 'exec')
    except SyntaxError:
        import sys
        print('Could not compile generated code:\n%s' % code,
              file=sys.stderr)
        raise
    else:
        exec(cc)
