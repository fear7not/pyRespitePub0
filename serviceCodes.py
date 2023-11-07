import pandas as pd
from pdfToDict import *
import os
dr = os.path.dirname(os.path.realpath(__file__))

print('serviceCodes.py begin')
a = getDict(dr + "\\input\\merged.pdf")
new, row = [], []
df1 = pd.read_csv(dr + r'/input/serviceCodes.csv')
unique = df1['authCode'].tolist()
print(len(a), 'pages')
newFlag = False
for i in a:
    for j in range(0, len(i['DOSl'])):
        k = i['DOSl'][j]
        if k not in unique:
            newFlag = True
            unique.append(k)
            new.append(k)
            row.append({'authCode': k, 'rate': i['UCl'][j], 'genCode': "", 'q': "", 'inGen': "0"})
df = df1.append(row)
print(str(len(row)) + " new service codes")

df.to_csv(dr + r"/input/serviceCodes.csv", index=False)
print('serviceCodes.py end')