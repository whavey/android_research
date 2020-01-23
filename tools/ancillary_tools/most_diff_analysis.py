#!/usr/bin/python3

import json
import os

with open('analysis/post_analysis.json','r') as resfile:
    jfile = json.load(resfile)

    print("Unique identifiers found with >=8 Sensitivity Score for:")
    for cat in list(jfile.keys())[:-1]:
        most_diff = jfile[cat]["meta"]["most_diff_from_avg"]["app"]
        cat_avg = jfile[cat]["meta"]["avg"]

        entry_list = []
        print(f" {cat}: {most_diff.replace('results-','')}: AVG: {cat_avg}\n", "="*(9 + len(cat) + len(most_diff.replace('results-','')) + len(str(cat_avg))))
        
        with open(f"full_results/{cat}/{most_diff}", 'r') as catres:
            j2file = json.load(catres)
        
            for res in j2file['results']:
        
                for structkey in res.keys():
        
                    for _res in res[structkey]:
                        if _res["SENSITIVITY_LEVEL"] > cat_avg:
                            entry_list.append(f"{_res['ANDROID_APP_TOKEN']}:{_res['SENSITIVITY_LEVEL']}")
        
            for entry in set(entry_list):
                print(' ', entry)
        
        print("\n")
