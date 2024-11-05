import pdftotext

import re

abbrPage = 6
startPage = 8

def checkLine(line, multiLine):
    # Check line of a rule without a 'heading'

    outLine = ""
    linkStart = ""

    # Link to section
    line = re.sub(r'(A|T|[CED]V|IN|S|D) +(\d+\.?)+(\d+)', ":ref:`\g<0>`", line)

    line = line.lstrip().split()
    for word in line:
        alteredLine = False

        # Bullet point
        if word == '•':
            outLine += '\n\n-'
            alteredLine = True
            continue

        # Abbreviations
        for key in abbrs:
            keySearch = re.match(key, word)
            if keySearch:
                if len(outLine) > 0 or multiLine:
                    outLine += ' '

                outLine += ':abbr:`' + word + ' (' + abbrs[keySearch.group()] + ')`'
                alteredLine = True
                break

        if not alteredLine:
            #or (line.index(word) == 0 and len(outLine) > 0)
            if len(outLine) > 0 or multiLine:
              outLine += ' '

            outLine += word

    return outLine

# Load PDF
with open("rules-extraction/rules.pdf", "rb") as f:
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
        # print(pdf[i].index("\n"))
        pdfText += pdf[i][pdf[i].index("\n"):]

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

                if len(abbrSplit) >= 2:
                     abbrs[abbrSplit[0]] = ' '.join(abbrSplit[1:])
                else:
            # Log or handle cases where no definition is found
                    print(f"Could not find definition for abbreviation: {abbrSplit[0]}")
    
    # Main text parsing
    for line in pdfText.splitlines():
        footerMatch = re.match(r'Formula Student Rules 2020 +'
                               'Version: (\d+\.?)* +'
                               '\d+ of \d+', line)
        
        if footerMatch:
            continue

        line = re.sub(r'\s{1}\]', "]", line)

        headingUnderlines = ['=', '-', '^']

        # Match heading
        mo = re.match(r'^(A|T|[CED]V|IN|S|D) *(\d+\.?)*', line)

        if mo:
            headingLevel = len(mo.group().split('.'))

            # Level 1 heading
            h1Match = re.match(r'^(A|T|[CED]V|IN|S|D)\d{1,2} +[A-Z-()&[\] ]*', line)
            if h1Match:
                if not headingPrintRule:
                    print(ruleText + "\n") # Print rule text
                    headingPrintRule = True
                
                headingText = re.sub(r'\s{2,}', " ", h1Match.group())
                headingText = re.sub(r'(\b.) ', '\g<1>', headingText)

                headingText = headingText[mo.end():].strip()

                heading = mo.group() + ' - ' + headingText

                # Add 3 for dash
                underlineLength = len(headingText) + len(mo.group()) + 3
                underlines = headingUnderlines[headingLevel-1]*underlineLength + "\n"

                print(heading)
                print(underlines)
            
            if headingLevel == 2:
                if not headingPrintRule:
                    print(ruleText + "\n") # Print rule text
                    headingPrintRule = True
                    ruleText = ""
                
                headingText = line[mo.end():].strip()
                headingText = re.sub(r'\s{2,}', " ", headingText)
 
                heading = mo.group() + ' - ' + headingText

                # Add 3 for dash
                underlineLength = len(headingText) + len(mo.group()) + 3
                underlines = headingUnderlines[headingLevel-1]*underlineLength + "\n"

                print(heading)
                print(underlines)
            
            # If we have a rule
            if headingLevel == 3:
                if not headingPrintRule:
                    print(ruleText + "\n") # Print prev rule text
                    
                ruleGroup = mo.group()
                ruleText = checkLine(line[mo.end():].strip(), False)

                # Add 3 for dash
                underlineLength = len(ruleGroup)
                underlines = headingUnderlines[headingLevel-1]*underlineLength + "\n"

                print(ruleGroup)
                print(underlines)
                headingPrintRule = False

        else:
            ruleText += checkLine(line, True)

    print(ruleText + "\n") # Print final rule
