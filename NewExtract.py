from PyPDF2 import PdfReader
 

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
            pagesDict[page] = pageDataObj.extract_text(0).split("\n")
        return pagesDict
 
    def cleanPage(self, pageData): # function which cleans the rule lines
        cleanedPage = []
        i = 0
        RuleStart = [f"{letter}{num}" for letter in [chr(i) for i in range(65, 91)] for num in range(1, 51)] #Creates database of general format of A-Z,1-50. start of a rule
        while len(cleanedPage) < len(pageData):
            PageString = pageData[i]
            if i == len(pageData) - 1 or i == 0:
                #print(PageString)
                PageString = pageData[i].replace("Formula Student Rules 20","") #WIP
                #print(PageString)
            for strings in range(i, len(pageData)):
                try:
                    if pageData[i+1][:2] not in RuleStart: # ASSUMES ALL RULES START WITH E.G A00. up
                        PageString += pageData[i+1] #conjoins the two rules if second one is not a beginning
                        pageData.remove(pageData[i+1])
                    else:
                        break
                except IndexError:
                    break
            cleanedPage.append(PageString)
            i += 1
        return cleanedPage


 
 
 # PAGE NUMBER IS ONE LESS THAN TRUE PAGE MUMBER DUE TO THE WAY THE MODULE PYPDF2 WORKS
 # "rules-extraction/fsuk-2024-rules---v1-2.pdf"
 # "rules-extraction/FSG-Rules_2024_v1.1.pdf"
 # "rules-extraction/fsuk-2025-rules---v1-0.pdf"
 # Formula Student Rules 20--- on footer of both FSG and FSUK read on top or bottom depending on format of pdf, make a way to get rid of it


obj = PDF(filepath="rules-extraction/fsuk-2025-rules---v1-0.pdf") # LOOK AT OS LIBRARY TO SEARCH FOR FILE NAME AS OPPOSED TO ASSUMED DIRECTORY rules-extraction/
print(obj.pagesDict[10])
#for i in range (15):
    #for rules in obj.pagesDict[i]:
        #print(rules)
        #print(f"Page: {i+1}\n\n\n")