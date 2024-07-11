import pickle
import numpy as np
from datetime import datetime

import pandas as pd
import statsmodels.api as sm
import sys
import re
import warnings
from scipy.stats import ks_2samp
import glob
from pathlib import Path
import os
import json

#This script checks if U, L, y0,z0,y1 values reach equilibrium and writes summary file of dist


argErrCode=2
sameErrCode=3
if (len(sys.argv)!=3):
    print("wrong number of arguments")
    exit(argErrCode)


jsonFromSummaryLast=json.loads(sys.argv[1])
jsonDataFromConf=json.loads(sys.argv[2])

TDirRoot=jsonFromSummaryLast["TDirRoot"]
U_dist_dataDir=jsonFromSummaryLast["U_dist_dataDir"]
effective_data_num_required=int(jsonDataFromConf["effective_data_num_required"])


summary_U_distFile=TDirRoot+"/summary_U_dist.txt"


def sort_data_files_by_loopEnd(oneDir):
    dataFilesAll=[]
    loopEndAll=[]
    for oneDataFile in glob.glob(oneDir+"/*.csv"):
        # print(oneDataFile)
        dataFilesAll.append(oneDataFile)
        matchEnd=re.search(r"loopEnd(\d+)",oneDataFile)
        if matchEnd:
            indTmp=int(matchEnd.group(1))
            loopEndAll.append(indTmp)
    endInds=np.argsort(loopEndAll)
    sortedDataFiles=[dataFilesAll[i] for i in endInds]
    return sortedDataFiles


def parseSummaryU_Dist():
    startingFileInd=-1
    startingVecPosition=-1

    summaryFileExists=os.path.isfile(summary_U_distFile)
    if summaryFileExists==False:
        return startingFileInd,startingVecPosition

    with open(summary_U_distFile,"r") as fptr:
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

    return startingFileInd, startingVecPosition



def checkU_distDataFilesForOneT(U_dist_csv_dir):
    """

    :param dist_csv_dir:
    :return:
    """
    U_dist_sortedDataFilesToRead=sort_data_files_by_loopEnd(U_dist_csv_dir)
    if len(U_dist_sortedDataFilesToRead)==0:
        print("no data for U_dist.")
        exit(0)

    startingFileInd,startingVecPosition=parseSummaryU_Dist()

    if startingFileInd<0:
        #we guess that the equilibrium starts at this file
        startingFileInd=int(len(U_dist_sortedDataFilesToRead)/2)
    startingFileName=U_dist_sortedDataFilesToRead[startingFileInd]
    # print(startingFileName)
    #read the starting U_dist csv file
    in_dfStart=pd.read_csv(startingFileName,dtype={"U":float,"L":float,"y0":float,"z0":float,"y1":float})

    in_nRowStart,in_nColStart=in_dfStart.shape
    if startingVecPosition<0:
        #we guess equilibrium starts at this position
        startingVecPosition=int(in_nRowStart/2)

    UVec=np.array(in_dfStart.loc[startingVecPosition:,"U"])
    LVec=np.array(in_dfStart.loc[startingVecPosition:,"L"])
    y0Vec=np.array(in_dfStart.loc[startingVecPosition:,"y0"])
    z0Vec=np.array(in_dfStart.loc[startingVecPosition:,"z0"])
    y1Vec=np.array(in_dfStart.loc[startingVecPosition:,"y1"])

    #read the rest of the csv files
    for csv_file in U_dist_sortedDataFilesToRead[(startingFileInd+1):]:
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


    NLags=int(len(LVec)*3/4)
    eps=1e-3
    lagVal=-1
    pThreshHold=0.1
    same=False
    with warnings.catch_warnings():
        warnings.filterwarnings("error")
    try:
        acfOfVecU=sm.tsa.acf(UVec,nlags=NLags)
    except Warning as w:
        same=True

    with warnings.catch_warnings():
        warnings.filterwarnings("error")
    try:
        acfOfVecL=sm.tsa.acf(LVec,nlags=NLags)
    except Warning as w:
        same=True

    with warnings.catch_warnings():
        warnings.filterwarnings("error")
    try:
        acfOfVecy0=sm.tsa.acf(y0Vec,nlags=NLags)
    except Warning as w:
        same=True

    with warnings.catch_warnings():
        warnings.filterwarnings("error")
    try:
        acfOfVecz0=sm.tsa.acf(z0Vec,nlags=NLags)
    except Warning as w:
        same=True

    with warnings.catch_warnings():
        warnings.filterwarnings("error")
    try:
        acfOfVecy1=sm.tsa.acf(y1Vec,nlags=NLags)
    except Warning as w:
        same=True

    #all values are the same, exit with err code
    if same==True:
        with open(summary_U_distFile,"w+") as fptr:
            msg="error: same\n"
            fptr.writelines(msg)

    acfOfVecLAbs=np.abs(acfOfVecL)
    acfOfVecy0Abs=np.abs(acfOfVecy0)
    acfOfVecz0Abs=np.abs(acfOfVecz0)
    acfOfVecy1Abs=np.abs(acfOfVecy1)
    acfOfVecUAbs=np.abs(acfOfVecU)

    minAutcL=np.min(acfOfVecLAbs)
    minAutcy0=np.min(acfOfVecy0Abs)
    minAutcz0=np.min(acfOfVecz0Abs)
    minAutcy1=np.min(acfOfVecy1Abs)
    minAutcU=np.min(acfOfVecUAbs)

    # print(minAutcL)
    # print(minAutcy0)
    # print(minAutcz0)
    # print(minAutcy1)
    # print(minAutcU)
    if minAutcL<eps and minAutcy0< eps \
            and minAutcz0<eps and minAutcy1<eps and minAutcU<eps:
        lagL=np.where(acfOfVecLAbs<=eps)[0][0]
        lagy0=np.where(acfOfVecy0Abs<=eps)[0][0]
        lagz0=np.where(acfOfVecz0Abs<=eps)[0][0]
        lagy1=np.where(acfOfVecy1Abs<=eps)[0][0]
        lagU=np.where(acfOfVecUAbs<=eps)[0][0]

        lagVal=np.max([lagL,lagy0,lagz0,lagy1,lagU])

        # #     #select values by lagVal
        LVecSelected=LVec[::lagVal]
        y0VecSelected=y0Vec[::lagVal]
        z0VecSelected=z0Vec[::lagVal]
        y1VecSelected=y1Vec[::lagVal]
        UVecSelected=UVec[::lagVal]

        lengthTmp=len(LVecSelected)
        if lengthTmp%2==1:
            lengthTmp-=1
        lenPart=int(lengthTmp/2)

        LVecValsToCompute=LVecSelected[-lengthTmp:]
        y0VecValsToCompute=y0VecSelected[-lengthTmp:]
        z0VecValsToCompute=z0VecSelected[-lengthTmp:]
        y1VecValsToCompute=y1VecSelected[-lengthTmp:]
        UVecValsToCompute=UVecSelected[-lengthTmp:]

        #     # #test distributions

        #test L
        selectedLVecPart0=LVecValsToCompute[:lenPart]
        selectedLVecPart1=LVecValsToCompute[lenPart:]
        resultL=ks_2samp(selectedLVecPart0,selectedLVecPart1)
        # print(resultL)

        #test y0
        selectedy0VecPart0=y0VecValsToCompute[:lenPart]
        selectedy0VecPart1=y0VecValsToCompute[lenPart:]
        resulty0=ks_2samp(selectedy0VecPart0,selectedy0VecPart1)

        #test z0
        selectedz0VecPart0=z0VecValsToCompute[:lenPart]
        selectedz0VecPart1=z0VecValsToCompute[lenPart:]
        resultz0=ks_2samp(selectedz0VecPart0,selectedz0VecPart1)


        #test y1
        selectedy1VecPart0=y1VecValsToCompute[:lenPart]
        selectedy1VecPart1=y1VecValsToCompute[lenPart:]
        resulty1=ks_2samp(selectedy1VecPart0,selectedy1VecPart1)


        #test U
        selectedUVecPart0=UVecValsToCompute[:lenPart]
        selectedUVecPart1=UVecValsToCompute[lenPart:]
        resultU=ks_2samp(selectedUVecPart0,selectedUVecPart1)

        numDataPoints=len(selectedLVecPart0)+len(selectedLVecPart1)
        pValsAll=np.array([resultL.pvalue,resulty0.pvalue,resultz0.pvalue,resulty1.pvalue,resultU.pvalue])

        if np.min(pValsAll)>=pThreshHold and numDataPoints>=200:
            if numDataPoints>=effective_data_num_required:
                newDataPointNum=0
            else:
                newDataPointNum=effective_data_num_required-numDataPoints
            msg="equilibrium\n" \
                +"lag="+str(lagVal)+"\n" \
                +"numDataPoints="+str(numDataPoints)+"\n" \
                +"startingFileInd="+str(startingFileInd)+"\n" \
                +"startingVecPosition="+str(startingVecPosition)+"\n" \
                +"newDataPointNum="+str(newDataPointNum)+"\n"

            with open(summary_U_distFile,"w+") as fptr:
                fptr.writelines(msg)
            exit(0)

        continueMsg="continue\n"
        if np.min(pValsAll)<pThreshHold:
            #not the same distribution
            continueMsg+="p value: "+str(np.min(pValsAll))+"\n"
        if numDataPoints<200:
            #not enough data number
            continueMsg+="numDataPoints="+str(numDataPoints)+" too low\n"
        with open(summary_U_distFile,"w+") as fptr:
            fptr.writelines(continueMsg)
        exit(0)

    else:
        highMsg="high correlation"
        with open(summary_U_distFile,"w+") as fptr:
            fptr.writelines(msg)
        exit(0)


checkU_distDataFilesForOneT(U_dist_dataDir)