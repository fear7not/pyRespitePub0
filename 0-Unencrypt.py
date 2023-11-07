import time
import pikepdf
import glob
import os
from PyPDF2 import PdfFileMerger

dr = os.path.dirname(os.path.realpath(__file__))
def decrypt():
    inputFiles = glob.glob(dr + r'\input\new\*.pdf')
    for i, contents in enumerate(inputFiles):
        pdf = pikepdf.open(contents, password="notLeakingThePasswordHere")
        pdf.save(dr + r'/input/new/' + str(i) + ".pdf")
        pdf.close()
        os.remove(contents)
#         pdf = pikepdf.open(dr + r'\temp\test.pdf')
#         pdf.save(contents)
#         pdf.close
# os.remove(dr + r'\temp\test.pdf')

def combine():
    merger = PdfFileMerger()
    inputFiles = glob.glob(dr + r'\input\new\*pdf')
    for i in inputFiles:
        merger.append(i)
    merger.write(dr + r'\input\merged.pdf')
    merger.close()
    for i in inputFiles:
        os.remove(i)
decrypt()
time.sleep(1)
combine()
