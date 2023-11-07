# multiple variables are replaced to keep anonominity of patients and company operations

import glob
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from termcolor import colored
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger

dr = os.path.dirname(os.path.realpath(__file__))
import pdfToDict

startRow = int(open(dr + '\\input\\start.txt', "rt").readlines()[0])
# head = int(input('Headless? 1 = Yes, 0 = No'))
head = 1
op = webdriver.ChromeOptions()
global driver
try:
  if head == int(1):
    op.add_argument('--headless')
    driver = webdriver.Chrome(dr + '\\.dont\\chromedriver.exe', options=op)
  if head == int(0):
    driver = webdriver.Chrome(dr + '\\.dont\\chromedriver.exe')
except:
  print('Old version of chrome, program ended')
  driver = webdriver.Chrome(dr + '\\.dont\\chromedriver.exe')
driver.implicitly_wait(30)
# driver.implicitly_wait(1)
inputFile = dr + "\\input\\merged.pdf"
outDir = dr + "\\output"
tempDir = dr + "\\temp"
genLogin = []
if os.path.isfile(dr + r'/.dont/login.txt'):
  with open(dr + r"/.dont/login.txt", 'r') as f:
    genLogin.append(f.readline().rstrip())
    genLogin.append(f.readline().rstrip())
  print('Your current login information is: ' + genLogin[0] + "; " + genLogin[1])
  print('to change this close the program, go to /.dont and delete login.txt')
else:
  genLogin = []
  print("Input your generations login information")
  genLogin.append(input('Username:'))
  genLogin.append(input('Password:'))
  with open(dr + r"/.dont/login.txt", 'w') as f:
    f.write("\n".join(genLogin))
print("Interpreting authorization PDF")
dictList = pdfToDict.getDict(inputFile)
print("Success, finished interpretation")
generationsDict = {}
df = pd.read_csv(dr + r"\input\serviceCodes.csv")
for i in range(0, df.shape[0]):
  generationsDict[str(df['authCode'][i])] = (df['genCode'][i], df['q'][i])

def goTab(a):
  while len(driver.window_handles) <= a:
    time.sleep(.05)
  driver.switch_to.window(driver.window_handles[a])


def login(username, password):
  print("logging in")
  driver.get("https://ONLINEDB.com/views/loginnew.aspx")
  driver.find_element_by_name('txtAgencyID').send_keys("ORGCODE")
  driver.find_element_by_name('txtLogin').send_keys(username)
  driver.find_element_by_name('txtPassword').send_keys(password)
  driver.find_element_by_name('btnUserLogin').click()  # popup name is "lnkCancel"
  time.sleep(2)
  try:
    driver.find_element_by_id('lnkCancel').click()
  except Exception:
    pass

def restart():
  import sys
  print("argv was", sys.argv)
  print("sys.executable was", sys.executable)
  print("restart now")
  import os
  os.execv(sys.executable, ['python'] + sys.argv)

def go(code, iteration):
  page = iteration + 1
  time.sleep(.1)
  st = int(time.time())
  x = 15
  while True:
    try:
      exec(code)
    except Exception:
      time.sleep(.5)
    else:
      break
    if int(time.time()) - st > x:
      if x == 15:
        print(colored(str(int(time.time()) - st), 'green'), " seconds has passed trying to execute ", code, " restarting chrom webdriver")
        driver.refresh()
        x = 45
      else:
        print(colored(str(int(time.time()) - st), 'green'), " seconds has passed trying to execute ", code, " restarting program")
        with open(r'C:\Users\simon\Desktop\pyCRC\ircUpload1.0\input\start.txt', 'w') as f:
          f.write(str(page))
        time.sleep(1)
        restart()

def clientIDSearch(clientID, i):
  with open(r'C:\Users\simon\Desktop\pyCRC\ircUpload1.0\input\start.txt', 'w') as f:
    f.write(str(i + 1))
  go('''driver.find_element_by_id("ctl00_MainContent_ddlType").send_keys("All")''', i)
  go('''driver.find_element_by_id("ctl00_MainContent_imgCustomFilter").click()''', i)  # Custom Filter
  time.sleep(2)
  go('''driver.switch_to.frame("frameMainArea")''', i)  # switches frame to custom filter popup
  go("""driver.find_element_by_id("ctl00_cphPopup_ddlSearch").send_keys("All")""", i)
  go("""driver.find_element_by_id("ctl00_cphPopup_ddlIn").send_keys("Medical Record")""", i)
  driver.find_element_by_name("ctl00$cphPopup$txtFor").send_keys(str(clientID))
  go("""driver.find_element_by_name("ctl00$cphPopup$btnOk").click()""", i)
  go(
    """driver.switch_to.default_content()""", i)  # ctl00_MainContent_rptClientList_ctl01_ClientName ID for each entry increases ct by 1


login(genLogin[0], genLogin[1])
driver.find_element_by_id('ctl00_MainContent_aClientsImg').click()  # Clients
while len(driver.window_handles) == 1:
  time.sleep(.05)
goTab(0)  # begin close landing page
driver.close()
goTab(0)  # end close landing page
for i, myDict in enumerate(dictList):
  if int(myDict['date'].split('/')[2]) < 21:
    print("page " + str(myDict['pdfPage']) + " year is less than 21")
    continue
  if i + 1 < startRow:  # or i + 1 > endPage:
    print("page " + str(myDict['pdfPage']) + " skipped")
    continue
  startTime2 = time.time()
  print(str(myDict['pdfPage']) + ": " + myDict['lastName'] + ", " + myDict['firstName'] + "; " + myDict['clientId'])
  print(myDict)
  clientIDSearch(myDict['clientId'], i)
  """Check if authcode is in generations"""
  inGen = True
  """Check if Client ID is in generations"""
  start_time = time.time()
  goBreak = 0
  while True:
    current_time = time.time()
    elapsed_time = current_time - start_time
    if elapsed_time > 15:
      print(colored("ERROR-0000: ", "red"), "Client ID not found, page ", str(myDict['pdfPage']))
      with open(inputFile, "rb") as f:
        inputPDF = PdfFileReader(f)
        outputPDF = PdfFileWriter()
        outputPDF.addPage(inputPDF.getPage(i))
        with open(dr + r"/output/newAuths/" + myDict['lastName'] + ", " + myDict['firstName'] + ".pdf",
                  "wb") as outputStream:
          outputPDF.write(outputStream)
          outputStream.close()
        f.close()
      goBreak = 1
      break
    try:
      driver.find_element_by_id("ctl00_MainContent_rptClientList_ctl01_ClientName").click()
    except:
      time.sleep(.2)
    else:
      break
  if goBreak == 1:
    continue
  goTab(1)
  """Add Note"""
  go('''driver.find_element_by_id('ctl00_MainContent_tmpNotes').click()''', i)  # switch to notes tab
  go(
    '''driver.find_element_by_id('ctl00_MainContent_ClientNotes_dlClientNotes_ctl00_lnkAdd').click()''', i)  # click new note
  myNotes = "AUTOMATED POS UPDATE**********\n\n"
  for j in range(len(myDict['AUl'])):
    if generationsDict[myDict['DOSl'][j]][1] == 1:
      aMonth = "THREE MONTHS"
    else:
      aMonth = "month"
    myNotes = myNotes + str(myDict['AUl'][j]) + " hours per " + str(aMonth) + " from " + str(
      myDict['authFl'][j]) + " to " + str(myDict['authTl'][j]) + " " + str(generationsDict[myDict['DOSl'][j]][0]) + "\n"
  myNotes = myNotes.strip('\n')
  myNotes = myNotes + "\nAttached Authorization Notes:\n" + str(myDict['notes'])
  go(
    '''driver.find_element_by_id('ctl00_MainContent_ClientNotes_dlClientNotes_ctl00_ddlNOteTypeA').send_keys('UPDATED AUTH')''', i)  # set note type
  driver.find_element_by_id('ctl00_MainContent_ClientNotes_dlClientNotes_ctl00_txtNotesA').send_keys(myNotes)
  go('''driver.find_element_by_name('ctl00$MainContent$ClientNotes$dlClientNotes$ctl00$lnkInsert').click()''', i)  # save note
  """Adding attatchment"""
  time.sleep(2)
  go("""driver.find_element_by_id("ctl00_MainContent_tmpAttachments").click()""", i)  # switch to attatchments tab
  # Add all attatchment descriptions to a list
  time.sleep(4)
  count, entries, nonono = 0, [], 0
  while True:
    if count == 0:  # first iteration waits for element to load before reading
      try:
        charizard = WebDriverWait(driver, 15).until(EC.presence_of_element_located(
          (By.ID, "ctl00_MainContent_Attachments_dlAttachments_ctl01_lblDescription")))
        entries.append((r"01", str(charizard.text)))
      except:
        nonono = 1
        break
      count = count + 1
      continue
    else:
      driver.implicitly_wait(1)  # sets wait for element searches for 1 second
    if nonono == 0:
      entry = str(count + 1)
      if int(entry) < 10:  # formatting purposes for searching for the ID
        entry = str(0) + entry
      try:
        bulbasaur = "ctl00_MainContent_Attachments_dlAttachments_ctl" + entry + "_lblDescription"
        entries.append((entry, str(driver.find_element_by_id(bulbasaur).text)))
      except Exception:
        break
      count = count + 1
  driver.implicitly_wait(25)  # reverts to 25 second wait time before closing program
  attatchDescription = (  # possible description matches for attatchments to delete
    "POS " + myDict['date'], " ".join(["POS", myDict['firstName'], myDict['lastName'], myDict['date']]))
  matches = []
  for j in entries:  # compiles list of matches
    if j[1] in attatchDescription:
      matches.append(j)
  if not len(matches) > 0:
    """Create a page from the authorization PDF to upload to generations"""
    with open(inputFile, "rb") as f:
      inputPDF = PdfFileReader(f)
      outputPDF = PdfFileWriter()
      outputPDF.addPage(inputPDF.getPage(int(myDict['pdfPage']) - 1))
      with open(tempDir + "\\" + "Authorization.pdf", "wb") as outputStream:
        outputPDF.write(outputStream)
        outputStream.close()
      f.close()
    # back to web stuff
    go(
      """driver.find_element_by_id("ctl00_MainContent_Attachments_dlAttachments_ctl00_lnkAdd").click()""", i)  # add attatchment
    driver.find_element_by_id(
      "ctl00_MainContent_Attachments_dlAttachments_ctl00_FileAttachment_fuAttachment").send_keys(
      tempDir + "\\Authorization.pdf")
    driver.find_element_by_id(
      "ctl00_MainContent_Attachments_dlAttachments_ctl00_FileAttachment_txtDescription").send_keys(
      "POS " + myDict['date'])  # Add auth description
    driver.find_element_by_id(
      "ctl00_MainContent_Attachments_dlAttachments_ctl00_FileAttachment_lnkInsert").click()  # save
    os.remove(tempDir + "\\" + "Authorization.pdf")
  """Adding Service Order"""
  for j in range(0, len(myDict['DOSl'])):
    go('''driver.find_element_by_id("ctl00_MainContent_tmpServiceOrders").click()''', i)  # switch to service orders tab
    print("auth " + str(j + 1) + " of " + str(len(myDict['DOSl'])))
    go(
      '''driver.find_element_by_id("ctl00_MainContent_ServiceOrderList_rptServiceOrders_ctl00_lnkAdd").click()''', i)  # add SO
    scode = generationsDict[myDict['DOSl'][j]][0]
    driver.find_element_by_name("ctl00$MainContent$txtService").send_keys(str(scode) + Keys.ENTER)  # add Service Code
    time.sleep(.2)
    driver.find_element_by_id("ctl00_MainContent_txtHours").send_keys("24")  # input daily hours
    time.sleep(1)
    driver.find_element_by_id("ctl00_MainContent_txtAuthorization").send_keys(myDict['authNum'])  # input auth num
    driver.find_element_by_id("ctl00_MainContent_dpStatus").send_keys("A")  # set client as active
    driver.find_element_by_id("ctl00_MainContent_txtPatientNo").send_keys(
      myDict['clientId'])  # enter UCI into Patient Number
    driver.find_element_by_id("ctl00_MainContent_DateRange_txtStartDate").clear()  # fill start and end dates
    driver.find_element_by_id("ctl00_MainContent_DateRange_txtStartDate").send_keys(myDict['authFl'][j])
    driver.find_element_by_id("ctl00_MainContent_DateRange_txtEndDate").clear()
    driver.find_element_by_id("ctl00_MainContent_DateRange_txtEndDate").send_keys(myDict['authTl'][j])
    go('''driver.find_element_by_id("ctl00_MainContent_Recurrence_btnAllDays").click()''', i)  # click all days
    time.sleep(1)
    scoders = driver.find_element_by_name("ctl00$MainContent$txtService").get_property('value')
    if scode != scoders:  # error handling for new service codes
      print(" ".join((colored(scode, 'red'), "vs", scoders)))
      print(" ".join((colored("SCODERS ALERT! UCI", 'red'), myDict['clientId'], "Auth", str(j + 1), "of",
                      str(len(myDict['DOSl'])), "is SCODERS")))
    go(
      '''driver.find_element_by_id("ctl00_MainContent_dlstAuthorizations_ctl00_lnkAdd").click()''', i)  # create new 8.13 rule
    go(
      '''driver.find_element_by_id("ctl00_MainContent_dlstAuthorizations_ctl00_ddlType").send_keys("Units")''', i)  # set rules
    driver.find_element_by_id("ctl00_MainContent_dlstAuthorizations_ctl00_ddlTimespan").send_keys("Calendar Month")
    go('''driver.find_element_by_name("ctl00$MainContent$dlstAuthorizations$ctl00$txtMaxUnitsorDollars").clear()''', i)
    time.sleep(.1)
    driver.find_element_by_name("ctl00$MainContent$dlstAuthorizations$ctl00$txtMaxUnitsorDollars").send_keys(
      myDict['AUl'][j])
    go('''driver.find_element_by_id("ctl00_MainContent_txtNotes").send_keys(myDict['notes'])''', i)  # add notes
    go('''driver.find_element_by_id("ctl00_MainContent_dlstAuthorizations_ctl00_ImgAdd").click()''', i)  # save rules
    time.sleep(1)
    go('''driver.find_element_by_id("ctl00_MainContent_btnManualOverride").click()''', i)  # manual overrride
    time.sleep(1.2)
    go('''driver.find_element_by_id("ctl00_MainContent_txtTotalUnit").clear()''', i)  # input total approved units
    if generationsDict[myDict['DOSl'][j]][1] == 1:
      quarter = int(myDict['AUl'][j]) * int(myDict['maxMonthsl'][j]) / 3
    else:
      quarter = int(myDict['AUl'][j]) * int(myDict['maxMonthsl'][j])
    driver.find_element_by_id("ctl00_MainContent_txtTotalUnit").send_keys(str(quarter))
    driver.find_element_by_id("ctl00_MainContent_txtAmount").clear()  # input total amount approved
    driver.find_element_by_id("ctl00_MainContent_txtAmount").send_keys(myDict['maxAuthAmountl'][j])
    driver.find_element_by_id("ctl00_MainContent_txtVisits").clear()  # input total approved visits
    driver.find_element_by_id("ctl00_MainContent_txtVisits").send_keys(str(int(myDict['maxMonthsl'][j]) * 30))
    pikachu = WebDriverWait(driver, 30).until(
      EC.element_to_be_clickable((By.ID, 'ctl00_MainContent_btnManualOverrideSave'))
    )
    go('''driver.find_element_by_id("ctl00_MainContent_btnManualOverrideSave").click()''', i)  # save override
    time.sleep(1)
    go('''driver.find_element_by_id('ctl00_MainContent_btnOK').click()''', i)  # save button
    time.sleep(1)
    go('''driver.find_element_by_id("ctl00_MainContent_btnClose").click()''', i)  # close button
    time.sleep(1)
  driver.close()
  goTab(0)
  print(colored(str(int(time.time() - startTime2)), 'blue'), 'seconds to complete')
"""Combine New Authorizations"""
print("Making newAuth report")
newAuths = glob.glob(dr + r"/output/newAuths/*.pdf")
merger = PdfFileMerger()
if len(newAuths) > 0:
  for i in newAuths:
    merger.append(i)
  merger.write(dr + r'\output\newAuths.pdf')
  merger.close()
  for i in newAuths:
    os.remove(i)
else:
  print("No new auths")
  try:
    os.remove(dr + r'\output\newAuths.pdf')
  except:
    pass
with open(r'C:\Users\simon\Desktop\pyCRC\ircUpload1.0\input\start.txt', 'w') as f:
  f.write(str(1))
print('set start to 1, done')
