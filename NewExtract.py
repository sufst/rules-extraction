from PyPDF2 import PdfReader
import os
import re
import difflib 

class PDF():
    def __init__(self, filename) -> None:
        self.filename = filename
        # General formats for each attribute of rule documents as per 2025 FSG FSUK and FSG
        self._rule_start_regex = r"^[A-Z]{1,2}\d{1,3}\.\d{1,3}\."
        self._title_regex = r"^[A-Z]{1,2}\d{1,3}\.\d{1,3}\s"
        self._footer_regex = r"©|\s+\d{4}\sRules|Formula Student Rules\s+Version:" 
        self._section_regex = r"^[A-Z]{1,2}\d{1,2}\s+[A-Z]|SECTION\s+[A-Z]{1,2}\s+[A-Z]|^[A-Z]{1,2}\d{1,2}\s+\["
        self.regex_check = re.compile("|".join([self._rule_start_regex,self._title_regex,self._section_regex]))

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
                    if re.search(self.regex_check,pageData[i+1].strip()): # Assumption: Follows regex format of start of a rule, if its found it means it wont join it to the string before it
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
        if not re.search(self.regex_check, next_page[0])  and next_page[0][0].islower():
            new_rule = page[-1] + next_page[0]
            page[-1] = new_rule
            new_next_page = next_page[1:]
            return [page, new_next_page]
        else:
            return 0


    def objectify_pages(self): # Also filters through to second instance of SECTION A (ignoring contents section a) and deletes everything before it as its irrelevant // IMPROVE EFFICIENCY
        obj_pagesList = []
        delete_count = 0 # Counts number of times section A appears, when 2 it chops the first part of the document off as its uneccesary
        for keys in self.pagesDict:
            page = self.pagesDict[keys]
            obj_page = []
            for lines in page:
                split_text = lines.split()
                id = split_text[0]
                if len(split_text) > 1:
                    content = (" ").join(split_text[1:])
                else:
                    content = lines
                if re.search(self._rule_start_regex,lines):
                    obj_page.append(self.Rule(keys,id,content))
                elif re.search(self._section_regex, lines):
                    obj_page.append(self.Section(keys,id,content))
                    if obj_page[-1].id == "A1":
                        delete_count +=1
                elif re.search(self._title_regex,lines):
                    obj_page.append(self.Title(keys,id,content))
            if delete_count == 2:
                obj_pagesList = []
                delete_count = 0
            obj_pagesList += obj_page
        return obj_pagesList

    # Title and Section Child Classes of Rule, act similar
    class Rule:
        def __init__(self, page_no, id, content):
            self.page_no = page_no
            self.id = id
            self.content = content

    class Title(Rule):
        def __init__(self, page_no, id, title):
            super().__init__(page_no, id, title)

    class Section(Rule):
        def __init__(self, page_no, id, section):
            super().__init__(page_no, id, section)

            
def find_differences(PDF1, PDF2):
    # Function compares PDF2 TO PDF1 and shows difference of PDF2 compared to 1
    # Initialise PDF Objects
    PDF1_obj = PDF(PDF1)
    PDF2_obj = PDF(PDF2)
    content_1 = PDF1_obj.pagesObjList
    content_2 = PDF2_obj.pagesObjList
    # Data storage for matching
    sections_1, sections_2, titles_1, titles_2, rules_1, rules_2 = [{},{},{},{},{},{}] # Will be formatted ID, Content

    for lines in zip(content_1,content_2):
        line_1 = lines[0]
        line_2 = lines[1]

        if type(line_1) == PDF.Rule:
            rules_1[line_1.id] = line_1.content
        elif type(line_1) == PDF.Title:
            titles_1[line_1.id] = line_1.content
        elif type(line_1) == PDF.Section:
            sections_1[line_1.id] = line_1.content

        if type(line_2) == PDF.Rule:
            rules_2[line_2.id] = line_2.content
        elif type(line_2) == PDF.Title:
            titles_2[line_2.id] = line_2.content
        elif type(line_2) == PDF.Section:
            sections_2[line_2.id] = line_2.content
        # TURN THIS DATASET INTO A LIST SET NOT DICT SO GET CLOSE MACTHES WORKS EASILY AND LINK IDS AND CONTENT FOR COMPARISON, CAN LATER CONVERT BACK INTO OBKECT IF NEEDED USE 
        # GET CLOSE MATCHES WILL ENSURE IF A RULE FULLY DOESNT EXIST, TINKER WITH DIFFERENCE FACTOR
    print(zip(rules_1,rules_2))
    for checks in zip(rules_1,rules_2): # zip dict element: ((ID1, CONTENT1),(ID2, CONTENT2)), etc
        id_1, cont_1 = checks[0][0], checks[0][1]
        id_2, cont_2 = checks[1][0], checks[1][1]
        

        pass
        

        # Outputs for testing
        output_1 = []
        output_2 = []
        file_output = "\n".join(output_1) + "\n\n" + "\n".join(output_2)
    
        directory = os.path.dirname(__file__)
        filepath = os.path.join(directory,"Output_text.txt")
        with open(filepath,"w",encoding="utf-8") as f:
            f.write(file_output)
    



 
 # PAGE NUMBER IS ONE LESS THAN TRUE PAGE MUMBER DUE TO THE WAY THE MODULE PYPDF2 WORKS - TBC IF THIS DEPENDS ON FILE!!!!
 # READS FOOTER FROM PAGE BEFORE IT SOMETIMES AS HEADER OF CURRENT PAGE


# FILES AND FILE INFO
# "rules-extraction/fsuk-2024-rules---v1-2.pdf"
# "rules-extraction/FSG-Rules_2024_v1.1.pdf"
# "rules-extraction/fsuk-2025-rules---v1-0.pdf"
# 

find_differences("fsuk-2025-rules---v1-0.pdf","fsuk-2024-rules---v1-2.pdf")

# RULE DIFFERENCES ARE DUE TO RULE ID CODES VARYING BETWEEN DOCUMENTS BUT CONTENT BEING THE SAME GOT TO THINK AROUND THIS, MAYBE FOCUS ON MATCHING TEXT