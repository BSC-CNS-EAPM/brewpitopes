#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 10 14:21:51 2020
@author: rocfarriolduran
"""
### EPITOPE EXTRACTOR
## GOAL: extract linear epitopes in tabulated data either from linear or structural prediction origin.
## Variant for structural Discotope predictions at: 
## https://services.healthtech.dtu.dk/service.php?DiscoTope-2.0
## SUBGOAL: Create epitopes from continous residues that surpass a given quality threshold in Structural predictions.


# IMPORTS
import sys
import csv
import os.path
from pathlib import Path
import pandas as pd
import more_itertools as mit
import statistics

## HELP
h = '''
    To right usage of this script:
        $ python3 epixtractor_structural.py 
        The files in use have to be provided by stating
        "location/file_name.csv"
    to the input questions that appear in the console.
    <file_name> should be a .csv separated by ","
    OPTIONAL 
    The script returns a <file_name>_out.xlsx as output.
    You can also do the following (if using Mac/Linux OS):
        $ chmod +x epixtractor_structural.py 
        $ ./epixtractor_structural.py  <location/file_name.csv>
    You need python 3 installed in your computer!!!
    '''


## FILE EXISTANCE
def fileExist(file):
    if file!="":
        if Path(file).is_file():
            return True
        elif file=='-h':
            print(h)
        else:
            print("\n>>>>>>> "+file + " File not exist or is not accessible\n")
            return False
    else:
        return False


## FILE UPLOAD
data_file=""
num_args=len(sys.argv)

if num_args>=2:
    data_file = sys.argv[1]

while not fileExist(data_file):
    data_file = input(''' Provide location and name of the file dataset.
        For example: data/file_test.csv
            (-h for help)
        Here: ''')

print("Input file: " + data_file)


## MULTICHAIN MODULE
# Executed externally.

# NAME THE OUTPUT FILE
extension = os.path.splitext(data_file)[1]
lenextension=len(extension)
nameOutFile=data_file[:-lenextension]+"_Out"+extension
#out_file=open(nameOutFile, "w")
#out_file.writelines("Epitope_id,Epitope_seq\n")

## PIPELINE for EXTRACTION OF EPITOPES FROM STRUCTURAL PREDICTIONS

# READ THE CSV INPUT & ADD HEADERS TO DISCOTOPE DATAFRAME
prediction = pd.read_csv(data_file, 
			 sep='\t',
			 names = ["SeqPos", "AliSeq", "model1", "model2", "model3", "model4", "model5", "average", "prediction", "stdev", "zscore"],
             skiprows=1)
##SeqPos    AliSeq  model1  model2  model3  model4  model5  average prediction  stdev   zscore

print(prediction)

## 3-LETTER TO 1-LETTER AA SCRIPT

# Create dictionary for aminoacids
'''aa_dict = {"ALA" : "A",
           "ARG" : "R",
           "ASN" : "N",
           "ASP" : "D",
           "CYS" : "C",
           "GLN" : "Q", 
           "GLU" : "E",
           "GLY" : "G",
           "HIS" : "H",
           "ILE" : "I",
           "LEU" : "L",
           "LYS" : "K",
           "MET" : "M",
           "PHE" : "F",
           "PRO" : "P",
           "SER" : "S",
           "THR" : "T",
           "TRP" : "W",
           "TYR" : "Y",
           "VAL" : "V"}'''

# Extract residues to convert
#residues = prediction["resName"] #column from df as series
           
# Use dictionary to convert 3LAA to 1LAA into new df column
prediction["aa"]=residues.map(aa_dict)
    
## Error when treating multi chain data. >= cannot read strings or floats.
# Filter by discotope_score threshold at -3.7
scored = prediction.loc[prediction['average'] >= 0.5]

# Reset index of filtered DF to use indexes later on
scored = scored.reset_index(drop=True)

# Loop to append a position if the previous is contiguous
resid = []
for i in range(len(scored)):
    try:
        if scored.loc[i,'SeqPos']-scored.loc[i-1,'SeqPos'] == 1:
            resid.append(scored.loc[i,'SeqPos'])
    except:
        resid.append(scored.loc[i,'SeqPos'])
        continue
        
# Group the epitopes and extract positions
resid_grouped = [list(group) for group in mit.consecutive_groups(resid)]

# filter for groups larger than 4 elements
resid_grouped_filtered = [group for group in resid_grouped if len(group)>=2]
resid_grouped_filtered

# EXTRACT THE CONTINOUS SEQUENCES
sequences = []
for group in resid_grouped_filtered:
    sequence = []
    for n in group:
        sequence.append(scored.AliSeq[scored.SeqPos==n].values[0])
    sequences.append(''.join(sequence))
sequences

# LOOP TO EXTRACT START AND END POSITION
start = []
end = []
for group in resid_grouped_filtered:
    start.append(group[0])
    end.append(group[-1])
    print(start)
    print(end)
    
# EXTRACT MEAN SCORE
scores = []
for group in resid_grouped_filtered:
    score = []
    for n in group:
        score.append(scored.average[scored.SeqPos==n].values[0])
    scores.append(statistics.mean(score))
scores
    
# EXTRACT SCORE
Score = scores

# CREATE LIST TO PREPARE OUTPUT DATAFRAME
out = list(zip(sequences,start,end,resid_grouped_filtered, Score))
print (out)

# CREATE OUTPUT DATAFRAME
out_file = pd.DataFrame(out, columns = ("Sequence", "Start", "End", "Positions", "Score"))
print(out_file)

# EXPORT OUTPUT FILE
out_file.to_csv(nameOutFile, sep = ";", index = True, index_label = "Rank")
print("Output file: "+nameOutFile)