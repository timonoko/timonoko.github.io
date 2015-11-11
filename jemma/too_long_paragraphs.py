#! /usr/bin/python

import sys

In_String=False
String_Count=0
Sentence_Count=0
c=0

while True:
    prev_c=c
    c=sys.stdin.read(1)
    if not c:
        break
    Sentence_Count=Sentence_Count+1
    if In_String:
        String_Count=String_Count+1
        if String_Count>300:
            In_String=False
    if c=='\r':
        c=prev_c
    elif c=='\n':
        if prev_c=='\n':
            sys.stdout.write('\n- - - \n')
        else:
            sys.stdout.write(' ')
    elif c=='"':
        sys.stdout.write(c)
        if In_String:
            In_String=False
            String_Count=0
        else:
            In_String=True
    elif c==' ':
        if not In_String and prev_c=='.' and Sentence_Count>300:
            Sentence_Count=0
            sys.stdout.write('\n  ')
        else:
            sys.stdout.write(' ')
    else:
        sys.stdout.write(c)

      
