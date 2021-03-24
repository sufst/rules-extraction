import pdftotext
import re
import os
from enum import IntEnum

def page_range(pages: tuple):
    return range(pages[0], pages[1])

def load_pdf(file_path):
    # todo - add some exception catching, handle reactions to non-pdf files
    with open(file_path, 'rb') as f:
        return pdftotext.PDF(f)
    
def _old_parse_page(page):
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
                    
def get_page(page):
    return page.splitlines()
    
def get_section(pdf: pdftotext.PDF, section_pages: tuple):
    '''
    pdf: the result of pdftotext.PDF(PDF_FILE)
    section_pages: page range for section you want to extract, e.g. (0, 5) for pages 0-4
    '''
    pages = []
    
    for page_number, page in enumerate(pdf):
        if page_number in page_range(section_pages):
            pages.append(get_page(page))
    
    return pages # return list of pages (as list of their lines) for requested section

def is_footer(line: str):
    return re.match(r' *Formula Student Rules 2020 +Version: (\d+\.?)* +\d+ of \d+', line)

def is_header(line: str):
    return re.match(r' *Formula Student Rules 2020 ?', line)
class RuleLayer(IntEnum):
    CATEGORY = 0   # e.g. A       - Administrative Regulations
    SECTION = 1    # e.g. A 1     - Competition Overview
    SUBSECTION = 2 # e.g. A 1.1   - Competition Objective
    RULE = 3       # e.g. A 1.1.1 - RULE

# todo - parse_abbreviations()... etc

def parse_rules(pages, category_labels=['A', 'T', 'CV', 'EV', 'DV', 'IN', 'S', 'D']):
    '''
    todo
    '''       
    rules = {}
    for label in category_labels:
        rules[label] = {'title': '', 'sections': {}} # initialize categories in rules dict
        
    rules['figures'] = {}
        
    section_index, subsection_index, rule_index = [0, 0, 0]
    previous_layer = RuleLayer.CATEGORY
    
    for page in pages:
        for line_index, line in enumerate(page):
            
            if is_header(line) or line_index == 0: # skip headers (or first line)
                continue
            
            if is_footer(line): # skip footers
                continue
            
            # Match category, section, subsection, or rule
            category_match = re.match(r'^ +(A|T|[CED]V|IN|S|D) +((?:[A-Z]+ *)+)$', line)
            section_match = re.match(r'^(A|T|[CED]V|IN|S|D) ?(\d+) +(.+)', line)
            subsection_match = re.match(r'^(A|T|[CED]V|IN|S|D) ?(\d+\.\d+) +(.+)', line)
            rule_match = re.match(r'^(A|T|[CED]V|IN|S|D) ?(\d+\.\d+\.\d+) +(.+)', line)
            # all_match = re.match(r'^(A|T|[CED]V|IN|S|D) +(?:(\d+\.?)*)', line) # matches all three
                
            if category_match:
                category, category_title = category_match.groups()   
                rules[category]['title'] = category_title
                
                previous_layer = RuleLayer.CATEGORY
            elif section_match:
                category, section_index, section_title = section_match.groups()
                
                section_index = int(section_index)
                
                # initialize new section:
                if section_index in rules[category]['sections'].keys():
                    continue # skip repeated section titles
                else:
                    rules[category]['sections'][section_index] = {'title': section_title, 'subsections': {}} 
                    
                previous_layer = RuleLayer.SECTION
            
            elif subsection_match:
                category, index, subsection_title = subsection_match.groups()
                
                section_index, subsection_index = [int(v) for v in index.split('.')]
                
                # initialize new subsection:
                rules[category]['sections'][section_index]['subsections'][subsection_index] = {'title': subsection_title, 'rules': {}, 'notes': ''} 
                
                previous_layer = RuleLayer.SUBSECTION
                
            elif rule_match:
                category, index, rule_text = rule_match.groups()
                
                section_index, subsection_index, rule_index = [int(v) for v in index.split('.')]
                
                # initialize new rule:
                rules[category]['sections'][section_index]['subsections'][subsection_index]['rules'][rule_index] = rule_text
                
                previous_layer = RuleLayer.RULE
                                    
            else:
                                
                # todo - handle tables, table captions
                
                figure_caption_match = re.match(r'^ *Figure *(\d+): *(.*)$', line)
                if figure_caption_match:
                    # should this handle overflowing figure captions?
                    figure_index, figure_caption = figure_caption_match.groups()
                    figure_index = int(figure_index)
                    
                    rules['figures'][figure_index] = figure_caption
                elif previous_layer == RuleLayer.CATEGORY: # overflow category title
                    rules[category]['title'] += ' ' + line.strip()
                elif previous_layer == RuleLayer.SECTION:  # overflow section title
                    rules[category]['sections'][section_index]['title'] += ' ' + line.strip()
                elif previous_layer == RuleLayer.SUBSECTION: # overflow subsection title
                    rules[category]['sections'][section_index]['subsections'][subsection_index]['notes'] += ' ' + line.strip()
                elif previous_layer == RuleLayer.RULE: # overflow rule
                    rules[category]['sections'][section_index]['subsections'][subsection_index]['rules'][rule_index] += ' ' + line.strip()
                else:
                    print(line)
    return rules