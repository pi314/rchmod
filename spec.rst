Command Line Arguments
----------------------

# Output help page and exit
rchmod [-h|--help]

rchmod rootdir

# Use Rule in rule_file
rchmod --rule rule_file rootdir

# Show rules and exit
rchmod --show-rules

# Ask for every file and directory
rchmod [-i|--interact] rootdir

# List the files/directories need to be processed and exit
rchmod --test rootdir

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

Dynamically add new rules may be needed,
or I need to parse the rule to use
^.*\.git$
on
.../.git/...
