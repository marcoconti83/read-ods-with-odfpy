#! /usr/bin/python3
def dict_sheet_to_dict(sheet, *funcs):
    '''For a sheet with rows of keys and values, creates a dictionary from it with functions applied to the keys or keys and values, or none.
    Example: keyval(sheet, str, int)
    If only one function is provided, it will apply the function to keys and values.'''
    out = {}
    if not funcs:
        for row in sheet:
            out[row[0]] = row[1]
    else:
        for row in sheet:
            if len(funcs) == 1:
                out[funcs[0](row[0])] = funcs[0](row[1])
            else:
                out[funcs[0](row[0])] = funcs[1](row[1])
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
    
def dict_of_dicts_from_list_of_dicts(key, dicts):
    assert False, 'Incomplete'
    # I want this to return a dict which is keyed by a field given by key,
    # and then it will be a dict of dicts.
    
