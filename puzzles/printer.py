from puzzlesettings import *
# -*- coding: utf-8 -*-

from puzzles import templates

import ConfigParser,StringIO,tempfile
import md5,os,ftplib,sys,logging,codecs,pgmagick,boto

from boto.utils import fetch_file

from PIL import Image

from reportlab import rl_config
rl_config.defaultGraphicsFontName = "Nimbus"
rl_config.canvas_basefontname = rl_config.defaultGraphicsFontName
rl_config.T1SearchPath.insert(0,os.path.join(BASEDIR,"puzzles","templates","font"))
from reportlab.pdfbase import pdfmetrics,ttfonts
#pdfmetrics.standardFonts = ()
#pdfmetrics.findFontAndRegister("NimbusSanL-Regu")
#pdfmetrics.findFontAndRegister("NimbusSanL-ReguItal")
#pdfmetrics.findFontAndRegister("LinLibertine")
#pdfmetrics.findFontAndRegister("LinLibertineI")
#pdfmetrics.findFontAndRegister("GFSBodoni-Regular")
#pdfmetrics.findFontAndRegister("GFSBodoni-Italic")
#pdfmetrics.findFontAndRegister("Helvetica")
#pdfmetrics.findFontAndRegister("Helvetica-Oblique")
#pdfmetrics.findFontAndRegister("LibrisADFStd-Regular")
#pdfmetrics.findFontAndRegister("LibrisADFStd-Italic")
pdfmetrics.registerFont(ttfonts.TTFont("Verdana",os.path.join("puzzles","templates","font","verdana.ttf")))
pdfmetrics.registerFont(ttfonts.TTFont("Verdana-Italic",os.path.join("puzzles","templates","font","verdanai.ttf")))
pdfmetrics.registerFont(ttfonts.TTFont("Nimbus",os.path.join("puzzles","templates","font","nimbus.ttf")))
pdfmetrics.registerFont(ttfonts.TTFont("Nimbus-Italic",os.path.join("puzzles","templates","font","nimbusi.ttf")))
pdfmetrics.registerFont(ttfonts.TTFont("LiberationSans-Regular",os.path.join("puzzles","templates","font","LiberationSans-Regular.ttf")))
pdfmetrics.registerFont(ttfonts.TTFont("LiberationSans-Italic",os.path.join("puzzles","templates","font","LiberationSans-Italic.ttf")))
pdfmetrics.registerFont(ttfonts.TTFont("Helvetica",os.path.join("puzzles","templates","font","Helvetica.ttf")))
from reportlab.lib import colors
from reportlab.lib.units import inch,cm,mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics import barcode
from reportlab.lib.colors import Color,HexColor

logger = logging.getLogger(__name__)

AVAILSTATUS = ("OrderAcquired","PdfTransferred","InProduction","CheckedOut","Delivered")
ACCEPTEDSTATUS = ("InProduction","CheckedOut","Delivered")
FINISHEDSTATUS = ("CheckedOut","Delivered")

POSTPROCESS = { 
    "all":"gs",
    "additional":"gs14",
}

class MyConfigParser(ConfigParser.SafeConfigParser):
    def optionxform(self, optionstr):
        return optionstr

    def _read(self,fp,filename):
        t = fp.read()
        if t.startswith(codecs.BOM_UTF8):
            t = t[3:]
        elif t[0]==unicode(codecs.BOM_UTF8,"utf8"):
            t = t[1:]
        ConfigParser.SafeConfigParser._read(self,StringIO.StringIO(t),filename)

    def write(self,fp):
        if self._defaults:
            fp.write("[%s]\r\n" % DEFAULTSECT)
            for (key, value) in self._defaults.items():
                try:
                    fp.write(("%s=%s\r\n" % (key, str(value).replace('\n', '\r\n\t'))).encode("utf8"))
                except:
                    print "could not write "+str(value)
            fp.write("\r\n")
        for section in self._sections:
            fp.write("[%s]\r\n" % section)
            for (key, value) in self._sections[section].items():
                if key != "__name__":
                    try:
                        fp.write(("%s=%s\r\n" %
                                 (key, unicode(value).replace('\n', '\r\n\t'))).encode("utf8"))
                    except:
                        print "could not write "+str(value)
            fp.write("\r\n")

def send_file(uri,content,username=None,password=None):
    bucket_name, key_name = uri[len('s3://'):].split('/', 1)
    c = boto.connect_s3(aws_access_key_id=username, aws_secret_access_key=password)
    bucket = c.get_bucket(bucket_name)
    key = bucket.get_key(key_name)
    if not key:
        key = bucket.new_key(key_name)
    key.set_contents_from_string(content)

def makebarcode(order_id,puzzle_id,reprint=""):
    if len(PRINTERKN)==2:
        t = str(int(md5.md5(str(order_id)+str(puzzle_id)+reprint).hexdigest(),16)%1000000000)
        while len(t)<9:
            t = "0"+t
        return PRINTERKN+t+"0"
    elif len(PRINTERKN)==3:
        t = str(int(md5.md5(str(order_id)+str(puzzle_id)+reprint).hexdigest(),16)%100000000)
        while len(t)<8:
            t = "0"+t
        return PRINTERKN+t+"0"
    return ""

def cleanuppdf(data,v="all"):
    pp = ""
    if "all" in POSTPROCESS.keys():
        pp = POSTPROCESS["all"]
    if v in POSTPROCESS.keys():
        pp = POSTPROCESS[v]
    if pp=="ps2pdf":
        (pdffd,pdf) = tempfile.mkstemp(suffix=".pdf")
        (psfd,ps) = tempfile.mkstemp(suffix=".ps")
        pdffd = os.fdopen(pdffd,'w')
        pdffd.write(data)
        pdffd.close()
        os.system("pdf2ps %s %s"%(pdf,ps))
        os.system("ps2pdf13 %s %s"%(ps,pdf))
        data = open(pdf).read()
        os.remove(ps)
        os.remove(pdf)
    elif pp=="pstopdf":
        (pdffd,pdf) = tempfile.mkstemp(suffix=".pdf")
        (psfd,ps) = tempfile.mkstemp(suffix=".ps")
        pdffd = os.fdopen(pdffd,'w')
        pdffd.write(data)
        pdffd.close()
        os.system("pdftops %s %s"%(pdf,ps))
        os.system("ps2pdf13 %s %s"%(ps,pdf))
        data = open(pdf).read()
        os.remove(ps)
        os.remove(pdf)
    elif pp=="gs":
        (pdffd,pdf) = tempfile.mkstemp(suffix=".pdf")
        (psfd,ps) = tempfile.mkstemp(suffix=".pdf")
        psfd = os.fdopen(psfd,'w')
        psfd.write(data)
        psfd.close()
        os.system("gs -q -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress -dEmbedAllFonts=true -dSubsetFonts=true -dCompatibilityLevel=1.3 -r1200 -sOutputFile=%s %s"%(pdf,ps))
        data = open(pdf).read()
        os.remove(ps)
        os.remove(pdf)
    elif pp=="gs14":
        (pdffd,pdf) = tempfile.mkstemp(suffix=".pdf")
        (psfd,ps) = tempfile.mkstemp(suffix=".pdf")
        psfd = os.fdopen(psfd,'w')
        psfd.write(data)
        psfd.close()
        os.system("gs -q -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress -dEmbedAllFonts=true -dSubsetFonts=true -dCompatibilityLevel=1.4 -r1200 -sOutputFile=%s %s"%(pdf,ps))
        data = open(pdf).read()
        os.remove(ps)
        os.remove(pdf)
    return data

class Order:
    order_id = ""
    reprint = ""
    puzzle_id = ""
    puzzle_type = "0"
    puzzle_s3 = None
    puzzle_data = None
    puzzle_title = ""
    state = "ODR"
    template = "std"
    orientation = "horizontal"
    color = "#665533"
    count = 1
    shipping_name = ""
    shipping_street = ""
    shipping_number = ""
    shipping_zipcode = ""
    shipping_city = ""
    shipping_country = ""
    shipping_provider = "DHL"
    additionaldata = None
    printing_status = None
    shipping_status = None
    preview = None
    barcode = None
    debug = False

    def finished(self):
        if self.printing_status:
            for t in FINISHEDSTATUS:
                if self.printing_status.startswith(t):
                    return True
        return False

    def valid(self):
        if self.printing_status:
            for t in ACCEPTEDSTATUS:
                if self.printing_status.startswith(t):
                    return True
        return False


    def generatebarcode(self):
        self.barcode = makebarcode(self.order_id,self.puzzle_id,self.reprint)
        return self.barcode

    def generatebooktype(self):
        for t in PUZZLETYPES:
            if t[0]==self.puzzle_type:
                return t[1]
        return ""

    def getimage(self):
        if self.puzzle_data:
            return self.puzzle_data
        if self.puzzle_s3:
            f = fetch_file(self.puzzle_s3,username=AWSKEYID,password=AWSSECRET)
            self.puzzle_data = f.read()
            return self.puzzle_data
        return None

    def putfile(self,path,content):
        if path:
            s3 = "s3://"+AWSBUCKET+AWSARCHIVE+path
            send_file(s3,content,username=AWSKEYID,password=AWSSECRET)

    def createpreview(self,puzzle,cover):
        d = 72
        while d>4:
            try:
                blob = pgmagick.Blob(cover)
                img = pgmagick.Image()
                img.density(str(d))
                img.read(blob,pgmagick.Geometry(640,480))
                img.scale('640x480')
                (fd,n) = tempfile.mkstemp(suffix=".jpg")
                img.write(n)
                t = open(n).read()
                os.remove(n)
                return t
            except:
                d = d/2
                print "retrying preview generation with res="+str(d)
        return None

    def createpuzzle(self,bc):
        dimensions = (100,100,100,100)
        trafos = {}
        for t in PUZZLETYPES:
            if t[0]==self.puzzle_type:
                dimensions = t[2]
                trafos = t[3]
        puzzle = ""
        puzzleio = StringIO.StringIO()
        coverio = StringIO.StringIO()
        (imfd,im) = tempfile.mkstemp(suffix=".jpg")
        z = os.fdopen(imfd,'w')
        z.write(self.getimage())
        z.close()
#        image = Image.open(StringIO.StringIO(self.getimage()))
#        imager = ImageReader(image)
        image = im
        imager = im
        c = Canvas(puzzleio,pagesize=(dimensions[0]*mm,dimensions[1]*mm))
        if self.orientation=="horizontal":
            c.drawInlineImage(image,0,0,width=dimensions[0]*mm,height=dimensions[1]*mm)
        else:
            c.rotate(90)
            c.translate(0,-dimensions[0]*mm)
            c.drawInlineImage(image,0,0,width=dimensions[1]*mm,height=dimensions[0]*mm)
        c.showPage()
        c.save()
#        pdfmetrics.standardFonts = ()
        c = Canvas(coverio,pagesize=(dimensions[2]*mm,dimensions[3]*mm))
        col = HexColor("#000000")
        col.alpha = None
        bcimg = barcode.createBarcodeDrawing("EAN13",value=bc,fontName=rl_config.defaultGraphicsFontName,textColor=col,barFillColor=col)
        templates.rendercover(self.puzzle_type,self.template,self.orientation,self.color,c,imager,self.puzzle_title,dimensions[2],dimensions[3],bcimg,trafos,self.debug)
        c.showPage()
        c.save()
        os.remove(im)
        return (cleanuppdf(puzzleio.getvalue(),"puzzle"),cleanuppdf(coverio.getvalue(),"cover"))

    def makepreview(self):
        if "ODR"!=self.state:
            return
        basename = self.generatebarcode()
        (puzzle,cover) = self.createpuzzle(basename)
        self.preview = self.createpreview(puzzle,cover)

    def write(self,directory=None):
        if "ODR"!=self.state:
            return
        try:
            basename = self.generatebarcode()
            filename = basename+"."+self.state
            tmpname = basename+".TMP"
            data = MyConfigParser()
            puzzlepdf = "I_"+basename+".PDF"
            coverpdf = "U_"+basename+".PDF"
            (puzzle,cover) = self.createpuzzle(basename)
            self.preview = self.createpreview(puzzle,cover)

            data.add_section("Order")
            data.set("Order","CustomersShortName",PRINTERSN)
            data.set("Order","CustomersOrderNumber",self.order_id)

            data.add_section("Book")
            data.set("Book","BarcodeNumber",basename)
            data.set("Book","PdfNameBook",basename+"\\"+puzzlepdf)
            data.set("Book","PdfNameCover",basename+"\\"+coverpdf)
            data.set("Book","BookMd5",md5.md5(puzzle).hexdigest())
            data.set("Book","CoverMd5",md5.md5(cover).hexdigest())
            data.set("Book","BookType",self.generatebooktype())
            data.set("Book","PageCount","1")
            data.set("Book","BookCount",str(self.count))

            data.set("Book","DeliveryAddressCount","1")
            data.set("Book","Delivery0BookCount",str(self.count))
            data.set("Book","Delivery0Name",self.shipping_name)
            data.set("Book","Delivery0Street",self.shipping_street)
            data.set("Book","Delivery0HouseNumber",self.shipping_number)
            data.set("Book","Delivery0ZipCode",self.shipping_zipcode)
            data.set("Book","Delivery0City",self.shipping_city)
            data.set("Book","Delivery0Country",self.shipping_country)
            data.set("Book","Delivery0ParcelService",self.shipping_provider)
            if self.additionaldata:
                additionalpdf = "ADDITIONAL.PDF"
                adddata = cleanuppdf(self.additionaldata,"additional")
                data.set("Book","Delivery0AdditionalDocuments",basename+"\\"+additionalpdf)
                data.set("Book","Delivery0AdditionalDocumentsBackGroundIdentifier","0")
        except Exception,e:
            logging.warn("could not render print "+self.order_id+" "+str(e))
            return

        ftp = ftplib.FTP(PRINTERSRV,PRINTERFTPUSER,PRINTERFTPPWD)
        if not ftp:
            return
        try:
            if directory:
                try:
                    os.mkdir(os.path.join(directory,basename))
                except:
                    pass
            else:
                try:
                    ftp.mkd(basename)
                except:
                    pass
            if directory:
                open(os.path.join(directory,basename,puzzlepdf),'w').write(puzzle)
                open(os.path.join(directory,basename,coverpdf),'w').write(cover)
            else:
                ftp.cwd("/")
                ftp.cwd(basename)
                ftp.storbinary("STOR "+puzzlepdf,StringIO.StringIO(puzzle))
                ftp.storbinary("STOR "+coverpdf,StringIO.StringIO(cover))
                self.putfile(basename+"/"+puzzlepdf,puzzle)
                self.putfile(basename+"/"+coverpdf,cover)

            if self.additionaldata:
                if directory:
                    open(os.path.join(directory,basename,additionalpdf),'w').write(adddata)
                else:
                    ftp.storbinary("STOR "+additionalpdf,StringIO.StringIO(adddata))
                    self.putfile(basename+"/"+additionalpdf,adddata)
            dataio = StringIO.StringIO()
            data.write(dataio)
            if directory:
                open(os.path.join(directory,tmpname),'w').write(dataio.getvalue())
                os.rename(os.path.join(directory,tmpname),os.path.join(directory,filename))
            else:
                ftp.cwd("/")
                ftp.storbinary("STOR "+tmpname,StringIO.StringIO(dataio.getvalue()))
                ftp.rename(tmpname,filename)
                self.putfile(filename,dataio.getvalue())
        except Exception,e:
            logging.warn("could not print "+self.order_id+" "+str(e))
        finally:
            if not directory:
                ftp.quit()

    def read(self,fn,fp,statusfp=[]):
        data = MyConfigParser()
        self.state = fn[-3:]
        if fp:
            data.readfp(fp)
            self.order_id = data.get("Order","CustomersOrderNumber")
            self.shipping_name = data.get("Book","Delivery0Name")
            self.shipping_street = data.get("Book","Delivery0Street")
            self.shipping_number = data.get("Book","Delivery0HouseNumber")
            self.shipping_zipcode = data.get("Book","Delivery0ZipCode")
            self.shipping_city = data.get("Book","Delivery0City")
            self.shipping_country = data.get("Book","Delivery0Country")
            try:
                self.printing_status = data.get("Faults","0Text")
            except:
                pass
        else:
            self.state = "ACC"
        for sfp in statusfp:
            status = MyConfigParser()
            status.readfp(StringIO.StringIO(sfp))
            if not self.printing_status:
                try:
                    self.printing_status = status.get("BookStates",fn[:-4])
                except:
                    pass
            if not self.shipping_status:
                try:
                    self.shipping_status = status.get("ShippingInfo",fn[:-4]+"_0")
                except:
                    pass
            if self.printing_status and self.shipping_status:
                break

    @staticmethod
    def fromFile(fn,data,statusdata):
        o = Order()
        if data:
            o.read(fn,StringIO.StringIO(data),statusdata)
        else:
            o.read(fn,None,statusdata)
        o.barcode = fn[0:-4]
        return o

def readorders(ext=['FLT','ACC'],barcodes=[]):
    ftp = ftplib.FTP(PRINTERSRV,PRINTERFTPUSER,PRINTERFTPPWD)
    orders = []
    if not ftp:
        return
    try:
        files = ftp.nlst()
        statuslist = [x for x in files if x.endswith(".STA")]
        statuslist.sort(reverse=True)
        status = []
        if len(statuslist)>30:
            statuslist = statuslist[0:30]
        for fn in statuslist:
            statusio = StringIO.StringIO()
            ftp.retrbinary("RETR "+fn,lambda x:statusio.write(x))
            t = statusio.getvalue()
            s = MyConfigParser()
            s.readfp(StringIO.StringIO(t))
            try:
                for v in s.options("BookStates"):
                    if v not in barcodes:
                        barcodes.append(v)
            except:
                pass
            status.append(t)
        for fn in [x for x in files if x[-3:] in ext]:
            v = StringIO.StringIO()
            logging.info("reading "+fn)
            ftp.retrbinary("RETR "+fn,lambda x:v.write(x))
            o = Order.fromFile(fn,v.getvalue(),status)
            if o.barcode in barcodes:
                barcodes.remove(o.barcode)
            orders.append(o)
        for fn in ["%s.ACC"%(x) for x in barcodes]:
            orders.append(Order.fromFile(fn,None,status))
    finally:
        ftp.quit()
    return orders

def putorder(orderid,puzzleid,s3,template="std",orientation="horizontal",color="#333333",address={},directory=None):
    order = Order()
    order.order_id = orderid
    order.puzzle_id = puzzleid
    order.puzzle_s3 = s3
    order.template = template
    order.color = color
    order.shipping_name = address["name"]
    order.shipping_street = address["street"]
    order.shipping_number = address["number"]
    order.shipping_zipcode = address["zip"]
    order.shipping_city = address["city"]
    order.shipping_country = address["country"]
    order.write(directory=directory)

def demo(d,s3,title,color=None,orientation=None,puzzle_type=None,orderid="2153432",puzzleid="837642",debug=False):
    order = Order()
    order.puzzle_s3 = s3
    order.puzzle_title = title
    order.puzzle_id = puzzleid
    order.order_id = orderid
    order.shipping_name = "Karl Puzzleprinter"
    order.shipping_street = "Äußere Musterstraße"
    order.shipping_number = "3e"
    order.shipping_zipcode = "93047"
    order.shipping_city = "Bad Musterstadt"
    order.shipping_country = "Deutschland"
    order.shipping_provider = "DHL"
    order.debug = debug
    if color:
        order.color = color
    if orientation:
        order.orientation = orientation
    if puzzle_type:
        order.puzzle_type = puzzle_type
    order.write(d)
    return order.generatebarcode()

