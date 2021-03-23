import pdftotext

import re

abbrPage = 6
startPage = 8

def checkLine(line):
    outLine = ""
    
    # Line of a rule without a 'heading'
    line = line.split()

    for word in line:
        alteredLine = False
        
        # Bullet point
        if word == '•':
            outLine += '\n  -'
            alteredLine = True
            continue

        # Abbreviations
        for key in abbrs:
            keySearch = re.search(key, word)
            if keySearch:
                outLine += ' {abbr}`' + word + ' (' + abbrs[keySearch.group()] + ')`'
                alteredLine = True
                break

        if not alteredLine:
            outLine += ' ' + word

    return outLine

# Load PDF
with open("rules.pdf", "rb") as f:
    abbrText = ""
    pdfText = ""

    currentLevelOne = ""
    ruleText = ""
    ruleGroup = ""
    headingPrintRule = False

    pdf = pdftotext.PDF(f)

    for i in range(abbrPage - 1, startPage - 1):
        abbrText += pdf[i]

    for i in range(startPage - 1, len(pdf)):
        pdfText += pdf[i]

    # Abbreviations parsing
    abbrs = {}
    
    for line in abbrText.splitlines():
        footerMatch = re.match(r'Formula Student Rules 2020 +'
                                'Version: (\d+\.?)* +'
                                '\d+ of \d+', line)
        if footerMatch:
            continue

        headerMatch = re.match(r'A BBREVIATIONS', line)
        if headerMatch:
            continue

        abbrMatch = re.findall(r'([A-Z0-9]+\s+([\w-]+[ ]?)+\b)', line)
        if abbrMatch:
            for abbr in abbrMatch:
                abbr = abbr[0]

                abbrSplit = re.split('\s{2,}', abbr)

                abbrs[abbrSplit[0]] = abbrSplit[1]
    
    # Main text parsing
    for line in pdfText.splitlines():
        footerMatch = re.match(r'Formula Student Rules 2020 +'
                               'Version: (\d+\.?)* +'
                               '\d+ of \d+', line)
    
        if footerMatch:
            continue

        headingUnderlines = ['=', '-']

        # Match heading
        mo = re.match(r'^(A|T|[CED]V|IN|S|D) +(\d+\.?)*', line)

        if mo:
            headingLevel = len(mo.group().split('.'))

            # Determine between top of page heading and level 1 headings
            if headingLevel == 1:
                if line != currentLevelOne:
                    currentLevelOne = line;
                else:
                    continue
                
            # If we have a heading not a rule
            if headingLevel < 3:
                print('  ' + ruleText + "\n") # Print rule text
                headingPrintRule = True
                ruleText = ""
                
                headingText = line[mo.end():].strip()

                heading = mo.group() + ' - ' + headingText;

                # Add 3 for dash
                underlineLength = len(headingText) + len(mo.group()) + 3
                underlines = headingUnderlines[headingLevel-1]*underlineLength

                print("\n")
                print(heading)
                print(underlines)

            # If we have a rule
            if headingLevel == 3:
                if not headingPrintRule:
                    print(' ' + ruleText + "\n") # Print prev rule text
                    
                ruleGroup = mo.group()
                # ruleText = line[mo.end():].strip()

                ruleText = checkLine(line[mo.end():].strip())

                print(ruleGroup)
                headingPrintRule = False

        else:
            ruleText += checkLine(line)
        
    print(' ' + ruleText + "\n") # Print final rule
