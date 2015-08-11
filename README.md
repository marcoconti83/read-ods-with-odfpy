read-ods-with-odfpy
===================

As seen on: http://www.marco83.com/work/173/read-an-ods-file-with-python-and-odfpy

Odfpy is a python library to read and write OpenDocument documents (such as the .odt or.ods created with OpenOffice.org). However, the documentation and examples shipped with Odfpy are more oriented to writing new documents rather than reading existing ones.

Failing to find any simple spreadsheet reading code snippet on the internet, I wrote a simple ODS reader in python that reads an entire .ods file in a dictionary of sheets, where each sheets is stored as an array of arrays (rows, columns). It still requires Odfpy to run.

It has been tested with odfpy 0.9.3 and 1.3.0, python 2.7 and 3.4, using ods files created with OpenOffice.org. Here’s the script: Odf to array Python script.

Usage example:

```python
from ODSReader import ODSReader

doc = ODSReader(u'films.ods', clonespannedcolumns=True)
table = doc.getSheet(u'Sheet1')
for i in range(len(table)):
    for j in range(len(table[i])):
        print (table[i][j])
```

Requirements
-----------------
 * odfpy 0.9.3 or 1.3.0
 * python 2.7 or 3.4
