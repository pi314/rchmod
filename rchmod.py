from __future__ import print_function
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

locked_dirs = []

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
        perm = oct(os.lstat(dir_path).st_mode & 0777).rjust(4, '0')[1:]
        yield ('ign', 'd', perm, dir_path)
        for f in files:
            perm = oct(os.lstat(dir_path+'/'+f).st_mode & 0777).rjust(4, '0')[1:]
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
    global locked_dirs

    for dir_path, sub_dirs, files in os.walk(rootdir):
        perm = oct(os.lstat(dir_path).st_mode & 0777).rjust(4, '0')[1:]

        action = get_dir_action(perm, dir_path, sub_dirs, files)

        if action == 'ign' or action == 'non':
            if verbose:
                for i in ignore_tree(dir_path):
                    yield i
            del sub_dirs[:]
        else:
            if action != perm or (action == perm and verbose):
                yield (action, 'd', perm, dir_path)

            ign_sub_dir_list = get_ignore_sub_dirs_list(sub_dirs)

            if verbose:
                for i in ign_sub_dir_list:
                    for j in ignore_tree(dir_path + '/' + i):
                        yield j

            for i in ign_sub_dir_list:
                sub_dirs.remove(i)

            # may have problem to walk
            for i in sub_dirs:
                perm = oct(os.lstat(dir_path + '/' + i).st_mode & 0777).rjust(4, '0')[1:]
                if re.match(r'^.*[0123].*$', perm):
                    locked_dirs.append(
                        '[{perm}] {itemname}'.format(
                        perm=perm,
                        itemname=dir_path+'/'+i) )

            for file_name in files:
                perm = oct(os.lstat(dir_path + '/' + file_name).st_mode & 0777).rjust(4, '0')[1:]
                action = get_file_action(perm, dir_path, file_name)

                output = False

                if (action != 'ign' and action != perm) or verbose:
                    yield (action, 'f', perm, dir_path + '/' + file_name)

def test (rootdir, verbose=True):
    item_list = gen_items(rootdir, verbose)
    total_amount = 0
    if sys.stdout.isatty():
        for i in item_list:
            #(action, 'f', perm, file_name)
            if i[0] == 'ign':
                print( '\033[1;35m[ignore][{}     ] {}\033[m'.format(i[2], i[3]) )
            elif i[0] == 'non':
                print( '\033[1;35m[unknow][{}     ] {}\033[m'.format(i[2], i[3]) )
            elif i[0] == i[2]:
                print( '\033[1;30m[ skip ][{}->{}]\033[m {}'.format(i[2], i[0], i[3]) )
            else:
                print( '\033[1;32m[match ][{}->{}]\033[m {}'.format(i[2], i[0], i[3]) )
            total_amount += 1
    else:
        for i in item_list:
            if i[0] == 'ign':
                print( '[ignore][{}     ] {}'.format(i[2], i[3]) )
            if i[0] == 'non':
                print( '[unknow][{}     ] {}'.format(i[2], i[3]) )
            elif i[0] == i[2]:
                print( '[ skip ][{}->{}] {}'.format(i[2], i[0], i[3]) )
            else:
                print( '[match ][{}->{}] {}'.format(i[2], i[0], i[3]) )
            total_amount += 1
    print("Total:", total_amount)

def clean_permission (rootdir):
    item_list = list( gen_items(rootdir, verbose=False) )

    total_amount = len(item_list)
    progress_number_width = len(str(total_amount))
    progress_number = 1

    if sys.stdout.isatty():
        for i in item_list:
            print( '\033[1;32m[{progress:4.0%}][{perm}->{action}]\033[m {itemname}'.format(
                progress=float(progress_number)/float(total_amount),
                perm=i[2], action=i[0], itemname=i[3]), end='\r\n')
            os.chmod( i[3], int(i[0], 8) )
            progress_number += 1
        print("Total:", total_amount)
    else:
        for i in item_list:
            print( '[{progress:4.0%}][{perm}->{action}] {itemname}'.format(
                progress=float(progress_number)/float(total_amount),
                perm=i[2], action=i[0], itemname=i[3]), end='\r\n')
            os.chmod( i[3], int(i[0], 8) )
            progress_number += 1
        print("Total:", total_amount)

    if len(locked_dirs) != 0:
        print('\033[1;33m==============================================================\033[m')
        print('\033[1;33mDue to permission problem, these directoies are not processed.\033[m')
        print('\033[1;33mPlease reset permissions for them by hand.\033[m')
        print('\033[1;33mSorry for the inconvenience.\033[m')
        print('')
        print('\033[1;33mSkiped directories:\033[m')
        for i in locked_dirs:
            print('\033[1;33m' + i + '\033[m')
        print('\033[1;33m==============================================================\033[m')

def parse_rule_format (line):
    match_result = rule_matcher.match(line)
    if match_result:
        return match_result.group(1), match_result.group(2), match_result.group(3)
    else:
        if line != "" and line[0] != '#':
            if sys.stdout.isatty():
                print('\033[1;33mRule format incorrect:\033[m', line)
            else:
                print('Rule format incorrect:', line)
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
        if sys.stdout.isatty():
            raw_input()

    if '^.*$' not in [i[-1] for i in dir_rules]:
        print('\033[1;33m=================================================================\033[m')
        print('\033[1;33mFriendly warning:\033[m')
        print('\033[1;33m  Your rule file has no default rule for directories like "^.*$".\033[m')
        print('\033[1;33m  There may be directories that doesn\'t match any rule.\033[m')
        print('\033[1;33m=================================================================\033[m')
        print('Press enter to continue.')
        if sys.stdout.isatty():
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

    if sys.stdout.isatty():
        for i in block_lines[1:]:
            print('| {} | {} |'.format(i[0], i[1]).\
                replace('^', '\033[1;32m^').replace('$', '$\033[m'))
    else:
        for i in block_lines[1:]:
            print('| {} | {} |'.format(i[0], i[1]))

    # table bottom line
    print(table_top_line)

    print('Rule file format:')

    for i in file_rules:
        print( 'f {} {}'.format(i[0], i[1]) )

    for i in dir_rules:
        print( '{} {} {}'.format(i[0], i[1], i[2]) )

def print_help_page_and_exit ():
    name = sys.argv[0]
    print('Usage:')
    print('')
    print('    {name} [-h|--help]'.format(name=name))
    print('        Show this help message and exit')
    print('')
    print('    {name} [--rule RULE_FILE] --show-rules'.format(name=name))
    print('        Show current rule set and exit')
    print('        Custom rule set can be applied by --rule option')
    print('')
    print('    {name} [--rule RULE_FILE] [--list-all|--list-match] ROOTDIR'.format(name=name))
    print('        List items and their actions recursively under ROOTDIR')
    print('        Custom rule set can be applied by --rule option')
    print('')
    print('    {name} [OPTIONS] ROOTDIR'.format(name=name))
    print('        Recursively set permissions under rootdir according the rule set')
    print('')
    print('OPTIONS')
    print('')
    print('    --rule RULE_FILE        Apply specified rule set')
    print('    --interact              Confirm every files and directories')
    print('    --no-prograss           Don\'t calculate total item amount')
    exit()

def parse_arguments (args):

    # copy sys.argv without first argument
    args = list(args[1:])

    result = {}

    # because of unfamiliar with argparser,
    #  I use my shell script parsing style here
    try:
        while (len(args) > 0):
            first = args[0]

            if first in ['-h', '--help']:
                result['help'] = True

            elif first in ['--rule', '--rule-file', '--rule_file']:
                result['rule_file'] = args[1]
                args = args[1:]

            elif first in ['--show-rules', '--show_rules']:
                result['show_rules'] = True

            elif first in ['--interact']:
                result['interact'] = True
            
            elif first in ['--list-all']:
                result['list'] = 'all'

            elif first in ['--list-match']:
                result['list'] = 'match'

            elif first in ['--no-progress']:
                result['no_progress'] = True

            else:
                result['rootdir'] = first

            # pop one argument
            args = args[1:]
    except IndexError:
        print_help_page_and_exit()

    return result

def main ():

    args = parse_arguments(sys.argv)

    if args.get('help'):
        print_help_page_and_exit()

    if args.get('rule_file'):
        import_rule_file(args['rule_file'])

    if args.get('show_rules'):
        show_rules()

    elif args.get('list'):

        if args.get('rootdir'):
            if args.get('list') == 'all':
                test( args['rootdir'], verbose=True )
            else:
                test( args['rootdir'], verbose=False)

        else:
            print_help_page_and_exit()

    else:
        if args.get('rootdir'):
            clean_permission(args.get('rootdir'))
            pass
        else:
            print_help_page_and_exit()

if __name__ == '__main__':
    main()
