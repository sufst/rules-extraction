import pdftotext

import re

sections = { 
    # this will eventually be auto-generated from 
    # the file itself but it's manual for now
    'contents': (0, 2),
    'changelog': (2, 5),
    'abbreviations': (5, 7),
    'rules': (7, 133)
}

def page_range(pages: tuple):
    return range(pages[0], pages[1])

def load_pdf(file_path):
    # todo - add some exception catching, handle reactions to non-pdf files
    with open(file_path, 'rb') as f:
        return pdftotext.PDF(f)

def parse(file_path):
    pdf = load_pdf(file_path)
    
    # for page_number, page in enumerate(pdf):
    #     if page_number in page_range(sections['contents']):
    #         print(page_number)
    #         # print(page)
        
    #     if page_number >= sections['rules'][0]:
    #         text = "\n\n".join(page).splitlines()
    
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

parse('rules.pdf')