import re
import PyPDF2


def getDict(inputFile):
  """Convert PDF into list of lines"""
  pdfFile = open(inputFile, 'rb')  # Can have a loop here if more files
  readPdf = PyPDF2.PdfFileReader(pdfFile)
  lines = []
  for j in range(0, readPdf.getNumPages()):
    page = readPdf.getPage(j)
    page_content = page.extractText()
    lines.append(str(page_content.encode('utf-8')))
  '''Interpret lines from decoded PDF'''
  dictList = []
  for i, line in enumerate(lines):
    myDict = dict.fromkeys(
      ["pdfPage", "date", "authNum", "clientId", "Birth", "lastName", "firstName", "DOSl", "AUl", "authFl",
       "authTl", "maxMonthsl", "UCl", "maxAuthAmountl", "notes"])
    myDict["DOSl"], myDict["AUl"], myDict["authFl"], myDict["authTl"], myDict["maxMonthsl"], myDict["UCl"], myDict[
      "maxAuthAmountl"] = [], [], [], [], [], [], []
    myDict['pdfPage'] = i + 1
    myDict['date'] = re.findall(" \d{1,2}/\d\d/\d\d ", line)[0].strip()
    myDict['authNum'] = re.findall(" \d{8} ", line)[0].strip()
    myDict['clientId'] = re.findall(" \d{7} ", line)[0].strip()
    myDict['Birth'] = re.findall(" \d{1,2}/\d\d/\d\d\d\d ", line)[0].strip()
    myDict['lastName'] = re.findall(" CARE +[A-Z]+ ?[A-Z]*", line)[0][5:].strip()
    myDict['firstName'] = re.findall("[A-Z]+ ?[A-Z]*", line[397:])[0].strip()
    # Adding Multi-Line Authorization Information
    fromToList = re.findall("\d{1,2}/\d\d/\d\d {2}\d{1,2}/\d\d/\d\d", line)
    for j in range(0, len(fromToList)):
      if float(re.findall("\d*\.\d{4}", line)[j]).is_integer():
        myDict['AUl'].append(re.findall("\d*\.\d{4}", line)[j].split(".")[0])
      else:
        myDict['AUl'].append(re.findall("\d*\.\d{4}", line)[j])
      if re.findall("\d*\.\d{4}", line)[j] == ".0000":
        myDict['AUl'][j] = int(0)
      authFl = re.findall("\d{1,2}/\d\d/\d\d", fromToList[j])[0].split("/")
      myDict['authFl'].append(authFl[0] + "/" + authFl[1] + "/20" + authFl[2])
      authTl = re.findall("\d{1,2}/\d\d/\d\d", fromToList[j])[1].split("/")
      myDict['authTl'].append(authTl[0] + "/" + authTl[1] + "/20" + authTl[2])
      part2 = ""
      try:
        part2 = re.findall("8?62 +\S* *IN-HOME RESPITE SERV", line)[j][0:9].strip()
      except:
        pass
      myDict['DOSl'].append(part2)
      myDict['maxMonthsl'].append(
        re.findall("\d{1,2}/\d\d/\d\d {2}\d{1,2}/\d\d/\d\d *\d* *\d* *\d*", line)[j].split()[-1])
      myDict['UCl'].append(re.findall("\d*\.\d{4} *\d*.\d{3}", line)[j].strip().split()[-1])
      myDict['maxAuthAmountl'].append(re.findall("\d*\.\d{4} *\d*.\d{3} +\d*,?\d*.\d+", line)[j].strip().split()[-1])
    Notes = line[-537:]
    myDict['notes'] = (re.sub(" +", " ", Notes[0:45]).lstrip() + re.sub(" +", " ", Notes[157:202]) + re.sub(" +", " ",
                                                                                                            Notes[
                                                                                                            301:346]) + re.sub(
      " +", " ", Notes[456:503])).rstrip()
    dictList.append(myDict)
    del myDict
  pdfFile.close()
  return dictList
# a = getDict("C:\\Users\\simon\\Desktop\\pyCRC\\ircUpload1.0\\input\\yearAuth.pdf")
