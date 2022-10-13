#! /usr/bin/python3
def keyval_sheet_to_dict(sheet, sheetname, *funcs):
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

def dict_of_dicts_to_dict_of_objs(dict_of_dicts, objclass):
    '''Given a dict of dicts, outputs a dict of objects using the dict_of_dicts values.items as **kwargs.'''
    out = {}
    for (k,v) in dict_of_dicts.items():
        out[k] = objclass(**v)
    return out

def dict_sheet_to_dict_of_objs(sheet, sheetname, key, objclass, *funcs, nones='fill'):
    '''Creates a dict of objects for a particular sheet in an ODSReader() object.
    sheet is an ODSReader().
    sheetname is the worksheet name.
    key is the column that should be the key of the new dict of objs
    objclass is the class that will be called via __init__(**kwargs), with kwargs populated from the rows.
    funcs are functions that should be applied to the data as it becomes entries in the dict.
    nones describes how to handle empty fields. 'fill' fills with None, 'trim' removes, 'string' fills with 'None'.'''
    out = sheet.getSheet(sheetname)
    out = rows_to_list_of_dicts(out, *funcs, nones=nones)
    out = dict_of_dicts_from_list_of_dicts(key, out)
    out = dict_of_dicts_to_dict_of_objs(out, objclass)
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

def row_to_dict(key_row, row, *funcs, nones='fill'):
    '''Takes a row of a data from a spreadsheet (list), converts to a dict.'''
    out = {}
    for i,e in enumerate(key_row):
        # Is the examined element of the row populated?
        if len(row)-1 >= i:
            if row[i] is None:
                interpret_none(e, out, nones)
            else:
                # Does the examined element of the row have a function?
                if len(funcs)-1 >= i:
                    out[e] = funcs[i](row[i])
                else:
                    out[e] = str(row[i])
        else:
            # If not, it can be assumed to be None
            interpret_none(e, out, nones)
    return out                
    
def rows_to_list_of_dicts(sheet, *funcs, nones='fill'):
    '''Outputs a list of dicts from a spreadsheet, accepting functions to change the elements of the dicts.
    First row is labels and is untouched. If number of elements exceeds the functions provided, the rest are just handled as strings.
    Nones by default are "fill" (with None), "trim" (exclude from the dict), and "string" ("None")...'''
    out = []
    first_row = sheet[0]
    for row in sheet[1:]:
        out.append(row_to_dict(first_row, row, *funcs, nones=nones))
    return out
    
def dict_of_dicts_from_list_of_dicts(key, list_of_dicts):
    '''Takes a list of dicts and indexes them by key into a dict of dicts.'''
    out = {}
    while list_of_dicts:
        outdict = list_of_dicts.pop()
        outkey = outdict.pop(key)
        out[outkey] = outdict
    return out


def dict_sheet_to_dict_of_dicts(sheet, sheetname, key, *funcs, nones='fill'):
    '''Creates a dict of dicts (a mini-database) for a particular sheet in an ODSReader() object.
    sheet is an ODSReader().
    sheetname is the worksheet name.
    key is the column that should be the key of the new dict of dicts
    funcs are functions that should be applied to the data as it becomes entries in the dict.
    nones describes how to handle empty fields. 'fill' fills with None, 'trim' removes, 'string' fills with 'None'.'''
    out = sheet.getSheet(sheetname)
    out = rows_to_list_of_dicts(out, *funcs, nones=nones)
    out = dict_of_dicts_from_list_of_dicts(key, out)
    return out
