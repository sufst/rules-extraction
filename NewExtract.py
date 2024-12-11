from PyPDF2 import PdfReader
import os
import re

# General formats for rules, titles and headers FSG and FSUK documentation
Rule_Start_Regex = r"^[A-Z]{1,2}\d{1,3}\.\d{1,3}"
Title_Regex = r"^[A-Z]{1,2}\.\d{1,3}"
Header_Regex = r"^[A-Z]{1,2}\d{1,2}\s"
# General Formats as of 2025 for footers in FSG and FSUK documentation
Footer_Regexes = r"©|\s+\d{4}\sRules|Formula Student Rules\s+Version:" 


class Rule():
    def __init__(self, rule_code, content):
        self.rule_code = rule_code
        self.content = content

    class Title():
        def __init__(self, rule_code, content):
            super().__init__(rule_code, content)


class PDF():
    def __init__(self, filename) -> None:
        self.filename = filename

        # Establishes directory the folder of the python file is in, irrelvant of it's name.
        directory = os.path.dirname(__file__)
        filepath = os.path.join(directory,filename)
        self.pagesDict = PDF.create_page_dict(filepath)

        for pageNum in self.pagesDict: #for loop which cleans every page
            self.pagesDict[pageNum] = self.clean_page(self.pagesDict[pageNum])

    def create_page_dict(filepath):
        pdfObj = PdfReader(filepath)
        numPages = pdfObj._get_num_pages()
        pagesDict = {}
        for page in range(numPages): #Creates a dictionary of all the pages with 'uncleaned' rule lines
            pageDataObj = pdfObj.pages[page]
            pagesDict[page] = pageDataObj.extract_text().split("\n")
        return pagesDict

    def clean_page(self, pageData): # function which cleans the rule lines one a single 
        cleanedPage = []
        i = 0
        while len(cleanedPage) < len(pageData):
            PageString = pageData[i]
            for strings in range(i, len(pageData)):
                # FOOTER CLEANING - Checks each word in potential footer text and uses regexes to check'
                if re.search(Footer_Regexes, PageString):
                    PageString = ""
                    break

                #BLANK / SHORT LINE CLEANING
                if PageString.strip() == "" or len(PageString) < 3:
                    PageString = PageString.strip()
                    break

                #RULE CLEANING
                try:
                    if re.search(Rule_Start_Regex,pageData[i+1].strip()): # Assumption: Follows regex format of start of a rule, if its found it means it wont join it to the string before it
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

    def clean_between_pages(self):
        # have to match start of a page disregarding the header and footer where the first sentence doesnt start with a rule code
        pass


 
 # PAGE NUMBER IS ONE LESS THAN TRUE PAGE MUMBER DUE TO THE WAY THE MODULE PYPDF2 WORKS - TBC IF THIS DEPENDS ON FILE!!!!
 # READS FOOTER FROM PAGE BEFORE IT SOMETIMES AS HEADER OF CURRENT PAGE

# CODE ASSUMPTIONS
# EVERY RULE BEGINS WITH GENERAL FORMAT A-Z 1-50 . (no spaces)
# EVERY FOOTER HAS © IN IT TO IDENTIFY IT AS A FOOTER TO CLEAN AND MIGHT CONTAIN 'RULES' AS FINAL WORD

# FILES AND FILE INFO
# "rules-extraction/fsuk-2024-rules---v1-2.pdf"
# "rules-extraction/FSG-Rules_2024_v1.1.pdf"
# "rules-extraction/fsuk-2025-rules---v1-0.pdf"
# Formula Student Rules 20--- on footer of both FSG and FSUK read on top or bottom depending on format of pdf
# FSG doesnt have spaces between words when \n occurs between the two words

obj = PDF("fsuk-2024-rules---v1-2.pdf") # LOOK AT OS LIBRARY TO SEARCH FOR FILE NAME AS OPPOSED TO ASSUMED DIRECTORY rules-extraction/
# for rules in obj.pagesDict[10]:
#     if re.search(Title_Regex, rules):
#         print(rules)
print(obj.pagesDict[10])
# for i in range (15):
#     for rules in obj.pagesDict[i]:
#         print(rules)
#         if rules == obj.pagesDict[i][-1]:
#             print(f"Page: {i+1}\n\n\n")

