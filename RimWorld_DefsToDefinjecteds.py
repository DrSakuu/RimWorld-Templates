import os
import sys
import shutil
import xml.etree.ElementTree as ET

import rwtutil

__author__ = 'Sakuukuli'


def printhelp():
    """ Print information about the script.
    """
    print("RimWorld Translation Template Script")
    print("Copies all Def's from the RimWorld Core mod folder and creates DefInject templates for them.")
    print("Usage: RimWorld_DefsToDefInjecteds.py <RimWorld installation folder> <Folder for templates>")


def writeheader(file):
    """Writes the first lines of a DefInjected file.

    :param file: File to write to
    """
    file.write('<?xml version="1.0" encoding="utf-8" ?>\n')
    file.write('<LanguageData>\n')
    file.write('    \n')


def writedeflabel(file, defname, labeltype, labeltext):
    """ Writes the translation data of a DefInjected file.

    Uses the correct syntax:
    <Ocean.label>ocean</Ocean.label>
    <Ocean.description>Open ocean. Great for fish - not so great for you.</Ocean.description>

    :param file: File to write to
    :param defname: Name of the Def to write
    :param labeltype: Tag of the label to write
    :param labeltext: Text inside tags
    """
    # Revert capitalization
    labeltype = labeltype[:1].lower() + labeltype[1:]
    file.write('    <' + defname + '.' + labeltype + '>' + labeltext + '</' + defname + '.' + labeltype + '>\n')


def writefooter(file):
    """ Writes the last lines of a DefInjected file.

    :param file: File to write to
    """
    file.write('</LanguageData>\n')


# Save the arguments
arguments = sys.argv[1:]
# Save the directories in variables
if len(arguments) == 2:
    defsDirPath = arguments[0]
    translationDirPath = arguments[1]
# If incorrect number of arguments then print help
elif not arguments:
    printhelp()
    sys.exit(2)
else:
    rwtutil.print_help_error()
    sys.exit(2)

# Print information about the script
print("--------------------------------------------------------------------")
print("RimWorld Translation Template Script")
print("")
print("RimWorld installation folder is \"" + defsDirPath + "\"")
print("Templates will be created in folder \"" + translationDirPath + "\"")
print("--------------------------------------------------------------------")
print("")

# Move to the directories where the files are
defsDirPath = os.path.join(defsDirPath, 'Mods', 'Core', 'Defs')
translationDirPath = os.path.join(translationDirPath, 'DefInjected')

# Define list of labels that need to be translated
labels = ['label', 'labelMechanoids', 'labelMale', 'labelFemale', 'labelShort', 'skillLabel', 'description',
          'adjective', 'pawnLabel', 'gerundLabel', 'reportString', 'verb', 'gerund', 'deathMessage', 'pawnsPlural',
          'leaderTitle', 'jobString', 'quotation', 'beginLetterLabel', 'beginLetter', 'recoveryMessage', 'baseInspectLine',
          'graphLabelY', 'fixedName', 'letterLabel', 'letterText', 'letterLabelEnemy', 'arrivalTextEnemy',
          'letterLabelFriendly', 'arrivalTextFriendly', 'Description', 'endMessage', 'successfullyRemovedHediffMessage']
nestedstartlabels = ['injuryProps']
nestedlabels = ['destroyedLabel', 'destroyedOutLabel']
liststartlabels = ['helpTexts', 'comps', 'stages', 'degreeDatas', 'rulePack', 'lifeStages', 'scoreStages', 'verbs',
                   'hediffGivers', 'logRulesInitiator', 'logRulesRecipient', 'parts']
nestedliststartlabels = ['rulesStrings']
listlabels = ['label', 'description', 'labelTendedWell', 'labelTended', 'labelTendedWellInner', 'labelTendedInner',
              'labelSolidTendedWell', 'labelSolidTended', 'oldLabel', 'discoverLetterLabel', 'discoverLetterText',
              'letterLabel', 'letter', 'labelSocial', 'customLabel']

# Check if the entered RimWorld installation folder was correct
if not os.path.exists(defsDirPath):
    print("Invalid RimWorld installation folder.")
    sys.exit(2)
else:
    print("Valid installation folder.")
    print("")

# Remove existing translation
if os.path.exists(translationDirPath):
    shutil.rmtree(translationDirPath)
# Create the translation folder
os.makedirs(translationDirPath)

# Count the number of files
numfiles = 0
for p, ds, fs in os.walk(defsDirPath):
    for f in fs:
        if f.endswith('.xml'):
            numfiles += 1

# Go through all the folders one by one
# dirpath is the full path to the current def directory, dirnames is a list of directories in the current directory
# and filenames is a list of files
processedfiles = 0
for dirpath, dirnames, filenames in os.walk(defsDirPath):

    # Go through all the files one by one
    for filename in [f for f in filenames if f.endswith('.xml')]:

        # Parse the .xml file with ElementTree

        parser = ET.XMLParser(encoding="utf-8")
        defTree = ET.parse(os.path.join(dirpath, filename), parser=parser)
        defRoot = defTree.getroot()

        # Assume that the file doesn't have anything to translate
        haslabels = False
        # Go through the tags one by one and check if there is something to translate
        # If there is, change haslabels to True and stop searching
        for child in defRoot:
            defElement = child.find('defName')
            if defElement is None:
                defElement = child.find('DefName')
                if defElement is None:
                    continue

            for label in labels:
                if child.find(label) is not None:
                    haslabels = True
                    break

            if haslabels:
                break
            # If there were no tags found check for list thingies
            else:
                for liststartlabel in liststartlabels:
                    if child.find(liststartlabel) is not None:
                        haslabels = True
                        break

        # If the file has something to translate
        if haslabels:

            defTypeDict = {}

            # Go through the file tag by tag
            # child is ThingDef, TraitDef etc.
            for child in defRoot:
                if child.tag not in defTypeDict.keys():
                    defTypeDict[child.tag] = []
                extraDefList = []
                labelList = []
                # Look for the defName of the Def
                defElement = child.find('defName')
                # Check if we found anything
                if defElement is not None:
                    # Save the defname
                    defName = defElement.text
                else:
                    # Check for alternate capitalization
                    defElement = child.find('DefName')
                    if defElement is not None:
                        defName = defElement.text
                    else:
                        continue

                # Go through the labels one by one
                for label in labels:
                    # Look for the label in tags
                    labelElement = child.find(label)
                    # Check if we found anything
                    if labelElement is not None:
                        # Add the label and its text to the list
                        labelList.append((labelElement.tag, labelElement.text))
                # Go through list thingies one by one
                for liststartlabel in liststartlabels:
                    # Check if there are them
                    if child.find(liststartlabel) is not None:
                        liststart = child.find(liststartlabel)
                        # Store the elements of the list
                        listelements = liststart.findall('li')
                        if listelements:
                            for i, listelement in enumerate(listelements):
                                if listelement.text is not None:
                                    # If the list element has no children, it has the text to translate in itself
                                    if not list(listelement):
                                        labelList.append((liststartlabel + '.' + str(i), listelement.text))
                                    else:
                                        # Go through the in-list labels
                                        for listlabel in listlabels:
                                            # Look for them in the list
                                            if listelement.find(listlabel) is not None:
                                                # Store the label tag
                                                listsubelement = listelement.find(listlabel)
                                                labelList.append((liststartlabel + '.' + str(i)
                                                                  + '.' + listsubelement.tag, listsubelement.text))
                        else:
                            for nestedliststartlabel in nestedliststartlabels:
                                nestedliststart = liststart.find(nestedliststartlabel)
                                if liststart.find(nestedliststartlabel) is not None:
                                    nestedlistelements = nestedliststart.findall('li')
                                    if nestedlistelements:
                                        for i, nestedlistelement in enumerate(nestedlistelements):
                                            if nestedlistelement.text is not None:
                                                # If the list element has no children, it has the text to translate in itself
                                                if not list(nestedlistelement):
                                                    labelList.append((liststartlabel + '.' + nestedliststartlabel
                                                                      + '.' + str(i), nestedlistelement.text))

                for nestedstartlabel in nestedstartlabels:
                    nestedstart = child.find(nestedstartlabel)
                    if nestedstart is not None:
                        for nestedlabel in nestedlabels:
                            nestedelement = nestedstart.find(nestedlabel)
                            if nestedelement is not None:
                                labelList.append((nestedstartlabel + '.' + nestedelement.tag, nestedelement.text))

                if child.get('ParentName') in ['BasePawn', 'AnimalThingBase', 'BaseMechanoid', 'BaseInsect', 'BaseHare',
                                               'BaseBear']:
                    labelElement = child.find('label')
                    if defName not in ['Chicken', 'Megascarab', 'Megaspider', 'Spelopede', 'Mechanoid_Centipede',
                                       'Mechanoid_Scyther']:
                        if child.find('race').find('leatherLabel') is not None:
                            leatherLabel = child.find('race').find('leatherLabel').text
                        else:
                            leatherLabel = labelElement.text + ' leather'
                        extraLabelList = [('label', leatherLabel),
                                               ('description', 'Leather made from the skin of a ' + labelElement.text + '.'),
                                               ('stuffProps.stuffAdjective', leatherLabel)]
                        extraDefList.append((defName + '_Leather', extraLabelList))
                    if defName not in ['Mechanoid_Centipede', 'Mechanoid_Scyther']:
                        if child.find('race').find('meatLabel') is not None:
                            meatLabel = child.find('race').find('meatLabel').text
                        else:
                            meatLabel = labelElement.text + ' meat'
                        extraLabelList = [('label', meatLabel),
                                               ('description', 'Raw flesh of a ' + labelElement.text + '.')]
                        extraDefList.append((defName + '_Meat', extraLabelList))
                    extraLabelList = [('label', labelElement.text + ' corpse'),
                                           ('description', 'Dead body of a ' + labelElement.text + '.')]
                    extraDefList.append((defName + '_Corpse', extraLabelList))

                if child.get('ParentName') == 'StoneBlocksBase':
                    labelElement = child.find('label')
                    labelList.append(('stuffProps.stuffAdjective', labelElement.text[:-7]))

                if child.get('ParentName') == 'TileStoneBase':
                    labelList.append(('description', 'Solid stone tiles for a castle feeling. '
                                                     'Pretty to look at, but they take a long time to lay.'))

                if child.get('ParentName') == 'TableBase':
                    labelList.append(('description', 'People eat off tables when chairs are placed facing them.'))

                if child.get('ParentName') in ['ResourceBase', 'ResourceVerbBase']:
                    if child.find('stuffProps') is not None:
                        labelElement = child.find('label')
                        labelList.append(('stuffProps.stuffAdjective', labelElement.text))

                if child.get('ParentName') == 'Bite':
                    labelList.append(('deathMessage', '{0} has been bitten to death.'))

                if defName == 'CarpetDark':
                    stonelist = ['Sandstone', 'Granite', 'Limestone', 'Slate', 'Marble']
                    roughnesslist = [('Rough', 'rough'), ('RoughHewn', 'rough-hewn'), ('Smooth', 'smooth')]
                    for stone in stonelist:
                        for roughness in roughnesslist:
                            extraDefList.append((stone + '_' + roughness[0],
                                                 [('label', roughness[1] + ' ' + stone.lower())]))

                defTypeDict[child.tag].append((defName, labelList))
                defTypeDict[child.tag] += extraDefList

            for defType in defTypeDict.keys():

                if defTypeDict[defType]:
                    # Create the directory in the translationDir if it doesn't exist
                    if not os.path.exists(os.path.join(translationDirPath, defType)):
                        os.mkdir(os.path.join(translationDirPath, defType))

                    # Open the file for writing
                    if os.path.exists(os.path.join(translationDirPath, defType, filename)):
                        defInjectFile = open(os.path.join(translationDirPath, defType, filename), 'a',
                                             encoding="utf-8")
                    else:
                        defInjectFile = open(os.path.join(translationDirPath, defType, filename), 'w',
                                             encoding="utf-8")

                    # Write the header of the file
                    writeheader(defInjectFile)

                    for defName, labelList in defTypeDict[defType]:
                        for label, text in labelList:
                            writedeflabel(defInjectFile, defName, label, text)
                        defInjectFile.write('    \n')

                    # Close the translatable file
                    defInjectFile.close()

        processedfiles += 1
        rwtutil.print_progress("Collecting tags", processedfiles, numfiles)

for dirpath, dirnames, filenames in os.walk(translationDirPath):

    for filename in [f for f in filenames if f.endswith('.xml')]:
        defInjectFile = open(os.path.join(dirpath, filename), 'a',
                             encoding="utf-8")
        writefooter(defInjectFile)
        # Close the translatable file
        defInjectFile.close()

print("")
print("")

print("Successfully processed all files.")
