import re
import matplotlib.pyplot as plt
import requests
import subprocess
import tempfile
from datetime import datetime
#absolute position of code-maat jar
CODE_MAAT_JAR_PATH = ""
LIBGDX_RELEASE_LOG = "https://raw.githubusercontent.com/libgdx/libgdx/master/CHANGES"
#absolute position of log file
logfile = ""
#gets chucn data between start and end (exclusive) time period
def getChurnBetween(CM_path, logfile_path):
    churn_history = []
    days_from_beginning = 0
    with tempfile.TemporaryFile() as tempf:
        analysis = ['java', '-jar', CM_path, '-l', logfile_path, '-c','git2', '-a', 'abs-churn']
        proc = subprocess.Popen(analysis, stdout=tempf)
        proc.wait()
        tempf.seek(0)
        tempf.readline()
        for line in tempf.readlines():
            dataline = line.split(',')
            addition = int(dataline[1])
            date = dataline[0]
            deletion = int(dataline[2])
            abs_churn = addition - deletion
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            churn_history.append((date_obj, abs_churn, addition, deletion))
    return churn_history

#parses all libgdx api events
def getlibgdxAPIEvents():
    by_patch = {}
    by_type = {}
    curr_patch = "Unknown Patch"
    r = requests.get("https://raw.githubusercontent.com/libgdx/libgdx/master/CHANGES", stream = True)
    for line in r.iter_lines():
        #if start of a new release
        match = re.search(r'\[(\d+\.\d+\.\d+)\]', line)
        if match:
            curr_patch = match.group(1)
        else:
            match = re.search(r'-\s+API\s(.+):(.+)', line)
            if match:
                type = match.group(1).lower()
                message = match.group(2)
                if curr_patch in by_patch:
                    by_patch[curr_patch].append((type, message))
                else:
                    by_patch[curr_patch] = [(type, message)]
                if type in by_type:
                    by_type[type].append((curr_patch, message))
                else:
                    by_type[type] = [(curr_patch, message)]
    print by_patch
    return by_patch , by_type

def plotChurn(dates, option = "all", start = None, end = None):
    first_day = dates[0][0]
    dateFromFunc = lambda date: (date - first_day).days
    timeline  = map(lambda item : dateFromFunc(item[0]), dates)
    plt.figure(figsize=(8,5), dpi = 200)
    plt.subplot(111)
    plt.xlabel("days from beginning")
    plt.ylabel("lines of code")
    if option is "all":
        plt.bar(timeline, map(lambda item: item[1], dates), color="blue", label = "Absolute churn ")
        plt.bar(timeline, map(lambda item: item[2], dates), color="green", label = "Addition churn ")
        plt.bar(timeline, map(lambda item: item[3], dates), color="red", label="Deletion churn ")
    elif option is "add":
        plt.bar(timeline, map(lambda item: item[2], dates), color="green", label = "Addition churn ")
    elif option is "del":
        plt.bar(timeline, map(lambda item: item[3], dates), color="red", label = "Deletion churn ")
    plt.legend()
    plt.savefig("img.png")

churns = getChurnBetween(CODE_MAAT_JAR_PATH, logfile)
plotChurn(churns, option = "add")