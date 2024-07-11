import numpy as np
from datetime import datetime
import sys
import re
import glob
import os
import json
from pathlib import Path
import pandas as pd
#this script extracts effective data for U, L, y0,z0,y1

if (len(sys.argv)!=2):
    print("wrong number of arguments")
    exit()


rowNum=int(sys.argv[1])

rowDirRoot="../dataAll/row"+str(rowNum)+"/"
obs_U_dist="U_dist"

#search directory
TVals=[]
TFileNames=[]
TStrings=[]
for TFile in glob.glob(rowDirRoot+"/T*"):
    # print(TFile)
    matchT=re.search(r"T([-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)",TFile)
    if matchT:
        TFileNames.append(TFile)
        TVals.append(float(matchT.group(1)))
        TStrings.append("T"+matchT.group(1))
#sort T values
sortedInds=np.argsort(TVals)
sortedTVals=[TVals[ind] for ind in sortedInds]
sortedTFiles=[TFileNames[ind] for ind in sortedInds]
sortedTStrings=[TStrings[ind] for ind in sortedInds]

# print(sortedTFiles)

def parseSummary(oneTFolder,obs_name):

    startingFileInd=-1
    startingVecPosition=-1
    lag=-1
    smrFile=oneTFolder+"/summary_"+obs_name+".txt"
    summaryFileExists=os.path.isfile(smrFile)
    if summaryFileExists==False:
        return startingFileInd,startingVecPosition,-1

    with open(smrFile,"r") as fptr:
        lines=fptr.readlines()
    for oneLine in lines:
        #match startingFileInd
        matchStartingFileInd=re.search(r"startingFileInd=(\d+)",oneLine)
        if matchStartingFileInd:
            startingFileInd=int(matchStartingFileInd.group(1))
        #match startingVecPosition
        matchStartingVecPosition=re.search(r"startingVecPosition=(\d+)",oneLine)
        if matchStartingVecPosition:
            startingVecPosition=int(matchStartingVecPosition.group(1))

        #match lag
        matchLag=re.search(r"lag=(\d+)",oneLine)
        if matchLag:
            lag=int(matchLag.group(1))
    return startingFileInd, startingVecPosition,lag


def sort_data_files_by_lpEnd(oneTFolder,obs_name):
    """

    :param oneTFolder: Txxx
    :param obs_name: data files sorted by loopEnd
    :return:
    """

    dataFolderName=oneTFolder+"/"+obs_name+"_dataFiles/"
    dataFilesAll=[]
    loopEndAll=[]

    for oneDataFile in glob.glob(dataFolderName+"/*.csv"):
        dataFilesAll.append(oneDataFile)
        matchEnd=re.search(r"loopEnd(\d+)",oneDataFile)
        if matchEnd:
            loopEndAll.append(int(matchEnd.group(1)))


    endInds=np.argsort(loopEndAll)
    # loopStartSorted=[loopStartAll[i] for i in startInds]
    sortedDataFiles=[dataFilesAll[i] for i in endInds]

    return sortedDataFiles




def U_dist_data2jsonForOneT(oneTFolder,oneTStr,startingFileInd,startingVecPosition,lag):
    TRoot=oneTFolder
    sortedDataFilesToRead=sort_data_files_by_lpEnd(TRoot,obs_U_dist)
    startingFileName=sortedDataFilesToRead[startingFileInd]
    # print("startingFileInd="+str(startingFileInd))
    # print("startingVecPosition="+str(startingVecPosition))
    #read the starting U_dist csv file
    in_dfStart=pd.read_csv(startingFileName,dtype={"U":float,"L":float,"y0":float,"z0":float,"y1":float})


    UVec=np.array(in_dfStart.loc[startingVecPosition:,"U"])
    LVec=np.array(in_dfStart.loc[startingVecPosition:,"L"])
    y0Vec=np.array(in_dfStart.loc[startingVecPosition:,"y0"])
    z0Vec=np.array(in_dfStart.loc[startingVecPosition:,"z0"])
    y1Vec=np.array(in_dfStart.loc[startingVecPosition:,"y1"])

    #read the rest of the csv files
    for csv_file in sortedDataFilesToRead[(startingFileInd+1):]:
        in_df=pd.read_csv(csv_file,dtype={"U":float,"L":float,"y0":float,"z0":float,"y1":float})
        in_U=np.array(in_df.loc[:,"U"])
        in_L=np.array(in_df.loc[:,"L"])
        in_y0=np.array(in_df.loc[:,"y0"])
        in_z0=np.array(in_df.loc[:,"z0"])
        in_y1=np.array(in_df.loc[:,"y1"])

        UVec=np.r_[UVec,in_U]
        LVec=np.r_[LVec,in_L]
        y0Vec=np.r_[y0Vec,in_y0]
        z0Vec=np.r_[z0Vec,in_z0]
        y1Vec=np.r_[y1Vec,in_y1]

    UVecSelected=UVec[::lag]
    LVecSelected=LVec[::lag]
    y0VecSelected=y0Vec[::lag]
    z0VecSelected=z0Vec[::lag]
    y1VecSelected=y1Vec[::lag]
    outJsonDataRoot=rowDirRoot+"/jsonOutAll/"

    outJsonFolder=outJsonDataRoot+"/"+oneTStr+"/"+obs_U_dist+"/"
    Path(outJsonFolder).mkdir(parents=True, exist_ok=True)
    outJsonFile=outJsonFolder+"/"+obs_U_dist+"Data.json"
    dataOut={
        "U":list(UVecSelected),
        "L":list(LVecSelected),
        "y0":list(y0VecSelected),
        "z0":list(z0VecSelected),
        "y1":list(y1VecSelected)
    }
    with open(outJsonFile,"w+") as fptr:
        json.dump(dataOut,fptr,indent=4)

for k in range(0,len(sortedTFiles)):
    tStart=datetime.now()
    oneTFolder=sortedTFiles[k]
    oneTStr=sortedTStrings[k]

    startingfileIndTmp,startingVecIndTmp,lagTmp=parseSummary(oneTFolder,obs_U_dist)
    if startingfileIndTmp<0:
        print("summary file does not exist for "+oneTStr+" "+obs_U_dist)
        continue

    U_dist_data2jsonForOneT(oneTFolder,oneTStr,startingfileIndTmp,startingVecIndTmp,lagTmp)
    tEnd=datetime.now()
    print("processed T="+str(sortedTVals[k])+": ",tEnd-tStart)