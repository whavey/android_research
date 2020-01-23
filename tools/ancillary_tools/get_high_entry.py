#!/usr/bin/python3

import json
import os

with open('post_analysis.json','r') as resfile:
    jfile = json.load(resfile)

    high = 0
    highcat = None
    for cat in list(jfile.keys())[:-1]:
        val = jfile[cat]["meta"]["num_results"]
        if val > high:
            high = val
            highcat = cat

    print("highest Category:", highcat, "with:", high)
