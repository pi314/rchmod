from __future__ import print_function
import argparse
import sys
import os

file_rules = [
        (755, r'^.*\.sh$'),
        (755, r'^.*\.exe$'),
        (644, r'^.*$'),
    ]
dir_rules = [
        ('h', 'ign', r'^.*\.git$'),
        ('d', 'ign', r'^.*\.git$'),
        ('d',  755 , r'^.*$'),
    ]

def gen_item_list (rootdir):
    result = []
    for i in os.walk(rootdir):
        result.append( ('d', oct(os.lstat(i[0]).st_mode & 0777)[1:], i[0]) )
        if i[2] != []:
            for f in i[2]:
                result.append(
                    (   'f',
                        oct(os.lstat(i[0]+'/'+f).st_mode & 0777)[1:],
                        i[0] + '/' + f)
                    )
    return result
    
def test (rootdir):
    item_list = gen_item_list(rootdir)
    for i in item_list:
        print(i)
    print(len(item_list))

def show_rules ():
    global file_rules
    global dir_rules

    print('File rules:')
    for i in file_rules:
        print(i[0], 'for', i[1])

    print('')

    print('Directory rules:')
    for i in dir_rules:
        if i[1] == 'ign':
            action_str = 'ignore'
        else:
            action_str = '{}   '.format(i[1])

        if i[0] == 'h':
            has_str = 'which has    '
        else:
            has_str = 'which matches'

        print(action_str, has_str, i[2])

    print('')

    print('Rule file format:')

    for i in file_rules:
        print( 'f {} {}'.format(i[0], i[1]) )

    for i in dir_rules:
        print( '{} {} {}'.format(i[0], i[1], i[2]) )
        

def main ():
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

    parser.add_argument('--no-prograss',
                        help="Don't calculate total item amount",
                        action='store_true')

    args = parser.parse_args()

    print(sys.argv)
    print(args)
    print('rootdir:',     args.rootdir)
    print('rule:',        args.rule)
    print('show_rules:',  args.show_rules)
    print('interact:',    args.interact)
    print('test:',        args.test)
    print('no_prograss:', args.no_prograss)
    print('')

    if args.test:
        test(args.test)
    elif args.show_rules:
        show_rules()
        exit()

if __name__ == '__main__':
    main()
