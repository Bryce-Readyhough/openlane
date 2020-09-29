# Copyright 2020 Efabless Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import subprocess
import csv
import pandas as pd

parser = argparse.ArgumentParser(
        description="compare one design from a regression result to a benchmark result")


parser.add_argument('--benchmark', '-b', action='store', required=True,
                help="The csv file from which to extract the benchmark results")

parser.add_argument('--regression_results', '-r', action='store', required=True,
                help="The csv file to be tested")

parser.add_argument('--design', '-d', action='store', required=True,
                help="The design to compare for between the two scripts. Same as -design in flow.tcl")

parser.add_argument('--output_report', '-o', action='store', required=True,
                help="The file to print the final report in")


args = parser.parse_args()
benchmark_file = args.benchmark
regression_results_file = args.regression_results
output_report_file = args.output_report
design = args.design


tolerance = {'general_tolerance':1, 'tritonRoute_violations':2, 'Magic_violations':10, 'antenna_violations':2}

critical_statistics = ['tritonRoute_violations','Magic_violations', 'antenna_violations']


def compare_vals(benchmark_value, regression_value, param):
    if str(benchmark_value) == "-1":
        return True
    if str(regression_value) == "-1":
        return False
    tol = tolerance['general_tolerance']
    if param in tolerance.keys():
        tol = 0-tolerance[param]
    if float(benchmark_value) - float(regression_value) >= tol: 
        return True
    else:
        return False

def findIdx(header, label):
    for idx in range(len(header)):
        if label == header[idx]:
            return idx
    else:
        return -1

def parseCSV(csv_file):
    design_out = dict()
    csvOpener = open(csv_file, 'r')
    csvData = csvOpener.read().split("\n")
    headerInfo = csvData[0].split(",")
    designNameIdx = findIdx(headerInfo, "design")
    if designNameIdx == -1:
        print("invalid report. No design names.")
    for i in range(1, len(csvData)):
        if len(csvData[i]):
            entry = csvData[i].split(",")
            designName=entry[designNameIdx]
            if designName == design:
                for idx in range(len(headerInfo)):
                    if idx != designNameIdx:
                        design_out[headerInfo[idx]] = entry[idx]
                break
    return design_out
    
def criticalMistmatch(benchmark, regression_result):
    if len(benchmark) == 0 or len(regression_result) == 0:
        return False, "Nothing to compare with"
    for stat in critical_statistics:
        if compare_vals(benchmark[stat],regression_result[stat],stat):
            continue
        else:
            if str(regression_result[stat]) == "-1":
                return True, "The test didn't pass the stage responsible for "+ stat
            else:
                return True, "The results of " +stat+" mismatched with the benchmark"
    return False, "The test passed"
        

benchmark = parseCSV(benchmark_file)
regression_result = parseCSV(regression_results_file)

testFail, reasonWhy = criticalMistmatch(benchmark,regression_result)

report = str(design)
if testFail:
    report += ",FAILED,"+reasonWhy+"\n"
else:
    report += ",PASSED,"+reasonWhy+"\n"


outputReportOpener = open(output_report_file, 'a+')
outputReportOpener.write(report)
outputReportOpener.close()