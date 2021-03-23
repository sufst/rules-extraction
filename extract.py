import pdftotext
import re
import os

def page_range(pages: tuple):
    return range(pages[0], pages[1])

def load_pdf(file_path):
    # todo - add some exception catching, handle reactions to non-pdf files
    with open(file_path, 'rb') as f:
        return pdftotext.PDF(f)
    
def parse_page(page):
    page_lines = page.splitlines()
    page_lines_split = [line.split() for line in page_lines]

    currentLevelOne = ""
    
    for line in page_lines:
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
    
def parse_section(pdf: pdftotext.PDF, section_pages: tuple):
    '''
    pdf: the result of pdftotext.PDF(PDF_FILE)
    section_pages: page range for section you want to extract, e.g. (0, 5) for pages 0-4
    '''
    
    for page_number, page in enumerate(pdf):
        if page_number in page_range(section_pages):
            parse_page(page)
        else:
            pass # skip pages not in requested section
    
    return []

def parse(file_path):
    pdf = load_pdf(file_path)
    
    section_pages = { # todo - generate automatically
        # this will eventually be auto-generated from 
        # the file itself but it's done manually for now
        'contents': (0, 2),
        'changelog': (2, 5),
        'abbreviations': (5, 7),
        'rules': (7, len(pdf))
    }
    
    rules = parse_section(pdf, section_pages['rules'])

parse('rules.pdf')

