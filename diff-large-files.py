#!/usr/bin/python

import sys

def resync(line_l, line_r, left, right):
    """Return a quadruple of

    (difflines_l, difflines_r, buflines_l, buflines_r)

    where difflines are lines that differ (and get a + or - before
    them in unified diff output). Since we have to read past the point
    of differences into the place where lines start matching again, we
    end up with some lines that should not be part of the difference
    set, these are put into buflines.

    """
    # We know that the given line_l and line_r differ:
    seen_l = {line_l:0}
    seen_r = {line_r:0}
    out_l = [line_l]
    out_r = [line_r]
    while 1:
        line_l = left.readline()
        line_r = right.readline()
        if not line_l and not line_r:
            return ( out_l, out_r,
                     [],    [] )
        elif not line_l:
            return ( out_l, out_r,
                     [],    [line_r] )
        elif not line_r:
            return ( out_l,    out_r,
                     [line_l], [] )
        elif line_l == line_r:
            return ( out_l,    out_r,
                     [line_l], [line_r] )
        elif line_l in seen_r:
            seen_l_in_r = seen_r[line_l]
            return ( out_l,    out_r[:seen_l_in_r],
                     [line_l], out_r[seen_l_in_r:]+[line_r] )
        elif line_r in seen_l:
            seen_r_in_l = seen_l[line_r]
            return ( out_l[:seen_r_in_l],          out_r,
                     out_l[seen_r_in_l:]+[line_l], [line_r] )
        else:
            seen_l[line_l] = len(out_l)
            seen_r[line_r] = len(out_r)
            out_l.append(line_l)
            out_r.append(line_r)

def getline(file, buffer):
    if buffer:
        return buffer[0], buffer[1:]
    else:
        return file.readline(), buffer

def run(left, right):
    buf_l, buf_r = [], []
    while 1:
        line_l, buf_l = getline(left, buf_l)
        line_r, buf_r = getline(right, buf_r)
        if not line_l and not line_r:
            break
        elif not line_r:
            print "-"+line_l,
        elif not line_l:
            print "+"+line_r,
        elif line_l == line_r:
            print " "+line_l,
        else:
            out_l, out_r, buf_l, buf_r = resync(line_l, line_r, left, right)
            print "".join(["-%s"%(l,) for l in out_l]), "".join(["+%s"%(r,) for r in out_r]),

try:
    left=open(sys.argv[1], 'r')
    right=open(sys.argv[2], 'r')
    run(left, right)
except IOError, e:
    print e
    sys.exit(1)

