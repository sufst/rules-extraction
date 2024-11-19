from PyPDF2 import PdfReader
import re
from collections import OrderedDict
import copy


class PDFReader():

    def __init__(self, filepath) -> None:

        self.pagesDict = PDFReader.getPageDict(filepath)

        for pageNum in self.pagesDict.keys():
            self.pagesDict[pageNum] = self.cleanPage(self.pagesDict[pageNum])


    @staticmethod
    def getPageDict(filepath):
        pdfObj = PdfReader(filepath)
        numPages = pdfObj._get_num_pages()

        pagesDict = OrderedDict()
        for page in range(numPages):
            pageDataObj = pdfObj.pages[page]

            pageData = pageDataObj.extract_text(0).split("\n")

            # Add page to dict of PageNum:PageData, but remove first 5 elements (it contains the footer from previous page)
            pagesDict[page] = pageData[5:]

        return pagesDict


    def cleanPage(self, pageData):
        tmpPage = []

        i = 0
        print(f"Len page:{len(pageData)-2}")
        while i < len(pageData)-3:
            firstStr = i
            tmpStr = pageData[firstStr]
            for stringPos in range(firstStr, len(pageData)-2):  # -2 because we do +1 in the loop
                i = stringPos
                if (pageData[stringPos+1][0].islower()):    #(j != self.numPages-1) and 
                    tmpStr = tmpStr + pageData[stringPos+1]
                else:
                    i += 1
                    break
            
            tmpPage.append(tmpStr)
        
        return tmpPage



obj = PDFReader(filepath="rules-extraction/fsuk-2024-rules---v1-2.pdf")
print(obj.pagesDict[41])