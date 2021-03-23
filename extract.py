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
    # todo - rename to get_page
    return page.splitlines()
    
def get_section(pdf: pdftotext.PDF, section_pages: tuple):
    # todo - rename to get_section
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
    return re.match(r'Formula Student Rules 2020 +Version: (\d+\.?)* +\d+ of \d+', line)

def is_header(line: str): # todo - change this to a header pattern
    return re.match(r'Formula Student Rules 2020 +', line)
class RuleLayer(IntEnum):
    CATEGORY = 0   # e.g. A       - Administrative Regulations
    SECTION = 1    # e.g. A 1     - Competition Overview
    SUBSECTION = 2 # e.g. A 1.1   - Competition Objective
    RULE = 3       # e.g. A 1.1.1 - RULE

# todo - parse_rules(), parse_abbreviations()... etc
def parse_rules_page(page, rules):
        
    section_index, subsection_index, rule_index = [0, 0, 0]

    for line in page:
        
        if is_header(line): # skip headers
            continue
        
        if is_footer(line): # skip footers
            continue
        
        # todo - handle tables, table captions, figures, figure captions, ... etc

        # Match section, subsection, or rule
        section_match = re.match(r'^(A|T|[CED]V|IN|S|D) ?(\d+) +(.+)', line)
        subsection_match = re.match(r'^(A|T|[CED]V|IN|S|D) ?(\d+\.\d+) +(.+)', line)
        rule_match = re.match(r'^(A|T|[CED]V|IN|S|D) ?(\d+\.\d+\.\d+) +(.+)', line)
        # all_match = re.match(r'^(A|T|[CED]V|IN|S|D) +(?:(\d+\.?)*)', line) # matches all three
                
        if section_match:
            category, section_index, section_title = section_match.groups()
            
            # initialize new section:
            rules[category][int(section_index)] = {'title': section_title, 'subsections': {}} 
        
        elif subsection_match:
            category, index, subsection_title = subsection_match.groups()
            
            section_index, subsection_index = [int(v) for v in index.split('.')]
            
            # initialize new subsection:
            rules[category][section_index][subsection_index] = {'title': subsection_title, 'rules': {}} 
            
        elif rule_match:
            category, index, rule_text = rule_match.groups()
            
            section_index, subsection_index, rule_index = [int(v) for v in index.split('.')]
            
             # initialize new rule:
            rules[category][section_index][subsection_index][rule_index] = rule_text
                                
        else: # todo - when rule overflows into other page, append this line to current rule
            pass
            # rules[category][section_index][subsection_index][rule_index] += line
                
    
    return rules

def parse_rules(pages, category_labels=['A', 'T', 'CV', 'EV', 'DV', 'IN', 'S', 'D']):
    '''
    todo
    '''       
    page = pages[0] # todo - repeat for all pages
    
    rules = {}
    for label in category_labels: # todo - do this within the parse_rules_page
        rules[label] = {} # initialize categories in rules dict
    
    rules = parse_rules_page(page, rules) # update rules with page
    
    # for page in pages:
        # rules = parse_rules_page(page, rules)
    
    return rules

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
    
    rules = get_section(pdf, section_pages['rules'])
    parsed = parse_rules(rules)
    
    return parsed
    
    # for section_page_range in section_pages:
        # parse_section(pdf, section_page_range)

parsed = parse('rules.pdf')
print(parsed)
