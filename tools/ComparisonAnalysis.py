#!/usr/bin/python3
import os
import json

global master_total
global master_total_no_zeros
global master_avg
global master_avg_no_zeros
global master_count
global master_count_no_zeros
global master_number_of_tens
global app_count
global analysis_dict

def getStats(cat, catlist):
    global master_total
    global master_total_no_zeros
    global master_avg
    global master_avg_no_zeros
    global master_count
    global master_count_no_zeros
    global master_number_of_tens
    global app_count

    if type(catlist) == str:
        catlist = [catlist]

    app_count += len(catlist)

    if len(catlist) > 0:
        number_of_tens = 0
        count = 0
        total = 0
        total_avg = 0
        count_no_zeros = 0
        total_avg_no_zeros = 0
        app_dict = {}

        for f in catlist:
            app_num_tens = 0
            with open(os.path.join("full_results", cat, f)) as jfile:
                j = json.loads(jfile.read())
                _total = j["meta"]["total_privacy_score"]
                avg = j["meta"]["average_privacy_score"]

                analysis_dict[cat][f] = { "agg": _total, "avg": avg }

                if j["meta"]["highest_sensitivity_score"] == 10:
                    number_of_tens += 1
                    master_number_of_tens += 1
                    app_num_tens += 1

                app_dict[f] = { "num_tens": app_num_tens }

                if avg != 0:
                    count_no_zeros += 1
                    total_avg_no_zeros += avg
                    master_total_no_zeros += _total
                    master_avg_no_zeros += avg
                    master_count_no_zeros += 1
                  
                count += 1
                total += _total
                total_avg += avg

                master_total += total
                master_count += count
                master_avg += total_avg

        print(f"\n{cat}:\n{'='*len(cat)}\nAPPS: {len(catlist)}")
        if total != 0:
            print("aggregate score:", total)
            print("aggregate average privacy score:", total/count)
            print("average privacy score:", total_avg/count)
            print("Number of 10 sensitivity keywords found:",number_of_tens)

            if count != count_no_zeros:
                print("Average total privacy score (NO ZEROS):", total/count_no_zeros)
                print("average privacy score (NO ZEROS):", total_avg_no_zeros/count_no_zeros)

        else:
            print("no results")

        analysis_dict[cat]["meta"] = {
                "aggregate": total, 
                "agg_avg": total/count, 
                "avg": total_avg/count, 
                "num10": number_of_tens, 
                "agg_avg_nz": total/count_no_zeros, 
                "avg_nz": total_avg_no_zeros/count_no_zeros
                }

master_total = 0
master_total_no_zeros = 0
master_avg = 0
master_avg_no_zeros = 0
master_count = 0
master_count_no_zeros = 0
master_number_of_tens = 0
app_count = 0
analysis_dict = {}

master_dict = {}
for cat in os.listdir("full_results"):
    resfiles = [f for f in os.listdir(os.path.join("full_results", cat)) if "results-" in f]
    master_dict[cat] = resfiles
    analysis_dict[cat] = {}
    getStats(cat, master_dict[cat])

    print(f"\nWithin Category Analysis:")
    most_diff = (0, None)
    most_diff_nz = (0, None)
    for f in list(analysis_dict[cat].keys())[1:]:
        diff = analysis_dict[cat][f]["avg"] - analysis_dict[cat]["meta"]["avg"]
        if abs(diff) > most_diff[0]:
            most_diff = (diff, f)

        diff_nz = analysis_dict[cat][f]["avg"] - analysis_dict[cat]["meta"]["avg_nz"]
        if abs(diff_nz) > most_diff_nz[0]:
            most_diff_nz = (diff_nz, f)

        print(f"\t{f} ({analysis_dict[cat][f]['avg']}):\tdifference from avg:", diff)
        print(f"\t{f} ({analysis_dict[cat][f]['avg']}):\tdifference from avg (NO ZEROS):", diff_nz)

    print(f"\n\t{most_diff[1]} was the APK that differed from category avg the most by: {most_diff[0]}.")
    print(f"\t{most_diff_nz[1]} was the APK that differed from category avg the most (NO ZEROS) by: {most_diff_nz[0]}.")

print("\n\nOverall Analysis")
print("Total APPs:", app_count)
print("Overall aggregate score:", master_total)
print("Overall aggregate score average:", master_total/master_count)
print("Overall aggregate score average (NO ZEROS):", master_total/master_count_no_zeros)
print("Overall privacy sensitivity average:", master_avg/master_count)
print("Overall privacy sensitivity average (NO ZEROS):", master_avg_no_zeros/master_count_no_zeros)
print("Total number of 10 sensitivity ratings:", master_number_of_tens)
