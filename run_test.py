#!/drives/c/Users/wayne/Desktop/Research/android/tools/python3
import time
import sys
import argparse
import subprocess
import os
import shutil
import xml.etree.ElementTree as ET
import configparser

def parse_args():
    parser = argparse.ArgumentParser(description='Run Flowdroid.')
    parser.add_argument('-a','--app', type=str, required=True, help='name of app (assumes path)')
    parser.add_argument('-s','--sands', type=str, required=True, help='name of sources and sinks file (assumes path)')
    parser.add_argument('-l','--log_name', type=str, required=True, help='name of log to write to (assumes path)') 
    parser.add_argument('-o','--other_args', type=str,  help='additional flowdroid args to pass') 
    parser.add_argument('-hp','--heap', type=str, help='Xmx heap max for jar') 
    parser.add_argument('-fh','--flowdroid_help', action='store_true', help='see flowdroid help') 
    parser.add_argument('-c','--config_file', help='use config file') 
    return parser.parse_args()
args = parse_args()


#TODO: auto detect best heap size
def heap_setup():
  heap = args.heap if args.heap else "1024m"
  if heap[-1] != "m":
      heap = heap + "m"
  return heap

def read_config(args):
  config = configparser.ConfigParser()
  if args.config_file:
    config.read(args.config_file)
  elif os.path.exists('./config'):
    config.read('./config')
  else:
    print('Must specify config file or \'./config\' must exist')
    sys.exit()
  return config
    
config = read_config(args)

flowdroid_path = config['Paths']['flowdroid_path'] 
platforms_path = config['Paths']['platforms_path'] 
app_path = config['Paths']['app_path'] 
sands_path = config['Paths']['sands_path'] 
logs_path = config['Paths']['logs_path'] 
soot_output = config['Paths']['soot_output'] 

if args.flowdroid_help:
  p1 = subprocess.Popen(['java', '-jar', flowdroid_path, '--help'])
  sys.exit()

results_dir = os.path.join(logs_path,args.log_name)
if not os.path.exists(results_dir):
    os.mkdir(results_dir)

log_file = "{}_output.xml".format(os.path.join(results_dir,args.log_name))
run_log = os.path.join(results_dir,"{}_run_log".format(args.log_name))
sands_file = r"{}/{}".format(sands_path,args.sands)
app_location = r"{}/{}".format(app_path,args.app)

if args.other_args:
  other_args = ['-{} '.format(a) for a in args.other_args.split(',')]
  p1 = subprocess.Popen(['java', '-Xmx{}'.format(heap_setup()), '-jar', flowdroid_path, '-p', platforms_path, '-s', sands_file, '-a', app_location, '-ls', '-o', log_file, other_args])
else:
  p1 = subprocess.Popen(['java', '-Xmx{}'.format(heap_setup()), '-jar', flowdroid_path, '-p', platforms_path, '-s', sands_file, '-a', app_location, '-ls', '-o', log_file])

p1.wait()

jimple_results = os.path.join(results_dir,"jimple_{}".format(args.log_name))
if os.path.exists(jimple_results):
    shutil.rmtree(jimple_results)
if not os.path.exists(soot_output):
  print("Something went wrong, no soot output generated")
  sys.exit()

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
