from puzzlesettings import *
# -*- coding: utf-8 -*-

from puzzles import templates

import ConfigParser,StringIO,tempfile
import md5,os,ftplib,sys,logging,codecs,pgmagick,boto

from boto.utils import fetch_file

from PIL import Image

from reportlab import rl_config
rl_config.defaultGraphicsFontName = "NimbusSanL-Regu"
rl_config.canvas_basefontname = rl_config.defaultGraphicsFontName
rl_config.T1SearchPath.insert(0,os.path.join(BASEDIR,"puzzles","templates","font"))
from reportlab.pdfbase import pdfmetrics
#pdfmetrics.standardFonts = ()
pdfmetrics.findFontAndRegister("NimbusSanL-Regu")
pdfmetrics.findFontAndRegister("NimbusSanL-ReguItal")
#pdfmetrics.findFontAndRegister("Helvetica")
#pdfmetrics.findFontAndRegister("Helvetica-Oblique")
from reportlab.lib import colors
from reportlab.lib.units import inch,cm,mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics import barcode

logger = logging.getLogger(__name__)

AVAILSTATUS = ("OrderAcquired","PdfTransferred","InProduction","CheckedOut","Delivered")
ACCEPTEDSTATUS = ("InProduction","CheckedOut","Delivered")
FINISHEDSTATUS = ("CheckedOut","Delivered")

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
                fp.write(("%s=%s\r\n" % (key, str(value).replace('\n', '\r\n\t'))).encode("utf8"))
            fp.write("\r\n")
        for section in self._sections:
            fp.write("[%s]\r\n" % section)
            for (key, value) in self._sections[section].items():
                if key != "__name__":
                    fp.write(("%s=%s\r\n" %
                             (key, unicode(value).replace('\n', '\r\n\t'))).encode("utf8"))
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
        image = Image.open(StringIO.StringIO(self.getimage()))
        imager = ImageReader(image)
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
        bcimg = barcode.createBarcodeDrawing("EAN13",value=bc,fontName="NimbusSanL-Regu")
        templates.rendercover(self.puzzle_type,self.template,self.orientation,self.color,c,imager,self.puzzle_title,dimensions[2],dimensions[3],bcimg,trafos)
        c.showPage()
        c.save()
        return (puzzleio.getvalue(),coverio.getvalue())

    def makepreview(self):
        if "ODR"!=self.state:
            return
        basename = self.generatebarcode()
        (puzzle,cover) = self.createpuzzle(basename)
        self.preview = self.createpreview(puzzle,cover)

    def write(self,directory="/tmp/"):
        if "ODR"!=self.state:
            return
        ftp = ftplib.FTP(PRINTERSRV,PRINTERFTPUSER,PRINTERFTPPWD)
        if not ftp:
            return
        try:
            basename = self.generatebarcode()
            filename = basename+"."+self.state
            tmpname = basename+".TMP"
            data = MyConfigParser()
            puzzlepdf = "I_"+basename+".PDF"
            coverpdf = "U_"+basename+".PDF"
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
            (puzzle,cover) = self.createpuzzle(basename)
            self.preview = self.createpreview(puzzle,cover)

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
            data.set("Book","BookCount","1")

            data.set("Book","DeliveryAddressCount","1")
            data.set("Book","Delivery0BookCount","1")
            data.set("Book","Delivery0Name",self.shipping_name)
            data.set("Book","Delivery0Street",self.shipping_street)
            data.set("Book","Delivery0HouseNumber",self.shipping_number)
            data.set("Book","Delivery0ZipCode",self.shipping_zipcode)
            data.set("Book","Delivery0City",self.shipping_city)
            data.set("Book","Delivery0Country",self.shipping_country)
            data.set("Book","Delivery0ParcelService",self.shipping_provider)

            if self.additionaldata:
                additionalpdf = "ADDITIONAL.PDF"
                if directory:
                    open(os.path.join(directory,basename,additionalpdf),'w').write(self.additionaldata)
                else:
                    ftp.storbinary("STOR "+additionalpdf,StringIO.StringIO(self.additionaldata))
                    self.putfile(basename+"/"+additionalpdf,self.additionaldata)
                data.set("Book","Delivery0AdditionalDocuments",basename+"\\"+additionalpdf)
                data.set("Book","Delivery0AdditionalDocumentsBackGroundIdentifier","0")
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

def demo(d,s3,title,color=None,orientation=None,puzzle_type=None,orderid="2153432",puzzleid="837642"):
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
    if color:
        order.color = color
    if orientation:
        order.orientation = orientation
    if puzzle_type:
        order.puzzle_type = puzzle_type
    order.write(d)
    return order.generatebarcode()

