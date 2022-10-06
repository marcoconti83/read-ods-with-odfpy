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
def record_reader(sheet, *funcs):
    '''Outputs a list of dicts from a spreadsheet, accepting functions to change the elements of the dicts.
    First row is labels and is untouched. If number of elements exceeds the functions provided, the rest are just handled as strings.'''
    out = []
    first_row = sheet[0]
    for row in sheet[1:]:
        record = {}
        if not funcs:
            for i,e in enumerate(row):
                record[first_row[i]] = e
        else:
            for i,e in enumerate(row):
                if i+1 <= len(funcs):
                    func = funcs[i]
                else:
                    func = str
                record[first_row[i]] = func(e)
        out.append(record)
    return out
    
    
