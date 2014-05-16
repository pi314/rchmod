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

rule_format = r'^([fdh]) (\d\d\d|ign) (\^.*\$)$'
rule_matcher = re.compile(rule_format)


def get_dir_action (perm, dir_path, sub_dirs, files):

    # skip symbolic links
    if os.path.islink(dir_path):
        return 'ign'

    for r in dir_rules:
        if r[0] == 'h':
            for sd in sub_dirs:
                if re.match(r[2], sd):
                    return r[1]
        elif r[0] == 'd':
            if re.match(r[2], dir_path.split('/')[-1]):
                return r[1]
    return 'non'

def get_file_action (perm, dir_path, file_name):

    # skip symbolic links
    if os.path.islink(dir_path + '/' + file_name):
        return 'ign'

    for r in file_rules:
        if re.match(r[-1], file_name):
            return r[0]
    return 'non'

def ignore_tree (root_dir):
    for dir_path, sd, files in os.walk(root_dir):
        perm = oct(os.lstat(dir_path).st_mode & 0777)[1:]
        yield ('ign', 'd', perm, dir_path)
        for f in files:
            perm = oct(os.lstat(dir_path+'/'+f).st_mode & 0777)[1:]
            yield ('ign', 'f', perm, dir_path + '/' + f)

def get_ignore_sub_dirs_list (sub_dirs):
    result = []
    for sd in sub_dirs:
        for r in filter(lambda x:x[0]=='d' and x[1]=='ign', dir_rules):
            if re.match(r[2], sd):
                result.append(sd)
                break
    return result

def gen_items (rootdir, verbose=False):
    for dir_path, sub_dirs, files in os.walk(rootdir):
        perm = oct(os.lstat(dir_path).st_mode & 0777)[1:]

        action = get_dir_action(perm, dir_path, sub_dirs, files)

        if action == 'ign' or action == 'non':
            if verbose:
                for i in ignore_tree(dir_path):
                    yield i
            del sub_dirs[:]
        else:
            if action == perm and verbose:
                yield (action, 'd', perm, dir_path)

            ign_sub_dir_list = get_ignore_sub_dirs_list(sub_dirs)

            if verbose:
                for i in ign_sub_dir_list:
                    for j in ignore_tree(dir_path + '/' + i):
                        yield j

            for i in ign_sub_dir_list:
                sub_dirs.remove(i)

            for file_name in files:
                perm = oct(os.lstat(dir_path + '/' + file_name).st_mode & 0777)[1:]
                action = get_file_action(perm, dir_path, file_name)

                output = False

                if (action != 'ign' and action != perm) or verbose:
                    yield (action, 'f', perm, dir_path + '/' + file_name)

def test (rootdir, verbose=True):
    item_list = gen_items(rootdir, verbose)
    if sys.stdout.isatty():
        for i in item_list:
            #(action, 'f', perm, file_name)
            if i[0] == 'ign':
                print( '\033[1;35m[ignore][{}->   ] {}\033[m'.format(i[2], i[3]) )
            elif i[0] == 'non':
                print( '\033[1;35m[unknow][{}->   ] {}\033[m'.format(i[2], i[3]) )
            elif i[0] == i[2]:
                print( '\033[1;30m[ skip ][{}->{}]\033[m {}'.format(i[2], i[0], i[3]) )
            else:
                print( '\033[1;32m[match ][{}->{}]\033[m {}'.format(i[2], i[0], i[3]) )
    else:
        for i in item_list:
            if i[0] == 'ign':
                print( '[ignore][{}->   ] {}'.format(i[2], i[3]) )
            if i[0] == 'non':
                print( '[unknow][{}->   ] {}'.format(i[2], i[3]) )
            elif i[0] == i[2]:
                print( '[ skip ][{}->{}] {}'.format(i[2], i[0], i[3]) )
            else:
                print( '[match ][{}->{}] {}'.format(i[2], i[0], i[3]) )

def clean_permission (rootdir):
    item_list = list( gen_items(rootdir, verbose=False) )
    total_amount = len(item_list)
    #if sys.stdout.isatty():
    for i in item_list:
        print( '\033[1;32m[match ][{}->{}]\033[m {}'.format(i[2], i[0], i[3]) )
    print("Total:", total_amount)

    #(action, 'f', perm, file_name)
    #else:
    #os.chmod( item, int('755', 8) )
    #print(len(item_list))
    pass

def parse_rule_format (line):
    match_result = rule_matcher.match(line)
    if match_result:
        return match_result.group(1), match_result.group(2), match_result.group(3)
    else:
        if line != "" and line[0] != '#':
            print('\033[1;33mRule format incorrect:\033[m', line)
        return None, None, None

def check_and_warn_default_rule (rule_file):
    global file_rules
    global dir_rules
    
    if '^.*$' not in [i[-1] for i in file_rules]:
        print('\033[1;33m=================================================================\033[m')
        print('\033[1;33mFriendly warning:\033[m')
        print('\033[1;33m  Your rule file has no default rule for files like "^.*$".\033[m')
        print('\033[1;33m  There may be files that doesn\'t match any rule.\033[m')
        print('\033[1;33m=================================================================\033[m')
        print('Press enter to continue.')
        raw_input()

    if '^.*$' not in [i[-1] for i in dir_rules]:
        print('\033[1;33m=================================================================\033[m')
        print('\033[1;33mFriendly warning:\033[m')
        print('\033[1;33m  Your rule file has no default rule for directories like "^.*$".\033[m')
        print('\033[1;33m  There may be directories that doesn\'t match any rule.\033[m')
        print('\033[1;33m=================================================================\033[m')
        print('Press enter to continue.')
        raw_input()

def import_rule_file (rule_file):
    global file_rules
    global dir_rules

    file_rules = []
    dir_rules  = []

    print("Parsing rule file:", rule_file)

    with open(rule_file) as rf:
        for line in rf:
            rule_type, rule_action, rule_content = parse_rule_format(line.strip())
            if rule_type == 'f':
                file_rules.append( (rule_action, rule_content) )
            elif rule_type == 'd' or rule_type == 'h':
                dir_rules.append( (rule_type, rule_action, rule_content) )

    check_and_warn_default_rule(rule_file)
    print("Parsing Done.\n")
    show_rules()
    print("")

def gen_rule_zip ():
    global file_rules
    global dir_rules

    file_rules_line = ['File rules:'] +\
        ['{} for {}'.format(i[0], i[-1]) for i in file_rules]

    dir_rules_line  = ['Directory rules:'] +\
        ['{} which {} {}'.format(
            (lambda x: 'ignore' if x=='ign' else x+'   ')(i[1]),
            (lambda x: 'has    ' if x=='h' else 'matches')(i[0]),
            i[-1]) for i in dir_rules]

    file_rules_len = len(file_rules)
    dir_rules_len  = len(dir_rules)

    file_rules_block_width = max([len(i) for i in file_rules_line])
    dir_rules_block_width  = max([len(i) for i in dir_rules_line])

    if file_rules_len >= dir_rules_len:
        dir_rules_line += ['']*(file_rules_len - dir_rules_len)
    else:
        file_rules_line += ['']*(dir_rules_len - file_rules_len)

    file_rules_line = map(lambda x:x.ljust(file_rules_block_width),
        file_rules_line)
    dir_rules_line = map(lambda x:x.ljust(dir_rules_block_width),
        dir_rules_line)

    return file_rules_block_width, dir_rules_block_width, zip(file_rules_line, dir_rules_line)

def show_rules ():
    global file_rules
    global dir_rules

    file_rules_block_width, dir_rules_block_width, block_lines = gen_rule_zip()

    table_top_line = '+' +\
        '-' * (file_rules_block_width + 2) +\
        '+' +\
        '-' * (dir_rules_block_width + 2) +\
        '+'

    print('Current rules:')
    # table top line
    print(table_top_line)

    print( '| ' + block_lines[0][0] + ' | ' + block_lines[0][1] + ' |')

    # table head line
    print(table_top_line)

    for i in block_lines[1:]:
        print('| {} | {} |'.format(i[0], i[1]).replace('^', '\033[1;32m^').replace('$', '$\033[m'))

    # table bottom line
    print(table_top_line)

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

    parser.add_argument('--rule', '--rule-file',
                        help='Import rule file',
                        )

    parser.add_argument('--show-rules',
                        help='Show rules and exit',
                        action='store_true')

    parser.add_argument('--interact',
                        help='Confirm every files and directories',
                        action='store_true')

    parser.add_argument('--list-all',
                        metavar='rootdir',
                        help='List all items and their actions and exit',
                        )

    parser.add_argument('--list-match',
                        metavar='rootdir',
                        help='List matched items and exit',
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
    print('list_all:',    args.list_all)
    print('list_match:',  args.list_match)
    print('no_prograss:', args.no_prograss)
    print('')

    if args.rule:
        import_rule_file(args.rule)

    if args.list_all:
        test(args.list_all, verbose=True)
    elif args.list_match:
        test(args.list_match, verbose=False)
    elif args.show_rules:
        show_rules()
    else:
        if not args.rootdir:
            print('rootdir is needed')
        else:
            clean_permission(args.rootdir)

if __name__ == '__main__':
    main()
