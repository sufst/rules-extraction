from file_io import write_to_json
from extract import *

pdf = load_pdf('rules.pdf')

section_pages = { 
        # todo - generate automatically from pdf
        'contents': (0, 2),
        'changelog': (2, 5),
        'abbreviations': (5, 7),
        'rules': (7, len(pdf))
}

rules = get_section(pdf, section_pages['rules'])
parsed_rules = parse_rules(rules)

write_to_json(parsed_rules, 'rules.json')

