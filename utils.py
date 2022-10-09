#! /usr/bin/python3
def keyval(sheet, *funcs):
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

# perhaps use namedtuple instead
def record_reader(sheet, *funcs, nones='fill'):
    '''Outputs a list of dicts from a spreadsheet, accepting functions to change the elements of the dicts.
    First row is labels and is untouched. If number of elements exceeds the functions provided, the rest are just handled as strings.
    Nones by default are...'''
    assert False, 'Incomplete.'
    # nones fill = give it a None
    # nones trim = leave it out of the dict, rather than adding 'None'
    # nones string = 'None'
    out = []
    first_row = sheet[0]
    for row in sheet[1:]:
        record = {}
        if not funcs:
            for i,e in enumerate(row):
                if trim_None:
                    if e is not None:
                        record[first_row[i]] = e
                else:
                    record[first_row[i]] = e
        else:
            for i,e in enumerate(row):
                if trim_None:
                    if e is not None:
                        if i+1 <= len(funcs):
                            func = funcs[i]
                        else:
                            func = str
                else:
                    if i+1 <= len(funcs):
                        func = funcs[i]
                    else:
                        func = str
                record[first_row[i]] = func(e)
        out.append(record)
    return out
    
def dict_of_dicts_from_list_of_dicts(key, dicts):
    assert False, 'Incomplete'
    # I want this to return a dict which is keyed by a field given by key,
    # and then it will be a dict of dicts.
    
