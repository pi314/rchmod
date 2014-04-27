from __future__ import print_function
import argparse
import sys
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('rootdir',
                        help='The root directory of processing',
                        nargs='?')

    parser.add_argument('--rule',
                        help='Import rule file',
                        )

    parser.add_argument('--show-rules',
                        help='Show rules and exit',
                        action='store_true')

    parser.add_argument('--interact',
                        help='Confirm every files and directories',
                        action='store_true')

    parser.add_argument('--test',
                        metavar='rootdir',
                        help='List items match the rule and exit',
                        )

    args = parser.parse_args()

    print('rootdir:',    args.rootdir)
    print('rule:',       args.rule)
    print('show_rules:', args.show_rules)
    print('interact:',   args.interact)
    print('test:',       args.test)

