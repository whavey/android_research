#!/usr/bin/python3

x = 0
with open('count', 'r') as count:
    for i in count:
        if int(i) > 29:
            i = 29
        x += int(i)

print(x)
