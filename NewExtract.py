from PyPDF2 import PdfReader
import os
import re

class PDF():
    def __init__(self, filename) -> None:
        self.filename = filename
        # General formats for each attribute of rule documents as per 2025 FSG FSUK
        self._rule_start_regex = r"^[A-Z]{1,2}\d{1,3}\.\d{1,3}"
        self._title_regex = r"^[A-Z]{1,2}\.\d{1,3}"
        self._footer_regex = r"©|\s+\d{4}\sRules|Formula Student Rules\s+Version:" 
        self._section_regex = r"^[A-Z]{1,2}\d{1,2}\s"

        # Establishes directory the folder of the python file is in, irrelvant of it's name.
        directory = os.path.dirname(__file__)
        filepath = os.path.join(directory,filename)
        self.pagesDict = self.create_page_dict(filepath)
        self.pagesObjList = self.objectify_pages()

    def create_page_dict(self, filepath) -> dict:
        pdfObj = PdfReader(filepath)
        numPages = pdfObj._get_num_pages()
        pagesDict = {}
        page_memory = []
        for page_index in range(numPages): #Creates a dictionary of all the pages with 'uncleaned' rule lines and also cleans them simultaneously
            if page_memory:
                page = page_memory[0]
                page_memory = []
            else:
                page = self.clean_page(pdfObj.pages[page_index].extract_text().split("\n"))
            try:
                next_page = self.clean_page(pdfObj.pages[page_index+1].extract_text().split("\n"))
                clean_result = self.clean_between_pages(page, next_page)
                if clean_result != 0:
                    page, next_page = clean_result
                    pagesDict[page_index+1] = next_page
                page_memory.append(next_page)
            except IndexError:
                pass
            pagesDict[page_index] = page
        return pagesDict
    
    def clean_page(self, pageData: list) -> list: # function which cleans the rule lines on a page 
        cleanedPage = []
        i = 0
        while len(cleanedPage) < len(pageData):
            PageString = pageData[i]
            for _ in range(i, len(pageData)):
                # FOOTER CLEANING - Checks each word in potential footer text and uses regexes to check'
                if re.search(self._footer_regex, PageString):
                    PageString = ""
                    break

                #BLANK / SHORT LINE CLEANING
                if PageString.strip() == "" or len(PageString) < 3:
                    PageString = PageString.strip()
                    break

                #RULE CLEANING
                try:
                    if re.search(self._rule_start_regex,pageData[i+1].strip()): # Assumption: Follows regex format of start of a rule, if its found it means it wont join it to the string before it
                        break
                    else:
                        PageString += pageData[i+1] #conjoins the two rules if second one is not a 'beginning'
                        pageData.remove(pageData[i+1])
                except IndexError:
                    break

            cleanedPage.append(PageString)
            i += 1
        cleanedPage = list(filter(None, cleanedPage))
        return cleanedPage

 
    def clean_between_pages(self, page: list, next_page: list) -> list: # SLOW FUNCTION MIGHT NEED TO OPTIMISE
        # Links rules seperated by pages which should be together.
        regex_check = re.compile("|".join([self._rule_start_regex,self._title_regex,self._section_regex]))
        if not re.search(regex_check, next_page[0])  and next_page[0][0].islower():
            new_rule = page[-1] + next_page[0]
            page[-1] = new_rule
            new_next_page = next_page[1:]
            return [page, new_next_page]
        else:
            return 0
    
    def list_rules(self):
        for key in self.pagesDict:
            rules = {}
            page = self.pagesDict[key]
        pass

    def objectify_pages(self): # Function is perfectly fast
        obj_pagesList = []
        for keys in self.pagesDict:
            page = self.pagesDict[keys]
            obj_page = []
            for lines in page:
                if re.search(self._rule_start_regex,lines):
                    id = lines.split()[0]
                    obj_page.append(self.Rule(keys,id,lines))
                elif re.search(self._section_regex, lines):
                    id = lines.split()[0]
                    obj_page.append(self.Section(keys,id,lines))
                elif re.search(self._title_regex,lines):
                    id = lines.split()[0]
                    obj_page.append(self.Title(keys,id,lines))
            obj_pagesList += obj_page
        return obj_pagesList

    # Title and Section Child Classes of Rule, act similar
    class Rule:
        def __init__(self, page_no, id, content):
            self.page_no = page_no
            self.id = id
            self.content = content

    def __str__(self):
        return f"Pg: {self.page_no}, {self.id}: {self.content}"


    class Title(Rule):
        def __init__(self, page_no, id, title):
            super().__init__(page_no, id, title)

        def __str__(self):
            return f"Pg: {self.page_no}, {self.id}: {self.content}"


    class Section(Rule):
        def __init__(self, page_no, id, section):
            super().__init__(page_no, id, section)

        def __str__(self):
            return f"Pg: {self.page_no}, {self.id}: {self.content}"
            

def find_differences_rules(PDF1,PDF2):
    PDF1 = PDF(PDF1)
    PDF2 = PDF(PDF2)
    Rules1 = PDF1.pagesObjList
    Rules2 = PDF2.pagesObjList
    for rules1, rules2 in zip(Rules1, Rules2):
        print(rules1.content)
        print(rules2)
        print("\n")

 
 # PAGE NUMBER IS ONE LESS THAN TRUE PAGE MUMBER DUE TO THE WAY THE MODULE PYPDF2 WORKS - TBC IF THIS DEPENDS ON FILE!!!!
 # READS FOOTER FROM PAGE BEFORE IT SOMETIMES AS HEADER OF CURRENT PAGE


# FILES AND FILE INFO
# "rules-extraction/fsuk-2024-rules---v1-2.pdf"
# "rules-extraction/FSG-Rules_2024_v1.1.pdf"
# "rules-extraction/fsuk-2025-rules---v1-0.pdf"
# 

find_differences_rules("fsuk-2025-rules---v1-0.pdf","fsuk-2024-rules---v1-2.pdf")
# for i in range (10,21):
#     for rules in obj.pagesDict[i]:
#         print(rules)
#         if rules == obj.pagesDict[i][-1]:
#             print(f"Page: {i+1}\n\n\n")

# BEGUN COMPARISON RULES INFRASTRUCTURE, HOWEVER THERES SOME SORT OF PRINTING ISSUE WITH THE OBJECTS ALSO I THINK THE FINAL FEW PAGES ARE CLEANED WRONG SO GO BACK AND CHECK