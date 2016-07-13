import sys
import warnings
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
    col = handleInputs(prompt0, ["m", "c"], prompt1)
    if (col == "m"):
        isCol = False
    elif (col == "c"):
        isCol = True

    if isCol:
        prompt3 = "Input one collection ID."
        collectionId = []
        while (len(collectionId) != 1):
            collectionId = repeatPrompt(prompt3, '', False)
        prompt4 = "Do you want all of the module IDs in this collection?"
        getModules = handleInputs(prompt4, ['yes', 'no'])
        if (getModules == "yes"):
            return isCol, collectionId, True
        else:
            return isCol, collectionId, False

    else:

        prompt2 = "Do you want to import the module IDs from an excel sheet?"
        excel = handleInputs(prompt2, ['yes', 'no'])
        if (excel == "yes"):
            moduleIdList = importExcel()
            print moduleIdList
        else:
            prompt3 = "Input the module IDs separated by spaces."
            moduleIdList = []
            moduleIdList = handleInputs(prompt3, 0, '', False)
            print moduleIdList
        return isCol, moduleIdList, True

def repeatPrompt(prompt0, prompt1 = "", notModules = True):
    response = ""
    while (len(response) == 0):
        print prompt0
        if (notModules):
            response = raw_input(prompt1)
        else:
            response = raw_input(prompt1).replace(",", "").split()
    return response

def handleInputs(prompt0, expected, prompt1 = '', notModules = True):
    if not notModules: # to get module and col ids
        return repeatPrompt(prompt0, prompt1, notModules)
    else:
        if (type(expected) is int): # filenames
            inputs = []
            while (len(inputs) != expected):
                inputs = repeatPrompt(prompt0, prompt1, notModules).replace(', ', ',').split(',')
            return inputs
        else: # questions like yes or no
            response = ''
            while (response not in expected):
                response = repeatPrompt(prompt0, prompt1, notModules).lower()
            return response


def importExcel():
    prompt7 = "Type the file name, worksheet name, and title of the column with the IDs separated by commas."
    inputs = handleInputs(prompt7, 3, '', True)
    filename = inputs[0]
    sheetname = inputs[1]
    title = inputs[2]
    if (filename[-5:] != '.xlsx'):
        filename += '.xlsx'
    wb2 = load_workbook(filename)
    sheetNames = wb2.get_sheet_names()
    if sheetname not in sheetNames:
        output = "A worksheet with the name '%s' does not exist in the file." %sheetname
        sys.exit(output)
    else:
        ws = wb2.get_sheet_by_name(sheetname)
        column = 0
        for col in ws.columns:
            if (title == col[0].value):
                column = col
                break
        if (column == 0):
            sys.exit("A column with that title doesn't exist.")
        ids = []
        for row in column[1:]:
            moduleId = row.value.encode('ascii','ignore').replace(' ', '')
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
    export = handleInputs(prompt4, ['csv', 'excel', 'terminal'], prompt5, True)
    if (export == 'terminal'):
        return 't', ''
    else:
        filename = ''
        prompt6 = 'Type the filename you want for the exported file.'
        filename = handleInputs(prompt6, 1, '', True)[0]
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
    warnings.simplefilter('ignore', UserWarning)
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
