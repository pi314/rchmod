from __future__ import print_function
import argparse
import sys
import os
import re

file_rules = [
        ('755', r'^.*\.sh$'),
        ('755', r'^.*\.exe$'),
        ('ign', r'^\..*$'),
        ('644', r'^.*$'),
    ]
dir_rules = [
        ('h', 'ign', r'^\.git$'),
        ('d', 'ign', r'^\.git$'),
        ('d', 'ign', r'^\.ssh$'),
        ('d', 'ign', r'^\..*$'),
        ('d', '755', r'^.*$'),
    ]

def get_dir_action (perm, dir_name, sub_dirs, files):
    for r in dir_rules:
        if r[0] == 'h':
            for sd in sub_dirs:
                if re.match(r[2], sd):
                    return r[1]
        elif r[0] == 'd':
            if re.match(r[2], dir_name):
                return r[1]

def get_file_action (perm, file_name):
    for r in file_rules:
        if re.match(r[1], file_name):
            return r[0]

def ignore_tree (root_dir):
    for dir_name, sd, files in os.walk(root_dir):
        yield ('ign', 'd', '***', dir_name)
        for f in files:
            yield ('ign', 'f', '***', dir_name + '/' + f)

def get_ignore_sub_dirs_list (dir_name, sub_dirs):
    result = []
    for sd in sub_dirs:
        for r in filter(lambda x:x[0]=='d' and x[1]=='ign', dir_rules):
            if re.match(r[2], sd):
                result.append(sd)
                break
    return result

def gen_items (rootdir, verbose=False, trim=True):
    verbose=False
    trim = True
    for dir_name, sub_dirs, files in os.walk(rootdir):
        perm = oct(os.lstat(dir_name).st_mode & 0777)[1:]

        action = get_dir_action(perm, dir_name, sub_dirs, files)

        if action == 'ign':
            if verbose:
                for i in ignore_tree(dir_name):
                    yield i
            del sub_dirs[:]
        else:
            if action != perm or not trim:
                yield (action, 'd', perm, dir_name)

            ign_sub_dir_list = get_ignore_sub_dirs_list(dir_name, sub_dirs)

            if verbose:
                for i in ign_sub_dir_list:
                    for j in ignore_tree(dir_name + '/' + i):
                        yield j

            for i in ign_sub_dir_list:
                sub_dirs.remove(i)

            for f in files:
                file_name = dir_name + '/' + f
                perm = oct(os.lstat(file_name).st_mode & 0777)[1:]
                action = get_file_action(perm, file_name)

                #result.append(
                #    (   action,
                #        'f',
                #        perm,
                #        file_name)
                #    )
                if action != perm or not trim:
                    yield (action, 'f', perm, file_name)
    
def test (rootdir):
    item_list = gen_items(rootdir, verbose=True, trim=False)
    for i in item_list:
        print(i)
    #print(len(item_list))

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
