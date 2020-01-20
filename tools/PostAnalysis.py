#!/usr/bin/python3
import os
import json
import numpy as np
import scipy.io
 
class PostAnalysis():

    def __init__(self, applimit = 20):

        self.categories  = [cat for cat in os.listdir("full_results")]
        self.analysis_dict = {}
        self.resdict = {}

        self.highest_avg_score = (0, None)
        self.highest_agg_score = (0, None)
        self.highest_avg_score_nz = (0, None)

        self.global_app_count = 0 
        self.global_app_count_nz = 0 
        self.global_agg = 0
        self.global_avg = 0
        self.global_avg_nz = 0
        self.global_entries = 0
        self.global_num10 = 0

        for cat in self.categories:
            self.resdict[cat] = []

            count = 0
            for f in os.listdir(os.path.join("full_results", cat)):
                if count >= applimit:
                    break
        
                if "results-" in f:
                    self.resdict[cat].append(f)
                    count += 1
        
            self.analysis_dict[cat] = {}

        if not os.path.isdir("analysis"):
            os.mkdir("analysis")

    @property
    def getCats(self):
        return self.categories
    
    def genVectors(self):
    
        vector_avg_nz = [self.categories, []]
        vector_avg = [self.categories, []]
        vector_agg = [self.categories, []]
        vector_num_10 = [self.categories, []]
        vector_num_results = [self.categories, []]
        vector_greatest_difference = [self.categories, [], [], []]
        vector_greatest_difference_nz = [self.categories, [], [], []]
        table_10tokens = {} 
    
        np_vectors = {} 
        
        for cat in self.categories:
            table_10tokens[cat] = self.analysis_dict[cat]["meta"]["10tokens"]
            vector_avg_nz[1].append(self.analysis_dict[cat]["meta"]["avg_nz"])
            vector_avg[1].append(self.analysis_dict[cat]["meta"]["avg"])
            vector_agg[1].append(self.analysis_dict[cat]["meta"]["aggregate"])
            vector_num_10[1].append(self.analysis_dict[cat]["meta"]["num10"])
            vector_num_results[1].append(self.analysis_dict[cat]["meta"]["num_results"])
        
            vector_greatest_difference[1].append(self.analysis_dict[cat]["meta"]["most_diff_from_avg"]["diff"])
            vector_greatest_difference[2].append(self.analysis_dict[cat]["meta"]["most_diff_from_avg"]["score"])
            vector_greatest_difference[3].append(self.analysis_dict[cat]["meta"]["most_diff_from_avg"]["app"].replace("results-",''))
        
            vector_greatest_difference_nz[1].append(self.analysis_dict[cat]["meta"]["most_diff_from_avg_nz"]["diff"])
            vector_greatest_difference_nz[2].append(self.analysis_dict[cat]["meta"]["most_diff_from_avg_nz"]["score"])
            vector_greatest_difference_nz[3].append(self.analysis_dict[cat]["meta"]["most_diff_from_avg_nz"]["app"].replace("results-",'')) 

        with open('analysis/table_10tokens.txt','w') as tokentable:
            for cat in table_10tokens.keys():
                print(f"{cat}:", file=tokentable)
                for token in table_10tokens[cat]:
                    print(f"\t{token}", file=tokentable)
        
        textfile = open('analysis/results.txt','w+')

        notes_avg_nz = "Average privacy sensitivity score per category. sum(privacy_sensitivity_avg foreach app in cat) / number of apps that had entries" 
        notes_avg = "Average privacy sensitivity score per category. sum(privacy_sensitivty_avg foreach app in cat) / number of apps including ones that had zero entries"
        notes_agg = "The sum of every apps privacy sensitivity score average in the category" 
        notes_num10 = "The number of privacy sensitive keywords found with a rating of 10 per category" 
        notes_numres = "The number of entries (identifiers that were similar to a privacy keyword) found across all apps in the category."
        notes_gd = "The app with a sensitivity average score most different from the category average using the category average score that was calculated including apps that had no results.COLUMNS: [[category],[difference],[apps_score],[app_name]]." 
        notes_gd_nz = "The app with a sensitivity average score most different from the category average using the category average score that was calculated NOT including apps that zero results. COLUMNS: [[category],[difference],[apps_score],[app_name]]."

        print(f"Vector_avg_nz:\n=======\nDescription: {notes_avg_nz}\n\n" + str(vector_avg_nz), file=textfile) 
        print(f"\nVector_avg:\n=======\nDescription: {notes_avg}\n\n" + str(vector_avg), file=textfile)
        print(f"\nVector_agg:\n=======\nDescription: {notes_agg}\n\n" + str(vector_agg), file=textfile)
        print(f"\nVector_num_10:\n=======\nDescription: {notes_num10}\n\n" + str(vector_num_10), file=textfile)
        print(f"\nVector_num_results:\n=======\nDescription: {notes_numres}\n\n" + str(vector_num_results), file=textfile)
        print(f"\nVector_greatest_difference:\n=======\nDescription: {notes_gd}\n\n" + str(vector_greatest_difference), file=textfile)
        print(f"\nVector_greatest_difference_nz:\n=======\nDescription: {notes_gd_nz}\n\n" + str(vector_greatest_difference_nz), file=textfile)
    
        #np_vector_avg_nz = np.array(vector_avg_nz),
        #np_vectors["np_vector_avg_nz"] =  np_vector_avg_nz
        #
        #np_vector_avg = np.array(vector_avg),
        #np_vectors["np_vector_avg"] =  np_vector_avg
        #
        #np_vector_agg = np.array(vector_agg)
        #np_vectors["np_vector_agg"] =  np_vector_agg
        #
        #np_vector_num_10 = np.array(vector_num_10),
        #np_vectors["np_vector_num_10"] =  np_vector_num_10
        #
        #np_vector_num_results = np.array(vector_num_results)
        #np_vectors["np_vector_num_results"] =  np_vector_num_results
        #
        #np_vector_greatest_difference = np.array(vector_greatest_difference)
        #np_vectors["np_vector_greatest_difference"] =  np_vector_greatest_difference
        #
        #np_vector_greatest_difference_nz = np.array(vector_greatest_difference_nz)
        #np_vectors["np_vector_greatest_difference_nz"] =  np_vector_greatest_difference_nz
        #
        #for npv in np_vectors.keys():
        #    scipy.io.savemat(f"analysis/{npv}.mat", mdict={f"{npv}": np_vectors[npv]})
    
    def catStats(self, cat):
    
        master_total = 0
        master_total_nz = 0
        master_avg = 0
        master_avg_nz = 0
        master_count = 0
        master_count_nz = 0
        master_number_of_tens = 0

        if len(self.resdict[cat]) > 0:
            count = 0
            count_nz = 0
            agg = 0
            sum_of_avg = 0
            count_nz = 0
            sum_of_avg_nz = 0
            app_dict = {}
            total_num_results = 0
            token_list = []
    
            for f in self.resdict[cat]:
                number_of_tens = 0
                with open(os.path.join("full_results", cat, f)) as jfile:
                    j = json.loads(jfile.read())
                    _agg = j["meta"]["total_privacy_score"]
                    avg = j["meta"]["average_privacy_score"]
                    
                    num_results = 0
                    if j["meta"]["highest_sensitivity_score"] == 10:
                        for entry in j["results"]:
                            for key in entry.keys():
                                num_results += len(entry[key])
                                for s_entry in range(len(entry[key])):
                                    if entry[key][s_entry]["SENSITIVITY_LEVEL"] == 10:
                                        token_list.append(str(entry[key][s_entry]["ANDROID_APP_TOKEN"]))
                                        number_of_tens += 1
                                        master_number_of_tens += 1
                    
                    total_num_results += num_results
                    self.analysis_dict[cat][f] = { "agg": _agg, "avg": avg, "num_results": num_results, "num10": number_of_tens}
    
                    if avg != 0:
                        count_nz += 1
                        sum_of_avg_nz += avg
                        master_total_nz += _agg
                        master_avg_nz += avg
                        master_count_nz += 1
                      
                    count += 1
                    agg += _agg
                    sum_of_avg += avg

            self.analysis_dict[cat]["meta"] = {
                    "num_apps": count,
                    "num_apps_nz": count_nz,
                    "num_results": total_num_results,
                    "aggregate": agg, 
                    "agg_avg_nz": agg/count_nz, 
                    "agg_avg": agg/count, 
                    "avg": sum_of_avg/count, 
                    "avg_nz": sum_of_avg/count_nz,
                    "num10": master_number_of_tens, 
                    "10tokens": list(set(token_list))
                    }
    
            #print(f"\n{cat}:\n{'='*len(cat)}\nAPPS: {len(self.resdict[cat])}")
            #if agg != 0:
            #    print("total number of results:", total_num_results)
            #    print("aggregate score:", agg)
            #    print("aggregate average privacy score:", agg/count)
            #    print("average privacy score:", sum_of_avg/count)
            #    print("Number of 10 sensitivity keywords found:", number_of_tens)
            #    print("Average 10 rated sensitivity keywords by app:", number_of_tens/count)
    
            #    if count != count_nz:
            #        print("Average total privacy score (NO ZEROS):", agg/count_nz)
            #        print("average privacy score (NO ZEROS):", sum_of_avg/count_nz)
    
            #else:
            #    print("no results")
    
    def catAnalysis(self):
    
            for cat in self.categories:

                most_diff = (0, None, 0)
                most_diff_nz = (0, None, 0)
                for f in self.resdict[cat]:
                    if self.analysis_dict[cat][f]["num_results"] == 0:
                        continue
    
                    diff = self.analysis_dict[cat][f]["avg"] - self.analysis_dict[cat]["meta"]["avg"]
                    if abs(diff) > most_diff[0]:
                        most_diff = (diff, f, self.analysis_dict[cat][f]["avg"])
    
                    diff_nz = self.analysis_dict[cat][f]["avg"] - self.analysis_dict[cat]["meta"]["avg_nz"]
                    if abs(diff_nz) > most_diff_nz[0]:
                        most_diff_nz = (diff_nz, f, self.analysis_dict[cat][f]["avg"])
    
                    #print(f"\t{f} Number of Results:", self.analysis_dict[cat][f]["num_results"])
                    #print(f"\t{f} ({self.analysis_dict[cat][f]['avg']}):\tdifference from avg:", diff)
                    #print(f"\t{f} ({self.analysis_dict[cat][f]['avg']}):\tdifference from avg (NO ZEROS):", diff_nz)
    
                    self.analysis_dict[cat][f].update({"diff_from_avg": diff, "diff_from_avg_nz": diff_nz})
    
                self.analysis_dict[cat]["meta"].update({
                    "most_diff_from_avg": {
                        "app": most_diff[1], 
                        "diff": most_diff[0],
                        "score": most_diff[2],
                        }, 
                    "most_diff_from_avg_nz": {
                        "app": most_diff_nz[1], 
                        "diff": most_diff_nz[0], 
                        "score": most_diff_nz[2], 
                        } 
                    })
    
                #print(f"\n\t{most_diff[1]} was the APK that differed from category avg the most by: {most_diff[0]}.")
                #print(f"\t{most_diff_nz[1]} was the APK that differed from category avg the most (NO ZEROS) by: {most_diff_nz[0]}.")
                print(json.dumps(self.analysis_dict[cat]), file=open(f"analysis/{cat}.json", 'w'))
            
    def globalStats(self):

        _global_avg = 0 
        _global_avg_nz = 0 
        for cat in self.categories:
            this_dict = self.analysis_dict[cat]["meta"]

            cat_avg = this_dict["avg"]
            if  cat_avg > self.highest_avg_score[0]:
                self.highest_avg_score = (cat_avg, cat)
    
            cat_avg_nz = this_dict["avg_nz"]
            if  cat_avg_nz > self.highest_avg_score_nz[0]:
                self.highest_avg_score_nz = (cat_avg_nz, cat)
    
            cat_agg = this_dict["aggregate"]
            if  cat_agg > self.highest_agg_score[0]:
                self.highest_agg_score = (cat_agg, cat)

            self.global_entries += this_dict["num_results"]
            self.global_agg += this_dict["aggregate"]
            self.global_app_count += this_dict["num_apps"]
            self.global_app_count_nz += this_dict["num_apps_nz"]
            self.global_num10 += this_dict["num10"]
            _global_avg += this_dict["avg"]
            _global_avg_nz += this_dict["avg_nz"]

        self.global_avg = _global_avg / len(self.categories)
        self.global_avg_nz = _global_avg_nz / len(self.categories)

        agg_avg = self.global_agg / len(self.categories)

        self.analysis_dict["meta"] = {
                "global_apps": self.global_app_count,
                "global_apps_nz": self.global_app_count_nz,
                "global_entries": self.global_entries,
                "global_entries_per_cat": self.global_entries / len(self.categories),
                "global_entries_per_app": self.global_entries / self.global_app_count,
                "global_aggregate": self.global_agg,
                "global_aggregate_avg": agg_avg,
                "global_sensitivity_avg": self.global_avg,
                "global_sensitivity_avg_nz": self.global_avg_nz,
                "global_10_sensitivity_ratings": self.global_num10,
                "highest_category_avg": {"category": self.highest_avg_score[1], "average": self.highest_avg_score[0]},
                "highest_category_avg_nz": {"category": self.highest_avg_score_nz[1], "average": self.highest_avg_score_nz[0]},
                "highest_category_agg": {"category": self.highest_agg_score[1], "aggregate": self.highest_agg_score[0]},
                }
        
        #print("\n\nOverall Analysis")
        #print("================")
        #print("Total Categories", len(self.categories))
        #print("Total APPs:", self.app_count)
        #print("Overall aggregate score:", master_total)
        #print("Overall aggregate score average by app count:", overall_agg_by_app)
        #print("Overall aggregate score average by app count (NO ZEROS):", overall_agg_by_app_nz)
        #print("Overall privacy sensitivity average:", avg_by_app) 
        #print("Overall privacy sensitivity average (NO ZEROS):", avg_by_app_nz)
        #print("Total number of 10 sensitivity ratings:", master_number_of_tens)
        #print("highest category average:", highest_avg_score[1], "with:",  highest_avg_score[0])
        #print("highest category average (NO ZEROS):", highest_avg_score_nz[1], "with:",  highest_avg_score_nz[0])
        #print("highest category aggregate:",  highest_agg_score[1], "with:", highest_agg_score[0])
        
        print(json.dumps(self.analysis_dict), file=open("analysis/post_analysis.json", "w"))

def main():
    ps = PostAnalysis()
    
    for cat in ps.getCats:
        ps.catStats(cat)
    
    ps.catAnalysis()
    ps.globalStats()
    ps.genVectors()

if __name__ == "__main__":
    main()

