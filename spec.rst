Command Line Arguments
----------------------

Usage:
    {name} [-h|--help]

        Show this help message and exit

    {name} [--rule RULE_FILE] --show-rules

        Show current rule set and exit
        Custom rule set can be applied by --rule option

    {name} [--rule RULE_FILE] [--list-all|--list-match] ROOTDIR

        List items and their actions recursively under ROOTDIR
        Custom rule set can be applied by --rule option

    {name} [OPTIONS] ROOTDIR

        Recursively set permissions under rootdir according the rule set

OPTIONS

    --rule RULE_FILE        Apply specified rule set

    --interact              Confirm every files and directories

    --no-prograss           Don't calculate total item amount

    --ignore-error          Keep going when error occurs

Rule File Format
----------------
#comment
f 755 ^.*\.sh$
f 755 ^.*\.exe$
f 644 ^.*$
d ign ^.*\.git$ # ignore
d 755 ^.*$
h ign ^.*\.git$ # directories that "has" ".git" are ignored

Output Format
-------------

-   normal processing

    <color>[XX%]</color>[aaa->bbb] filename
    color: cyan for directory, green for file

-   for command line ``--test``

    [Y][aaa->bbb] filename
    [N][aaa->bbb] filename
    [J][aaa->aaa] filename


Notes
-----

if rootdir is a file:
    process it and exit

filter(function, sequence)

sum(1 for i in gen)

links should be always skiped
