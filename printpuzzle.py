#!/usr/bin/python
from puzzles import printer
import os,sys,getopt

options = getopt.gnu_getopt(sys.argv[1:],"o:p:d:s:",["image=","title=","color=","help"])

directory = "/tmp"
orderid = "1"
puzzleid = "1"
image = "s3://puzzle-live/puzzle/images/print/puzzle_01010101-0101-0101-0101010101010101.jpg"
title = "Dein Titel"
color = "#FFFFFF"
puzzlesize = "1000"

for t in options[0]:
    if t[0]=="-o":
        orderid = t[1]
    if t[0]=="-p":
        puzzleid = t[1]
    if t[0]=="-d":
        if "ftp" == t[1]:
            directory = None
        else:
            directory = t[1]
    if t[0]=="-s":
        puzzlesize = t[1]
    if t[0]=="--image":
        image = t[1]
    if t[0]=="--title":
        title = t[1]
    if t[0]=="--color":
        color = t[1]

if orderid=="1" or puzzleid=="1":
    print "Usage: "+sys.argv[0]+" -o<id> -p<id> [-d<dir> ][-s<size> ][--image=<image> ][--title=<title> ][--color=<color>]"
    sys.exit(0)

print "rendering puzzle order: %s,%s,%s,%s,%s,%s in %s"%(orderid,puzzleid,image,title,color,puzzlesize,directory)
barcode = printer.demo(directory,image,title,color=color,puzzle_type=puzzlesize,orderid=orderid,puzzleid=puzzleid)
print "rendered barcode %s"%(barcode)
