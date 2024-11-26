from PyPDF2 import PdfReader

# Creates database of general format of A-Z,1-50: WEIRD WAY TO DO IT MIGHT BE A BETTER WAY TO RETHINK IT
RuleStart = [f"{letter}{num}" for letter in [chr(i) for i in range(65, 91)] for num in range(1, 51)]

# Database of potential keywords in footers: ALSO A WEIRD WAY TO DO IT
Footer = ["Formula", "Student", "Rules 20", "Rules"]

class PDF():
 
    def __init__(self, filepath) -> None:
 
        self.pagesDict = PDF.getPageDict(filepath)

        for pageNum in self.pagesDict: #for loop which cleans every page
            self.pagesDict[pageNum] = self.cleanPage(self.pagesDict[pageNum])

    @staticmethod
    def getPageDict(filepath):
        pdfObj = PdfReader(filepath)
        numPages = pdfObj._get_num_pages()
        pagesDict = {}
        for page in range(numPages): #Creates a dictionary of all the pages with 'uncleaned' rule lines
            pageDataObj = pdfObj.pages[page]

            pagesDict[page] = pageDataObj.extract_text().split("\n")
        return pagesDict

    def cleanPage(self, pageData): # function which cleans the rule lines one a single 
        cleanedPage = []
        i = 0
        while len(cleanedPage) < len(pageData):
            PageString = pageData[i]
            for strings in range(i, len(pageData)):
                #BLANK / SHORT LINE CLEANING
                if PageString.strip() == "" or len(PageString) < 3:
                    PageString = PageString.strip()
                    continue

                #FOOTER CLEANING
                footerdata = PageString.split()

                for words in footerdata:
                    #Checks each word in potential footer text and tests if a line ending with 'Rules' exists or its a part of the potential footer words
                    if words in Footer or words == "©":
                        PageString = ""
                    elif words == "Rules" and words == footerdata[-1]:
                        PageString = ""
                
                #RULE CLEANING
                try:
                    if pageData[i+1][:2] not in RuleStart: # ASSUMES ALL RULES START WITH E.G A00 UP TO 50
                        PageString += pageData[i+1] #conjoins the two rules if second one is not a 'beginning'
                        pageData.remove(pageData[i+1])
                    else:
                        break
                except IndexError:
                    break
            cleanedPage.append(PageString)
            i += 1
        cleanedPage = list(filter(None, cleanedPage))
        return cleanedPage


 
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

obj = PDF(filepath="rules-extraction/fsuk-2024-rules---v1-2.pdf") # LOOK AT OS LIBRARY TO SEARCH FOR FILE NAME AS OPPOSED TO ASSUMED DIRECTORY rules-extraction/
#print(obj.pagesDict[10])
for i in range (15):
    for rules in obj.pagesDict[i]:
        print(rules)
        if rules == obj.pagesDict[i][-1]:
            print(f"Page: {i+1}\n\n\n")