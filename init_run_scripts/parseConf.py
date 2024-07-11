import re
import sys
# inConfFile="./confFiles/run0.mc.conf"
import json
import os
#this script parse conf file and return the parameters as json data
fmtErrStr="format error: "
fmtCode=1
valueMissingCode=2
paramErrCode=3
fileNotExistErrCode=4
if (len(sys.argv)!=2):
    print("wrong number of arguments.")
    exit(paramErrCode)
inConfFile=sys.argv[1]

def removeCommentsAndEmptyLines(file):
    """

    :param file: conf file
    :return: contents in file, with empty lines and comments removed
    """
    with open(file,"r") as fptr:
        lines= fptr.readlines()

    linesToReturn=[]
    for oneLine in lines:
        oneLine = re.sub(r'#.*$', '', oneLine).strip()
        if not oneLine:
            continue
        else:
            linesToReturn.append(oneLine)
    return linesToReturn


def parseConfContents(file):
    """

    :param file: conf file
    :return:
    """
    file_exists = os.path.exists(file)
    if not file_exists:
        print(file+" does not exist,")
        exit(fileNotExistErrCode)
    lineWithCommentsRemoved=removeCommentsAndEmptyLines(file)
    TStr=""
    eraseData=""
    searchReadSmrFile=""
    obs_name=""
    confFileName=file
    effective_data_num_required=""
    loop_to_write=""
    default_flush_num=""
    potFuncName=""
    #the following parameters are specific for potential function V2
    a1Str=""
    a2Str=""
    c1Str=""
    c2Str=""
    coefsJson={}#containing coefficient values for the potential function

    float_pattern = r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?'
    boolean_pattern = r'(true|false)'
    for oneLine in lineWithCommentsRemoved:
        matchLine=re.match(r'(\w+)\s*=\s*(.+)', oneLine)
        if matchLine:
            key = matchLine.group(1).strip()
            value = matchLine.group(2).strip()

            #match T
            if key=="T":
                match_TValPattern=re.match(r"T\s*=\s*([-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)$",oneLine)
                if match_TValPattern:
                    TStr=match_TValPattern.group(1)
                else:
                    print(fmtErrStr+oneLine)
                    exit(fmtCode)
                # print(TStr)
            #match erase_data_if_exist
            if key=="erase_data_if_exist":
                matchErase=re.match(boolean_pattern,value,re.IGNORECASE)
                if matchErase:
                    eraseData=matchErase.group(1)
                    eraseData=eraseData.capitalize()
                else:
                    print(fmtErrStr+oneLine)
                    exit(fmtCode)

            #match search_and_read_summary_file
            if key=="search_and_read_summary_file":
                matchSmr=re.match(boolean_pattern,value,re.IGNORECASE)
                if matchSmr:
                    searchReadSmrFile=matchSmr.group(1)
                    searchReadSmrFile=searchReadSmrFile.capitalize()
                else:
                    print(fmtErrStr+oneLine)
                    exit(fmtCode)


            #match observable_name
            if key=="observable_name":
                #if matching a non word character
                if re.search(r"[^\w]",value):
                    print(fmtErrStr+oneLine)
                    exit(fmtCode)

                obs_name=value

            #match potential function name
            if key=="potential_function_name":
                #if matching a non word character
                if re.search(r"[^\w]",value):
                    print(fmtErrStr+oneLine)
                    exit(fmtCode)
                potFuncName=value

            #match loop_to_write
            if key=="loop_to_write":
                if re.search(r"[^\d]",value):
                    print(fmtErrStr+oneLine)
                    exit(fmtCode)
                loop_to_write=value
            #match default_flush_num
            if key=="default_flush_num":
                if re.search(r"[^\d]",value):
                    print(fmtErrStr+oneLine)
                    exit(fmtCode)
                default_flush_num=value

            #match effective_data_num_required
            if key=="effective_data_num_required":
                if re.search(r"[^\d]",value):
                    print(fmtErrStr+oneLine)
                    exit(fmtCode)
                effective_data_num_required=value


            #the following part are specific for potential function V2
            #match a1
            if key=="a1":
                match_a1ValPattern=re.match(r"a1\s*=\s*([-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)$",oneLine)
                if match_a1ValPattern:
                    a1Str=match_a1ValPattern.group(1)
                    # print(a1Str)
                else:
                    print(fmtErrStr+oneLine)
                    exit(fmtCode)

            #match a2
            if key=="a2":
                match_a2ValPattern=re.match(r"a2\s*=\s*([-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)$",oneLine)
                if match_a2ValPattern:
                    a2Str=match_a2ValPattern.group(1)
                else:
                    print(fmtErrStr+oneLine)
                    exit(fmtCode)

            #match c1
            if key=="c1":
                match_c1ValPattern=re.match(r"c1\s*=\s*([-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)$",oneLine)
                if match_c1ValPattern:
                    c1Str=match_c1ValPattern.group(1)
                else:
                    print(fmtErrStr+oneLine)
                    exit(fmtCode)

            #match c2
            if key=="c2":
                match_c2ValPattern=re.match(r"c2\s*=\s*([-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?)$",oneLine)
                if match_c2ValPattern:
                    c2Str=match_c2ValPattern.group(1)
                else:
                    print(fmtErrStr+oneLine)
                    exit(fmtCode)




        else:
            print("line: "+oneLine+" is discarded.")
            continue
    if TStr=="":
        print("T not found in "+str(file))
        exit(valueMissingCode)
    if eraseData=="":
        print("erase_data_if_exist not found in "+str(file))
        exit(valueMissingCode)
    if searchReadSmrFile=="":
        print("search_and_read_summary_file not found in "+str(file))
        exit(valueMissingCode)

    #do not check if observable exists
    if potFuncName=="":
        print("potential_function_name not found in "+str(file))
        exit(valueMissingCode)

    if effective_data_num_required=="":
        print("effective_data_num_required not found in "+str(file))
        exit(valueMissingCode)

    if loop_to_write=="":
        print("loop_to_write not found in "+str(file))
        exit(valueMissingCode)

    if default_flush_num=="":
        print("default_flush_num not found in "+str(file))
        exit(valueMissingCode)
    #the following part are specific for potential function V2
    if a1Str=="":
        print("a1 not found in "+str(file))
        exit(valueMissingCode)

    if a2Str=="":
        print("a2 not found in "+str(file))
        exit(valueMissingCode)

    if c1Str=="":
        print("c1 not found in "+str(file))
        exit(valueMissingCode)
    if c2Str=="":
        print("c2 not found in "+str(file))
        exit(valueMissingCode)

    coefsJson={
        "a1":a1Str,
        "a2":a2Str,
        "c1":c1Str,
        "c2":c2Str
    }
    if obs_name=="":
        dictTmp={
            "T":TStr,
            "erase_data_if_exist":eraseData,
            "search_and_read_summary_file":searchReadSmrFile,
            "potential_function_name":potFuncName,
            "effective_data_num_required":effective_data_num_required,
            "loop_to_write":loop_to_write,
            "default_flush_num":default_flush_num,
            "coefsJson":json.dumps(coefsJson),
            "confFileName":file

        }
        return dictTmp
    else:
        dictTmp={
            "T":TStr,
            "erase_data_if_exist":eraseData,
            "search_and_read_summary_file":searchReadSmrFile,
            "observable_name":obs_name,
            "potential_function_name":potFuncName,
            "effective_data_num_required":effective_data_num_required,
            "loop_to_write":loop_to_write,
            "default_flush_num":default_flush_num,
            "coefsJson":json.dumps(coefsJson),
            "confFileName":file


        }
        return dictTmp



jsonDataFromConf=parseConfContents(inConfFile)

confJsonStr2stdout="jsonDataFromConf="+json.dumps(jsonDataFromConf)

print(confJsonStr2stdout)