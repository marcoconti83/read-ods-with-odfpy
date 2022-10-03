#! /usr/bin/python3

def keyval(table, func=None):
    out = {}
    for row in table:
        if func is not None:
            out[func(row[0])] = func(row[1])
        else:
            out[row[0]] = row[1]
    return out
