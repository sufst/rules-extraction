from file_io import write_to_json
from extract import *
import os

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

current_dir = os.getcwd()
out_dir = os.path.join(current_dir, 'out')

out_file_path = os.path.join(out_dir, 'rules.json')

write_to_json(parsed_rules, out_file_path)

