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
        print('hi')
        for row in sheet:
            if len(funcs) == 1:
                out[funcs[0](row[0])] = funcs[0](row[1])
            else:
                out[funcs[0](row[0])] = funcs[1](row[1])
    return out
