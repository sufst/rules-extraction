import pdftotext

import re

# Load PDF
with open("rules.pdf", "rb") as f:
    pdf = pdftotext.PDF(f)

    pdfText = "\n\n".join(pdf).splitlines()

    currentLevelOne = ""
    
    for line in pdfText:
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
                    continue;
            

            # If we have a heading not a rule
            if headingLevel < 3:
                headingText = line[mo.end():].strip()

                heading = mo.group() + ' - ' + headingText;

                # Add 3 for dash
                underlineLength = len(headingText) + len(mo.group()) + 3
                underlines = headingUnderlines[headingLevel-1]*underlineLength

                print(heading)
                print(underlines)

            # If we have a rule
            if headingLevel == 3:
                print(line)
