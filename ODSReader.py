# Copyright 2011 Marco Conti

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Thanks to grt for the fixes

import odf.opendocument
from odf.table import Table, TableRow, TableCell
from odf.text import P

# http://stackoverflow.com/a/4544699/1846474
class GrowingList(list):
    def __setitem__(self, index, value):
        if index >= len(self):
            self.extend([None]*(index + 1 - len(self)))
        list.__setitem__(self, index, value)

class ODSReader:

    # loads the file
    def __init__(self, file, clonespannedcolumns=None):
        self.clonespannedcolumns = clonespannedcolumns
        self.doc = odf.opendocument.load(file)
        self.SHEETS = {}
        for sheet in self.doc.spreadsheet.getElementsByType(Table):
            self.readSheet(sheet)

    # reads a sheet in the sheet dictionary, storing each sheet as an
    # array (rows) of arrays (columns)
    def readSheet(self, sheet):
        name = sheet.getAttribute("name")
        rows = sheet.getElementsByType(TableRow)
        arrRows = []

        # for each row
        for row in rows:
            row_comment = ""
            arrCells = GrowingList()
            cells = row.getElementsByType(TableCell)

            # for each cell
            count = 0
            for cell in cells:
                # repeated value?
                repeat = cell.getAttribute("numbercolumnsrepeated")
                if(not repeat):
                    repeat = 1
                    spanned = int(cell.getAttribute('numbercolumnsspanned') or 0)
                    # clone spanned cells
                    if self.clonespannedcolumns is not None and spanned > 1:
                        repeat = spanned

                ps = cell.getElementsByType(P)
                textContent = ""

                # for each text/text:span node
                for p in ps:
                    for n in p.childNodes:
                        if (n.nodeType == 1 and
                                ((n.tagName == "text:span") or (n.tagName == "text:a"))):
                            for c in n.childNodes:
                                if (c.nodeType == 3):
                                    textContent = u'{}{}'.format(textContent, c.data)

                        if (n.nodeType == 3):
                            textContent = u'{}{}'.format(textContent, n.data)

                if(textContent):
                    if(textContent[0] != "#"):  # ignore comments cells
                        for rr in range(int(repeat)):  # repeated?
                            arrCells[count]=textContent
                            count+=1
                    else:
                        row_comment = row_comment + textContent + " "
                else:
                    for rr in range(int(repeat)):
                        count+=1

            # if row contained something
            if(len(arrCells)):
                arrRows.append(arrCells)

            #else:
            #    print ("Empty or commented row (", row_comment, ")")

        self.SHEETS[name] = arrRows

    # returns a sheet as an array (rows) of arrays (columns)
    def getSheet(self, name):
        return self.SHEETS[name]

def keyval_sheet_to_dict(sheet, sheetname, funcs=None):
    '''For a sheet with rows of 1 key and 1 value, returns a dictionary.
    sheet is an ODSReader().
    sheetname is the worksheet name.
    Example: keyval(sheet, sheetname, str, int)
    If only one function is provided, it will apply the function to keys and values.'''
    outsheet = sheet.getSheet(sheetname)
    out = {}
    if not funcs:
        for row in outsheet:
            out[row[0]] = row[1]
    else:
        for row in outsheet:
            if len(funcs) == 1:
                out[funcs[0](row[0])] = funcs[0](row[1])
            else:
                out[funcs[0](row[0])] = funcs[1](row[1])
    return out

def convert_dict_vals_to_objs_in_dict_of_dicts(dictin, objclass, depth=1):
    '''Converts, in place, a dict of dicts into a dict of objects, with any
    nesting depth. Typically depth will be the length of the keys of the
    dictionary, though this method is typically only called from within this
    module.'''
    assert depth >= 1, 'Depth must be 1 or higher.'
    if depth == 1:
        for k,v in dictin.items():
            dictin[k] = objclass(v)
    else:
        for k in dictin:
            convert_dict_vals_to_objs_in_dict_of_dicts(dictin[k], objclass, depth-1)

def dict_sheet_to_dict_of_objs(sheet, sheetname, objclass, keys=None, funcs=None, nones='fill'):
    '''Creates a dict of objects for a particular sheet in an ODSReader() object.
    sheet is an ODSReader().
    sheetname is the worksheet name.
    key is the column that should be the key of the new dict of objs
    objclass is the class that will be called via __init__(**kwargs), with kwargs populated from the rows.
    funcs are functions that should be applied to the data as it becomes entries in the dict.
    nones describes how to handle empty fields. 'fill' fills with None, 'trim' removes, 'string' fills with 'None'.'''
    out = dict_sheet_to_dict_of_dicts(sheet, sheetname, keys, funcs, nones)
    convert_dict_vals_to_objs_in_dict_of_dicts(out, objclass, len(keys))
    return out

def interpret_none(key, interpreted_dict, nones='fill'):
    '''Enters a value into row[key] based on nones.
    'fill' will enter a None
    'string' will enter 'None'
    'trim' is valid and will do nothing.
    Other values will raise assertion error.'''
    if nones == 'fill':
        interpreted_dict[key] = None
    elif nones == 'string':
        interpreted_dict[key] = 'None'
    else:
        assert nones == 'trim', f'Unknown interpretation of None: {nones}'

def row_to_dict(key_row, row, funcs=None, nones='fill'):
    '''Takes a row of a data from a spreadsheet (list), converts to a dict.
    Applies function to row items, with the default function being str'''
    out = {}
    for i,e in enumerate(key_row):
        # Is the examined element of the row populated?
        if len(row)-1 >= i:
            if row[i] is None:
                interpret_none(e, out, nones)
            else:
                # Does the examined element of the row have a function?
                if funcs is not None and len(funcs)-1 >= i:
                    out[e] = funcs[i](row[i])
                else:
                    # If element is beyond range of funcs, it defaults to str
                    out[e] = str(row[i])
        else:
            # If row doesn't extend this far, it is None
            interpret_none(e, out, nones)
    return out                
    
def rows_to_list_of_dicts(sheet, funcs=None, nones='fill'):
    '''Outputs a list of dicts from a spreadsheet, accepting functions to change the elements of the dicts.
    First row is labels and is untouched. If number of elements exceeds the functions provided, the rest are just handled as strings.
    Nones by default are "fill" (with None), "trim" (exclude from the dict), and "string" ("None")...'''
    out = []
    key_row = sheet[0]
    for row in sheet[1:]:
        out.append(row_to_dict(key_row, row, funcs, nones=nones))
    return out

def dict_to_dict_of_dicts(dictin, keys):
    '''Given keys, this creates a nested dictionary (any depth).'''
    # Because this assumes creating a single dict of dicts using a single dict,
    # no caution has to be taken to avoid overwriting,
    # and therefore you can populate from the innermost to outermost layer.
    assert keys != [], 'keys can not be empty list.'
    out = {}
    out[dictin[keys[-1]]] = dictin
    if len(keys) > 0:
        for k in reversed(keys[:-1]):
            temp = out
            out = {}
            out[dictin[k]] = temp
    return out


def add_dict_to_dict_of_dicts(dictin, keys, out):
    '''Adds a dict to a dict of dicts.'''
    assert keys, 'Need populated list.'
    if len(keys) >= 2:
        # If you have further depth before populating.
        if dictin[keys[0]] in out:
            out = out[dictin[keys[0]]]
            add_dict_to_dict_of_dicts(dictin, keys[1:], out)
        else:
            out[dictin[keys[0]]] = {}
            out = out[dictin[keys[0]]]
            add_dict_to_dict_of_dicts(dictin, keys[1:], out)
    else:
        out[dictin[keys[0]]] = dictin
        
def list_of_dicts_to_dict_of_dicts(dicts, keys):
    '''Converts list of dicts into dict of dicts (any depth).'''
    out = {}
    for d in dicts:
        add_dict_to_dict_of_dicts(d, keys, out)
    return out
    
def dict_sheet_to_dict_of_dicts(sheet, sheetname, keys, funcs=None, nones='fill'):
    '''Creates a dict of dicts (a mini-database) for a particular sheet in an ODSReader() object.
    sheet is an ODSReader().
    sheetname is the worksheet name.
    key is the column that should be the key of the new dict of dicts
    funcs are functions that should be applied to the data as it becomes entries in the dict.
    nones describes how to handle empty fields. 'fill' fills with None, 'trim' removes, 'string' fills with 'None'.'''
    out = sheet.getSheet(sheetname)
    out = rows_to_list_of_dicts(out, funcs, nones)
    out = list_of_dicts_to_dict_of_dicts(out, keys)
    return out


def dict_sheet_to_list_of_dicts(sheet, sheetname, keys, funcs=None, nones='fill'):
    '''Creates a list of dicts for a particular sheet in an ODSReader() object.
    sheet is an ODSReader().
    sheetname is the worksheet name.
    key is the column that should be the key of the new dict of dicts
    funcs are functions that should be applied to the data as it becomes entries in the dict.
    nones describes how to handle empty fields. 'fill' fills with None, 'trim' removes, 'string' fills with 'None'.'''
    out = sheet.getSheet(sheetname)
    out = rows_to_list_of_dicts(out, funcs, nones)
    return out
