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

def get_file_action (perm, dir_path, file_name):

    # skip symbolic links
    if os.path.islink(dir_path + '/' + file_name):
        return 'ign'

    for r in file_rules:
        if re.match(r[1], file_name):
            return r[0]

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

def gen_items (rootdir, verbose=False, trim=True):
    for dir_path, sub_dirs, files in os.walk(rootdir):
        perm = oct(os.lstat(dir_path).st_mode & 0777)[1:]

        action = get_dir_action(perm, dir_path, sub_dirs, files)

        if action == 'ign':
            if verbose:
                for i in ignore_tree(dir_path):
                    yield i
            del sub_dirs[:]
        else:
            if action != perm or not trim:
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

                #result.append(
                #    (   action,
                #        'f',
                #        perm,
                #        file_name)
                #    )
                output = False
                if action == 'ign':
                    if verbose:
                        output = True
                elif action == perm:
                    if not trim:
                        output = True
                else:
                    output = True

                if output:
                    yield (action, 'f', perm, dir_path + '/' + file_name)
    
def test (rootdir):
    item_list = gen_items(rootdir, verbose=True, trim=False)
    if sys.stdout.isatty():
        for i in item_list:
            #(action, 'f', perm, file_name)
            if i[0] == 'ign':
                print( '\033[1;35m[ignore][{}->   ] {}\033[m'.format(i[2], i[3]) )
            elif i[0] == i[2]:
                print( '\033[1;30m[ skip ][{}->{}]\033[m {}'.format(i[2], i[0], i[3]) )
            else:
                print( '\033[1;32m[match ][{}->{}]\033[m {}'.format(i[2], i[0], i[3]) )
    else:
        for i in item_list:
            if i[0] == 'ign':
                print( '[ignore][{}->   ] {}'.format(i[2], i[3]) )
            elif i[0] == i[2]:
                print( '[ skip ][{}->{}] {}'.format(i[2], i[0], i[3]) )
            else:
                print( '[match ][{}->{}] {}'.format(i[2], i[0], i[3]) )

def clean_permission (rootdir):
    item_list = list( gen_items(rootdir, verbose=False, trim=True) )
    total_amount = len(item_list)
    print(total_amount)
    #if sys.stdout.isatty():
    for i in item_list:
        print( '\033[1;32m[match ][{}->{}]\033[m {}'.format(i[2], i[0], i[3]) )
            
    #(action, 'f', perm, file_name)
    #else:
    #os.chmod( item, int('755', 8) )
    #print(len(item_list))
    pass

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
    else:
        clean_permission(args.rootdir)

if __name__ == '__main__':
    main()
