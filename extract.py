import pdftotext

import re

abbrPage = 6
startPage = 8

# Load PDF
with open("rules.pdf", "rb") as f:
    abbrText = ""
    pdfText = ""

    currentLevelOne = ""
    multilineRule = False
    ruleText = ""
    prevRuleText = ""
    ruleGroup = ""

    pdf = pdftotext.PDF(f)

    for i in range(abbrPage - 1, startPage - 1):
        abbrText += pdf[i]

    for i in range(startPage - 1, len(pdf)):
        pdfText += pdf[i]

    # pdfText = "\n".join(pdf).splitlines()
    
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
            if multilineRule:
                print('  ' + prevRuleText + "\n") # Print rule text
                multilineRule = False

            headingLevel = len(mo.group().split('.'))

            # Determine between top of page heading and level 1 headings
            if headingLevel == 1:
                if line != currentLevelOne:
                    currentLevelOne = line;
                else:
                    continue;

            # If we have a heading not a rule
            if headingLevel < 3:
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
                ruleGroup = mo.group()
                ruleText = line[mo.end():].strip()

                if prevRuleText != ruleText:
                    prevRuleText = ruleText

                    print(ruleGroup)

        else:
            # Line of a rule without a 'heading'
            prevRuleText += ' ' + line.strip()
            multilineRule = True

    print('  ' + prevRuleText + "\n") # Print final rule
