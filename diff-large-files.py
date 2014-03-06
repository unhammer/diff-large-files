#!/usr/bin/python

import sys, argparse

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

def join_prepend(prefix, list):
    return "".join("%s%s"%(prefix,l) for l in list)

def run(left, right, n_unified):
    seendiff=False
    n_bef = n_unified
    n_aft = n_unified
    ctx_bef = []
    ctx_aft = 0
    buf_l, buf_r = [], []
    while 1:
        line_l, buf_l = getline(left, buf_l)
        line_r, buf_r = getline(right, buf_r)
        if not line_l and not line_r:
            break
        elif not line_r:
            sys.stdout.write("-"+line_l)
        elif not line_l:
            sys.stdout.write("+"+line_r)
        elif line_l == line_r:
            if ctx_aft:
                sys.stdout.write(join_prepend(" ",[line_l]))
                ctx_aft-=1
            elif n_bef:
                # Keep a sliding window:
                ctx_bef.append(line_l)
                ctx_bef = ctx_bef[-n_bef:]
        else:
            if not seendiff:
                sys.stdout.write("--- %s  %s\n+++ %s  %s\n"%(left.name,"dateTODO",right.name,"dateTODO"))
                # TODO file-modification-time
                seendiff=True
            out_l, out_r, buf_l, buf_r = resync(line_l, line_r, left, right)
            if not ctx_aft: # TODO: should also not print if no ctx_bef (or something; ie. when we're right after the previous resync)
                sys.stdout.write("@@ -0,0 +0,0 @@\n")
                # TODO: Getting the line numbers in here would require
                # buffering some lines and then printing the whole
                # chunk, to get the line numbers right. At the moment,
                # dwdiff --diff-input accepts this hack so I'm not
                # sure I can be bothered.
            sys.stdout.write(join_prepend(" ", ctx_bef))
            sys.stdout.write(join_prepend("-", out_l))
            sys.stdout.write(join_prepend("+", out_r))
            ctx_bef = []
            ctx_aft = n_aft



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('left',
                        type=str,
                        help='Old file')
    parser.add_argument('right',
                        type=str,
                        help='New file')
    parser.add_argument('-U', '--unified',
                        metavar='NUM',
                        type=int,
                        default=3,
                        help='How many context lines to show before and after.')
    args = vars(parser.parse_args())
    left=open(args['left'], 'r')
    right=open(args['right'], 'r')
    run(left, right, args['unified'])

if __name__ == "__main__":
    sys.exit(main())
