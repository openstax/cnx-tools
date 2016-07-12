import sys
import requests
import json
import csv
from openpyxl import Workbook
from openpyxl.compat import range
from openpyxl import load_workbook

def parseInput():
    isCol = True
    prompt0 = "Do you want to input module IDs or collection IDs?"
    prompt1 = "(Type \"m\" or \"c\") "
    col = ""
    while (col != "m" and col != "c"):
        col = repeatPrompt(prompt0, prompt1)[0].lower()
    if (col == "m"):
        isCol = False
    elif (col == "c"):
        isCol = True

    if isCol:
        prompt3 = "Input one collection ID."
        collectionId = []
        while (len(collectionId) != 1):
            collectionId = repeatPrompt(prompt3)
        prompt4 = "Do you want all of the module IDs in this collection?"
        getModules = ""
        while (getModules != "yes" and getModules != "no"):
            getModules = repeatPrompt(prompt4)[0]
            print getModules
        if (getModules == "yes"):
            return isCol, collectionId, True
        else:
            return isCol, collectionId, False

    else:
        excel = ''
        prompt2 = "Do you want to import the module IDs from an excel sheet?"
        while (excel != "yes" and excel != "no"):
            excel = repeatPrompt(prompt2)[0]
        if (excel == "yes"):
            moduleIdList = importExcel()
            print moduleIdList
        else:
            prompt3 = "Input the module IDs separated by spaces."
            moduleIdList = []
            while not moduleIdList:
                moduleIdList = repeatPrompt(prompt3)
            print moduleIdList
        return isCol, moduleIdList, True

def repeatPrompt(prompt0, prompt1 = "", isFileName = False):
    response = ""
    while (len(response) == 0):
        print prompt0
        if (isFileName):
            response = raw_input(prompt1)
        else:
            response = raw_input(prompt1).replace(",", "").split()
    return response

def importExcel():
    prompt7 = "what file do you want to import from?"
    filename = repeatPrompt(prompt7, '', True)
    if (filename[-5:] != '.xlsx'):
        filename += '.xlsx'
    wb2 = load_workbook(filename)
    prompt8 = "Which worksheet?"
    sheetname = repeatPrompt(prompt8, '', True)
    sheetNames = wb2.get_sheet_names()
    if sheetname not in sheetNames:
        output = "A worksheet with the name '%s' does not exist in the file." %sheetname
        sys.exit(output)
    else:
        ws = wb2.get_sheet_by_name(sheetname)
        prompt9 = "Type the title of the column with the IDs you want to convert."
        title = repeatPrompt(prompt9, '', True)
        column = 0
        for col in ws.columns:
            if (title == col[0].value):
                column = col
                break
        if (column == 0):
            sys.exit("A column with that title doesn't exist.")
        ids = []
        for row in column[1:]:
            moduleId = row.value.encode('ascii','ignore')
            ids.append(moduleId)
        return ids

def convertModuleIdList(moduleIdList):
    # check that list is not empty
    # Check if the ids are valid
    # figure out which form it is in
    convertedList = []
    errorIdList = []
    count = 0
    if (len(moduleIdList) == 0):
        print "There were no IDs entered."
        sys.exit()
    for moduleId in moduleIdList:
        isLegacy = True
        if (moduleId[0].lower() != "m"):
            isLegacy = False
        if isLegacy:
            url = 'https://archive.cnx.org/content/%s/latest' % moduleId
        else:
            url = 'https://archive.cnx.org/contents/%s' % moduleId
        r = requests.get(url, allow_redirects=False)
        if (r.status_code != requests.codes.ok and r.status_code != 302):
            errorIdList.append(moduleId)
            continue
        r3 = requests.get(r.headers['location']+'.json')
        if (r3.status_code != requests.codes.ok):
            errorIdList.append(moduleId)
            continue
        responseJson = r3.json()
        moduleDict = {}
        moduleDict['Short ID'] = responseJson['shortId']
        moduleDict['Long ID'] = responseJson['id']
        moduleDict['Legacy ID'] = responseJson['legacy_id']
        convertedList.append(moduleDict)
        count += 1
    #print convertedList
    return convertedList, errorIdList, count

def convertColId(colId):
    #get the other forms of the collection id from json
    #make a list of all of the modules inside the collection
    #send the list to convertModuleIdList
    errorIdList = []
    isLegacy = True
    if (colId[0:3].lower() != "col"): #legacy id
        isLegacy = False

    if isLegacy: #legacyId
        url = 'https://archive.cnx.org/content/%s/latest' % colId
    else:
        url = 'https://archive.cnx.org/contents/%s' % colId
    r = requests.get(url, allow_redirects=False)
    if (r.status_code != requests.codes.ok and r.status_code != 302):
        errorIdList.append(colId)
        sys.exit("The Collection ID returned an error.")
    r3 = requests.get(r.headers['location']+'.json')
    if (r3.status_code != requests.codes.ok):
        errorIdList.append(colId)
        sys.exit("The Collection ID returned an error.")
    responseJson = r3.json()
    moduleDict = {}
    moduleDict['Short ID'] = responseJson['shortId']
    moduleDict['Long ID'] = responseJson['id']
    moduleDict['Legacy ID'] = responseJson['legacy_id']
    convertedList = [moduleDict]

    # get all of the module id's
    # get inside "tree" and then "contents" in json
    # get the id from preface if it exists
    # then get id from each bracket in contents inside
    contents = responseJson['tree']['contents']
    moduleIdList = []
    for section in contents:
        findModuleIds(section, moduleIdList)
    convertedModules, moduleErrors, count = convertModuleIdList(moduleIdList)
    errorIdList.extend(moduleErrors)
    convertedList.append(convertedModules)
    return convertedList, errorIdList, count

def findModuleIds(section, moduleIdList):
        moduleShort = section['shortId']
        if (moduleShort != 'subcol'):
            moduleIdList.append(moduleShort)
        else:
            for subSection in section['contents']:
                findModuleIds(subSection, moduleIdList)


def printResults(idList, errorList, printModules):
    if isCol:
        colDict = idList[0]
        print "Collection:"
        print  "Legacy ID   Long ID                                 Short ID"
        print colDict['Legacy ID'], "  ", colDict['Long ID'], "  ", colDict['Short ID']
        moduleList = idList[1]
    else:
        moduleList = idList
    if (printModules):
        if (len(moduleList) != 0):
            print "Modules:"
            print "Legacy ID   Long ID                                 Short ID"
            for modId in moduleList:
                print modId['Legacy ID'], "    ", modId['Long ID'], "  ", modId['Short ID']
        printErrors(errorList)

def printErrors(errorList):
    if (len(errorList) != 0):
        print "The following IDs returned an error:"
        for errorId in errorList:
            print errorId


def parseExportInput():
    prompt4 = "Pick the output format."
    prompt5 = "(type 'csv', 'excel', or 'terminal') "
    export = ''
    while (export != 'csv' and export != 'excel' and export != 'terminal'):
        export = repeatPrompt(prompt4, prompt5, True).lower()
    if (export == 'terminal'):
        return 't', ''
    else:
        filename = ''
        prompt6 = 'Type the filename you want for the exported file.'
        while (len(filename) == 0):
            filename = repeatPrompt(prompt6, '', True)
        if (export == 'excel'):
            if (filename[-5:] != '.xlsx'):
                filename += '.xlsx'
        else:
            if (filename[-4:] != '.csv'):
                filename += '.csv'
        return export[0], filename

def exportAsCsv(filename, idList, errorIdList):
    with open(filename, 'wb') as f:  # Just use 'w' mode in 3.x
        w = csv.DictWriter(f, ['Legacy ID', 'Long ID', 'Short ID'])
        w.writeheader()
        if isCol:
            colDict = idList[0]
            w.writerow(colDict)
            moduleDictList = idList[1]
        else:
            moduleDictList = idList
        if (len(moduleDictList) == 0):
            print 'There are no converted module IDs to output.'
        else:
            w.writerows(moduleDictList)
    print "Finished writing to file!"
    f.close()
    printErrors(errorIdList)

def exportAsExcel(filename, idList, errorIdList, count):
    wb = Workbook()
    dest_filename = filename
    ws1 = wb.active
    ws1.title = "Converted IDs"
    header = ['Legacy ID', 'Long ID', 'Short ID']
    for col in range(1, 4):
        _ = ws1.cell(column=col, row=1, value="%s" % header[col - 1])
    if isCol:
        colDict = idList[0]
        for col in range(1, 4):
            _ = ws1.cell(column=col, row=2, value="%s" % colDict[header[col - 1]])
        moduleDictList = idList[1]
        startRow = 3
    else:
        moduleDictList = idList
        startRow = 2
    if (len(moduleDictList) == 0):
        print 'There are no converted module IDs to output.'
    else:
        for row in range(startRow, count + startRow):
            for col in range(1, 4):
                _ = ws1.cell(column=col, row=row, value="%s" % moduleDictList[row - startRow][header[col - 1]])
    wb.save(filename = dest_filename)
    print "Finished writing to file!"
    printErrors(errorIdList)


#flags?
if __name__ == '__main__':
    isCol, idList, printModules = parseInput()
    if (len(idList) == 0):
        sys.exit()
    export, filename = parseExportInput()
    if isCol:
        convertedList, errorIdList, count = convertColId(idList[0])
    else:
        convertedList, errorIdList, count = convertModuleIdList(idList)
    if (export == 'c'):
        exportAsCsv(filename, convertedList, errorIdList)
    elif (export == 'e'):
        exportAsExcel(filename, convertedList, errorIdList, count)
    else:
        printResults(convertedList, errorIdList, printModules)
