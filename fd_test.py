import time
import sys
import argparse
import subprocess
import os
import shutil
import xml.etree.ElementTree as ET

def parse_args():
    parser = argparse.ArgumentParser(description='Run Flowdroid.')
    parser.add_argument('-a','--app', type=str,  help='name of app (assumes path)')
    parser.add_argument('-s','--sands', type=str,  help='name of sources and sinks file (assumes path)')
    parser.add_argument('-l','--log_name', type=str,  help='name of log to write to (assumes path)') 
    parser.add_argument('-o','--other_args', type=str,  help='additional flowdroid args to pass') 
    parser.add_argument('-hp','--heap', type=str,  help='Xmx heap max for jar') 
    parser.add_argument('-fh','--flowdroid_help', type=str,  help='see flowdroid help') 
    return parser.parse_args()

args = parse_args()



base_path = r'C:\users\wayne\desktop\research\android'
flowdroid_path = base_path + r'\tools\flowdroid\source\FlowDroid-master\soot-infoflow-cmd\target\soot-infoflow-cmd-jar-with-dependencies.jar'
platforms_path = r'C:\users\wayne\AppData\local\Android\sdk\platforms'
app_path = base_path + r'\apps'
sands_path = base_path + r'\tools\flowdroid\sands'
logs_path = base_path + r'\tools\flowdroid\logs'
soot_output = base_path+r'\tools\sootOutput'

if args.flowdroid_help:
    p1 = subprocess.Popen(['java', '-jar', flowdroid_path, '--help'])
    sys.exit()

results_dir = os.path.join(logs_path,args.log_name)

if not os.path.exists(results_dir):
    os.mkdir(results_dir)

log_file = "{}_output.xml".format(os.path.join(results_dir,args.log_name))
run_log = os.path.join(results_dir,"{}_run_log".format(args.log_name))
sands_file = r"{}\{}".format(sands_path,args.sands)
app_location = r"{}\base\{}".format(app_path,args.app)
heap = args.heap if args.heap else "1024m"
if heap[-1] != "m":
    heap = heap + "m"
if args.other_args:
    other_args = ['-{} '.format(a) for a in args.other_args.split(',')]
    p1 = subprocess.Popen(['java', '-Xmx{}'.format(heap), '-jar', flowdroid_path, '-p', platforms_path, '-s', sands_file, '-a', app_location, '-ls', '-o', log_file, other_args])
else:
    p1 = subprocess.Popen(['java', '-Xmx{}'.format(heap), '-jar', flowdroid_path, '-p', platforms_path, '-s', sands_file, '-a', app_location, '-ls', '-o', log_file])
p1.wait()

jimple_results = os.path.join(results_dir,"jimple_{}".format(args.log_name))
if os.path.exists(jimple_results):
    shutil.rmtree(jimple_results)
os.rename(soot_output,jimple_results)


with open(run_log,'w+') as result:
    print("Results:","\n\tApp: {}\n\tSources_and_sinks_file: {}".format(args.app,args.sands), file=result)
    tree = ET.parse(log_file)
    root = tree.getroot()
    print("\tSinks:",file=result)
    for sink in root.iter('Sink'):
        print("\t\tStatement:\n\t\t\t-",sink.attrib['Statement'],"\n\t\tMethod:\n\t\t\t-",sink.attrib['Method'], file=result)
    print("\tSources:",file=result)
    for source in root.iter('Source'):
        print("\t\tStatement:\n\t\t\t-",source.attrib['Statement'],"\n\t\tMethod:\n\t\t\t-",source.attrib['Method'], file=result)