from puzzlesettings import *

import os
from reportlab.pdfbase import pdfmetrics

from reportlab.lib import colors
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.utils import ImageReader
from reportlab.graphics import barcode,shapes
from reportlab.lib.colors import Color,HexColor
from PIL import Image

PUZZLEPRINTERURL = "www.puzzleprinter.de"
PUZZLEPRINTERSLOGAN = "wir machen ihr Puzzle"
PUZZLESIZES = {
    "200":"ca. 42,1x29,8cm",
    "500":"ca. 47,6x32,2cm",
    "600":"",
    "1000":"ca. 65,7x47,7cm",
}

#PUZZLEFONTPLAIN = "LibrisADFStd-Regular"
#PUZZLEFONTPLAIN = "GFSBodoni-Regular"
#PUZZLEFONTPLAIN = "LinLibertine"
#PUZZLEFONTPLAIN = "NimbusSanL-Regu"
#PUZZLEFONTPLAIN = "Verdana"
PUZZLEFONTPLAIN = "Nimbus"
#PUZZLEFONTPLAIN = "Helvetica"
#PUZZLEFONTOBLIQUE = "LibrisADFStd-Italic"
#PUZZLEFONTOBLIQUE = "GFSBodoni-Italic"
#PUZZLEFONTOBLIQUE = "LinLibertineI"
#PUZZLEFONTOBLIQUE = "NimbusSanL-ReguItal"
#PUZZLEFONTOBLIQUE = "Verdana-Italic"
PUZZLEFONTOBLIQUE = "LiberationSans-Italic"
#PUZZLEFONTOBLIQUE = "Helvetica-Oblique"

def registerfont(folder,afm,pfb,name):
    afmFile = os.path.join(folder,afm)
    pfbFile = os.path.join(folder,pfb)
    justFace = pdfmetrics.EmbeddedType1Face(afmFile, pfbFile)
    faceName = name
    pdfmetrics.registerTypeFace(justFace)
    justFont = pdfmetrics.Font(name,faceName,'WinAnsiEncoding')
    pdfmetrics.registerFont(justFont)

def renderpart(canvas,renderfk,args,trafo=None):
    canvas.saveState()
    if trafo:
        canvas.rotate(trafo[0])
        canvas.translate(trafo[1],trafo[2])
    apply(renderfk,args)
    canvas.restoreState()

def runtemplate(template,trafos,canvas,args,width,height):
    for t in template:
        if t[0]:
            trafo = trafos[t[0]]
            args[8] = trafo[3]*mm
            args[9] = trafo[4]*mm
            renderpart(canvas,t[1],list(args),(trafo[0],trafo[1]*mm,trafo[2]*mm))
        else:
            args[8] = width*mm
            args[9] = height*mm
            renderpart(canvas,t[1],list(args))

def fillcolor(puzzletype,templatedir,canvas,orientation,color,image,title,barcode,width,height):
    color = HexColor(color)
    color.alpha = None
    canvas.setFillColor(color)
    canvas.rect(0,0,width,height,fill=True,stroke=False)

t200files = (
    "light_h_bg.png", "light_h_f.png", "light_h_s.png",
    "light_h_f_bg.png", "light_h_f_p.png", "light_h_f_b.png",
    "light_h_s_bg.png", "light_h_s_p.png", "light_h_s_b.png",
    "light_v_bg.png", "light_v_f.png", "light_v_s.png",
    "light_v_f_bg.png", "light_v_f_p.png", "light_v_f_b.png",
    "light_v_s_bg.png", "light_v_s_p.png", "light_v_s_b.png"
)
t500files = (
    "light_h_bg.png", "light_h_f.png", "light_h_s.png", 
    "light_h_f_bg.png", "light_h_f_p.png", "light_h_f_b.png",
    "light_h_s_bg.png", "light_h_s_p.png", "light_h_s_b.png",
    "light_v_bg.png", "light_v_f.png", "light_v_s.png",
    "light_v_f_bg.png", "light_v_f_p.png", "light_v_f_b.png",
    "light_v_s_bg.png", "light_v_s_p.png", "light_v_s_b.png"
)
t1000files = t500files

def colordark(color):
    if colors.colorDistance(HexColor(color),HexColor("#000000"))<1.25:
        return True
    return False

def r200m(puzzletype,templatedir,canvas,orientation,color,image,title,barcode,width,height):
    if orientation=='horizontal':
        canvas.drawImage(os.path.join(templatedir,t200files[0]),12*mm,32*mm,width-((12+36)*mm),height-((32+10)*mm),mask=[0,0,0,0,0,0])
        canvas.drawImage(image,17*mm,36.5*mm,width-((17+69)*mm),height-((36.5+13.5)*mm),mask=[0,0,0,0,0,0])
    elif orientation=='vertical':
        canvas.drawImage(os.path.join(templatedir,t200files[0]),12*mm,21*mm,width-((12+36)*mm),height-((32+10)*mm),mask=[0,0,0,0,0,0])
        canvas.rotate(90)
        canvas.drawImage(image,25.5*mm,-17*mm-(width-((17+69)*mm)),height-((36.5+13.5)*mm),width-((17+69)*mm),mask=[0,0,0,0,0,0])
        canvas.rotate(-90)
    c = HexColor("#000000")
    if colordark(color):
        c = HexColor("#FFFFFF")
    c.alpha = None
    if orientation=='horizontal':
        canvas.setFillColor(c)
        canvas.setFont(PUZZLEFONTPLAIN,20*mm)
        canvas.drawString(12*mm,12*mm,title)
    elif orientation=='vertical':
        canvas.setFillColor(c)
        canvas.setFont(PUZZLEFONTPLAIN,15*mm)
        canvas.rotate(90)
        canvas.drawString(12*mm,-302*mm,title)
        canvas.rotate(-90)
    c = HexColor("#000000")
    c.alpha = None
    canvas.setFillColor(c)
    canvas.rotate(90)
    canvas.translate(156*mm,-280*mm)
    if orientation=='horizontal':
        canvas.setFont(PUZZLEFONTPLAIN,12*mm)
        canvas.drawString(19*mm,9*mm,puzzletype)
        canvas.setFont(PUZZLEFONTPLAIN,6*mm)
        canvas.drawString(0,0,PUZZLESIZES[puzzletype])
    elif orientation=='vertical':
        canvas.setFont(PUZZLEFONTPLAIN,12*mm)
        canvas.drawString(8*mm,9*mm,puzzletype)
        canvas.setFont(PUZZLEFONTPLAIN,6*mm)
        canvas.drawString(-11*mm,0,PUZZLESIZES[puzzletype])

def r200f(puzzletype,templatedir,canvas,orientation,color,image,title,barcode,width,height):
    if orientation=='horizontal':
        r = 544.0/400.0
        q = 162.0/108.0
        canvas.drawImage(os.path.join(templatedir,t200files[6]),16*mm,1*mm,(height-((1+1)*mm))*r,height-((1+1)*mm),mask=[0,0,0,0,0,0])
        canvas.drawImage(os.path.join(templatedir,t200files[7]),69*mm,18.5*mm,9*mm*q,9*mm,mask=[0,0,0,0,0,0])
        canvas.drawImage(os.path.join(templatedir,t200files[8]),width-(height-((1+1)*mm)),1*mm,height-((1+1)*mm),height-((1+1)*mm),mask=[0,0,0,0,0,0])
        canvas.drawImage(image,(16+1)*mm,(1+1)*mm,((height-((1+1)*mm))*r)-((1+1)*mm),height-((2+2)*mm),mask=[0,0,0,0,0,0])
    elif orientation=='vertical':
        r = 544.0/400.0
        q = 162.0/108.0
        canvas.drawImage(os.path.join(templatedir,t200files[15]),19*mm,1*mm,(height-((1+1)*mm))/r,height-((1+1)*mm),mask=[0,0,0,0,0,0])
        canvas.drawImage(os.path.join(templatedir,t200files[16]),69*mm,18.5*mm,9*mm*q,9*mm,mask=[0,0,0,0,0,0])
        canvas.drawImage(os.path.join(templatedir,t200files[17]),width-(height-((1+1)*mm)),1*mm,height-((1+1)*mm),height-((1+1)*mm),mask=[0,0,0,0,0,0])
        canvas.drawImage(image,(19+1)*mm,(1+1)*mm,((height-((1+1)*mm))/r)-((1+1)*mm),height-((2+2)*mm),mask=[0,0,0,0,0,0])
    c = HexColor("#FFFFFF")
    c.alpha = None
    canvas.setFillColor(c)
    canvas.rect(218*mm,4*mm,40*mm,28*mm,fill=True,stroke=False)
    barcode.drawOn(canvas,219*mm,5*mm)
    c = HexColor("#000000")
    if colordark(color):
        c = HexColor("#FFFFFF")
    c.alpha = None
    canvas.setFillColor(c)
    canvas.setFont(PUZZLEFONTPLAIN,12*mm)
    canvas.drawString(85*mm,18.5*mm,puzzletype)
    canvas.setFont(PUZZLEFONTPLAIN,6*mm)
    canvas.drawString(69*mm,6*mm,PUZZLESIZES[puzzletype])
    canvas.setFont(PUZZLEFONTOBLIQUE,6*mm)
    canvas.drawString(137*mm,9*mm,PUZZLEPRINTERURL)
    canvas.drawString(137*mm,16*mm,PUZZLEPRINTERSLOGAN)

def r200s(puzzletype,templatedir,canvas,orientation,color,image,title,barcode,width,height):
    if orientation=='horizontal':
        r = 544.0/400.0
        q = 162.0/108.0
        canvas.drawImage(os.path.join(templatedir,t200files[6]),15*mm,1*mm,(height-((1+1)*mm))*r,height-((1+1)*mm),mask=[0,0,0,0,0,0])
        canvas.drawImage(os.path.join(templatedir,t200files[7]),69*mm,18.5*mm,9*mm*q,9*mm,mask=[0,0,0,0,0,0])
        canvas.drawImage(os.path.join(templatedir,t200files[8]),width-(height-((1+1)*mm)),1*mm,height-((1+1)*mm),height-((1+1)*mm),mask=[0,0,0,0,0,0])
        canvas.drawImage(image,(15+1)*mm,(1+1)*mm,((height-((1+1)*mm))*r)-((1+1)*mm),height-((2+2)*mm),mask=[0,0,0,0,0,0])
    elif orientation=='vertical':
        r = 544.0/400.0
        q = 162.0/108.0
        canvas.drawImage(os.path.join(templatedir,t200files[15]),18*mm,1*mm,(height-((1+1)*mm))/r,height-((1+1)*mm),mask=[0,0,0,0,0,0])
        canvas.drawImage(os.path.join(templatedir,t200files[16]),69*mm,18.5*mm,9*mm*q,9*mm,mask=[0,0,0,0,0,0])
        canvas.drawImage(os.path.join(templatedir,t200files[17]),width-(height-((1+1)*mm)),1*mm,height-((1+1)*mm),height-((1+1)*mm),mask=[0,0,0,0,0,0])
        canvas.drawImage(image,(18+1)*mm,(1+1)*mm,((height-((1+1)*mm))/r)-((1+1)*mm),height-((2+2)*mm),mask=[0,0,0,0,0,0])
    c = HexColor("#000000")
    if colordark(color):
        c = HexColor("#FFFFFF")
    c.alpha = None
    canvas.setFillColor(c)
    canvas.setFont(PUZZLEFONTPLAIN,12*mm)
    canvas.drawString(85*mm,18.5*mm,puzzletype)
    canvas.setFont(PUZZLEFONTPLAIN,6*mm)
    canvas.drawString(69*mm,6*mm,PUZZLESIZES[puzzletype])

def r1000m(puzzletype,templatedir,canvas,orientation,color,image,title,barcode,width,height):
    canvas.setFillColor(HexColor("#aaaaaa"))
    canvas.rect(0,0,width,height,stroke=0,fill=1)
    canvas.drawImage(os.path.join(templatedir,t1000files[0]),12*mm,32*mm,width-((12+36)*mm),height-((32+10)*mm),mask=[0,0,0,0,0,0])
    canvas.drawImage(image,17*mm,36.5*mm,width-((17+69)*mm),height-((36.5+13.5)*mm),mask=[0,0,0,0,0,0])
    c = HexColor("#000000")
    if colordark(color):
        c = HexColor("#FFFFFF")
    c.alpha = None
    canvas.setFillColor(c)
    canvas.setFont(PUZZLEFONTPLAIN,20*mm)
    canvas.drawString(12*mm,12*mm,title)
    c = HexColor("#000000")
    c.alpha = None
    canvas.setFillColor(c)
    canvas.rotate(90)
    canvas.translate(190*mm,-303*mm)
    canvas.setFont(PUZZLEFONTPLAIN,12*mm)
    canvas.drawString(19*mm,9*mm,puzzletype)
    canvas.setFont(PUZZLEFONTPLAIN,6*mm)
    canvas.drawString(0,0,PUZZLESIZES[puzzletype])

def r1000f(puzzletype,templatedir,canvas,orientation,color,image,title,barcode,width,height):
    canvas.setFillColor(HexColor("#aaaaaa"))
    canvas.rect(0,0,width,height,stroke=0,fill=1)
    canvas.drawImage(os.path.join(templatedir,t1000files[1]),16*mm,6*mm,width-((16+16)*mm),height-((6+6)*mm),mask=[0,0,0,0,0,0])
    canvas.drawImage(image,18*mm,11*mm,51*mm,35*mm,mask=[0,0,0,0,0,0])
    c = HexColor("#FFFFFF")
    c.alpha = None
    canvas.setFillColor(c)
    canvas.rect(238*mm,14*mm,40*mm,28*mm,fill=True,stroke=False)
    barcode.drawOn(canvas,239*mm,15*mm)
    c = HexColor("#000000")
    if colordark(color):
        c = HexColor("#FFFFFF")
    c.alpha = None
    canvas.setFillColor(c)
    canvas.setFont(PUZZLEFONTPLAIN,12*mm)
    canvas.drawString(95*mm,33.5*mm,puzzletype)
    canvas.setFont(PUZZLEFONTPLAIN,6*mm)
    canvas.drawString(79*mm,19*mm,PUZZLESIZES[puzzletype])
    canvas.setFont(PUZZLEFONTOBLIQUE,6*mm)
    canvas.drawString(143*mm,23*mm,PUZZLEPRINTERURL)
    canvas.drawString(143*mm,30*mm,PUZZLEPRINTERSLOGAN)

def r1000s(puzzletype,templatedir,canvas,orientation,color,image,title,barcode,width,height):
    canvas.setFillColor(HexColor("#aaaaaa"))
    canvas.rect(0,0,width,height,stroke=0,fill=1)
    canvas.drawImage(os.path.join(templatedir,t1000files[2]),15*mm,6*mm,width-((15+15)*mm),height-((6+6)*mm),mask=[0,0,0,0,0,0])
    canvas.drawImage(image,17*mm,11*mm,51*mm,35*mm,mask=[0,0,0,0,0,0])
    c = HexColor("#000000")
    if colordark(color):
        c = HexColor("#FFFFFF")
    c.alpha = None
    canvas.setFillColor(c)
    canvas.setFont(PUZZLEFONTPLAIN,12*mm)
    canvas.drawString(95*mm,33.5*mm,puzzletype)
    canvas.setFont(PUZZLEFONTPLAIN,6*mm)
    canvas.drawString(79*mm,19*mm,PUZZLESIZES[puzzletype])

templates = {
    "std_200_light":((None,fillcolor),("m",r200m),("b",r200f),("r",r200s),("t",r200f),("l",r200s)),
    "std_200_dark":((None,fillcolor),("m",r200m),("b",r200f),("r",r200s),("t",r200f),("l",r200s)),
    "std_500_light":((None,fillcolor),("m",r200m),("b",r200f),("r",r200s),("t",r200f),("l",r200s)),
    "std_500_dark":((None,fillcolor),("m",r200m),("b",r200f),("r",r200s),("t",r200f),("l",r200s)),
    "std_600_light":((None,fillcolor),("m",r1000m),("b",r1000f),("r",r1000s),("t",r1000f),("l",r1000s)),
    "std_600_dark":((None,fillcolor),("m",r1000m),("b",r1000f),("r",r1000s),("t",r1000f),("l",r1000s)),
    "std_1000_light":((None,fillcolor),("m",r1000m),("b",r1000f),("r",r1000s),("t",r1000f),("l",r1000s)),
    "std_1000_dark":((None,fillcolor),("m",r1000m),("b",r1000f),("r",r1000s),("t",r1000f),("l",r1000s)),
}

def rendercover(puzzletype,template,orientation,color,canvas,image,title,width,height,barcode,trafos):
    oldStroke = shapes.STATE_DEFAULTS['strokeColor']
    oldFill = shapes.STATE_DEFAULTS['fillColor']
    shapes.STATE_DEFAULTS['strokeColor'] = None
    shapes.STATE_DEFAULTS['fillColor'] = None
    templatedir = os.path.join(BASEDIR,"puzzles","templates",template,puzzletype)
#    pdfmetrics.standardFonts = ()
#    registerfont(os.path.join(templatedir,"font"),"Helvetica.afm","Helvetica.pfb",PUZZLEFONTPLAIN)
#    registerfont(os.path.join(templatedir,"font"),"Helvetica_Oblique.afm","Helvetica.pfb",PUZZLEFONTOBLIQUE)
#    pdfmetrics.findFontAndRegister("Helvetica").face.addObjects(canvas._doc)
#    pdfmetrics.findFontAndRegister("Helvetica-Oblique").face.addObjects(canvas._doc)
    args = [puzzletype,templatedir,canvas,orientation,color,image,title,barcode,0,0]
    if colordark(color):
        template = templates[template+"_"+puzzletype+"_dark"]
    else:
        template = templates[template+"_"+puzzletype+"_light"]
    runtemplate(template,trafos,canvas,args,width,height)
    shapes.STATE_DEFAULTS['strokeColor'] = oldStroke
    shapes.STATE_DEFAULTS['fillColor'] = oldFill

