from PyPDF2 import PdfReader
import re
from collections import OrderedDict


class PDFReader():

    def __init__(self, filepath) -> None:

        self.pagesDict = PDFReader.getPageDict(filepath)
        self.cleanPages()


    @staticmethod
    def getPageDict(filepath):
        pdfObj = PdfReader(filepath)
        numPages = pdfObj._get_num_pages()

        pagesDict = OrderedDict()
        for page in range(numPages):
            pageDataObj = pdfObj.pages[page]

            pageData = pageDataObj.extract_text(0).split("\n")

            pagesDict[page] = pageData

        return pagesDict


    def cleanPages(self):
        # for page in 
        pass


obj = PDFReader(filepath="rules-extraction/fsuk-2024-rules---v1-2.pdf")
print(obj.pagesDict[41])