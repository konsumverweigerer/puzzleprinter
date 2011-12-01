from puzzlesettings import *

import ConfigParser,StringIO
from puzzles import templates
from boto.utils import fetch_file
import md5,os,ftplib
from reportlab import rl_config
rl_config.defaultGraphicsFontName = "NimbusSanL-Regu"
rl_config.canvas_basefontname = rl_config.defaultGraphicsFontName
rl_config.T1SearchPath.insert(0,os.path.join(BASEDIR,"puzzles","templates","font"))
from reportlab.pdfbase import pdfmetrics
pdfmetrics.standardFonts=()
pdfmetrics.findFontAndRegister("NimbusSanL-Regu")
pdfmetrics.findFontAndRegister("NimbusSanL-ReguItal")
pdfmetrics.findFontAndRegister("Helvetica")
pdfmetrics.findFontAndRegister("Helvetica-Oblique")
from reportlab.lib import colors
from reportlab.lib.units import inch,cm,mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph,Frame
from reportlab.lib.utils import ImageReader
from reportlab.graphics import barcode
from PIL import Image

class MyConfigParser(ConfigParser.SafeConfigParser):
    def optionxform(self, optionstr):
        return optionstr
           
    def write(self, fp):
        if self._defaults:
            fp.write("[%s]\r\n" % DEFAULTSECT)
            for (key, value) in self._defaults.items():
                fp.write("%s = %s\r\n" % (key, str(value).replace('\n', '\r\n\t')))
            fp.write("\r\n")
        for section in self._sections:
            fp.write("[%s]\r\n" % section)
            for (key, value) in self._sections[section].items():
                if key != "__name__":
                    fp.write("%s = %s\r\n" %
                             (key, str(value).replace('\n', '\r\n\t')))
            fp.write("\r\n")

class Order:
    order_id = ""
    puzzle_id = ""
    puzzle_type = "1000"
    puzzle_s3 = None
    puzzle_data = None
    puzzle_title = "Mein Puzzle"
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

    def generatebarcode(self):
        if len(PRINTERKN)==2:
            return PRINTERKN+str(int(md5.md5(str(self.order_id)+str(self.puzzle_id)).hexdigest(),16)%10000000000)
        elif len(PRINTERKN)==3:
            return "0"+PRINTERKN+str(int(md5.md5(str(self.order_id)+str(self.puzzle_id)).hexdigest(),16)%100000000)
        return ""

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

    def write(self,directory=None):
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
                if not os.path.exists(dirname):
                    ftp.mkd(basename)
            (puzzle,cover) = self.createpuzzle(basename)

            if directory:
                open(os.path.join(directory,basename,puzzlepdf),'w').write(puzzle)
                open(os.path.join(directory,basename,coverpdf),'w').write(cover)
            else:
                ftp.cwd("/")
                ftp.cwd(basename)
                ftp.storbinary("STOR "+puzzlepdf,StringIO.StringIO(puzzle))
                ftp.storbinary("STOR "+coverpdf,StringIO.StringIO(cover))

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
                additionalpdf = "additional.pdf"
                if directory:
                    open(os.path.join(directory,basename,additionalpdf),'w').write(additionaldata)
                else:
                    ftp.storbinary("STOR "+additionalpdf,StringIO.StringIO(additionaldata))
                data.set("Book","Delivery0AdditionalDocuments",basename+"\\"+self.additionalpdf)
            dataio = StringIO.StringIO()
            data.write(dataio)
            if directory:
                open(os.path.join(directory,tmpname),'w').write(dataio.getvalue())
                os.rename(os.path.join(directory,tmpname),os.path.join(directory,filename))
            else:
                ftp.cwd("/")
                ftp.storbinary("STOR "+tmpname,StringIO.StringIO(dataio.getvalue()))
#                ftp.rename(tmpname,filename)
        finally:
            if not directory:
                ftp.quit()

    def read(self,fn,fp,statusfp=[]):
        data = MyConfigParser()
        data.readfp(fp)
        self.state = fn[-3:]
        self.order_id = data.get("Order","CustomersOrderNumber")
        self.shipping_name = data.get("Book","Delivery0Name")
        self.shipping_street = data.get("Book","Delivery0Street")
        self.shipping_number = data.get("Book","Delivery0HouseNumber")
        self.shipping_zipcode = data.get("Book","Delivery0ZipCode")
        self.shipping_city = data.get("Book","Delivery0City")
        self.shipping_country = data.get("Book","Delivery0Country")
        for sfp in statusfp:
            status = MyConfigParser()
            status.readfp(StringIO.StringIO(sfp))
            self.shipping_status = status.get("BookStates",fn[:-4])
            self.printing_status = status.get("ShippingInfo",fn[:-4]+"_0")
            if (not self.printing_status) and (not self.shipping_status):
                break

    @staticmethod
    def fromFile(fn,data,statusdata):
        o = Order()
        o.read(StringIO.StringIO(data),StringIO.StringIO(statusdata))
        return o

def readorders(status=['ODR','FLT','WRK','ACC']):
    ftp = ftplib.FTP(PRINTERSRV,PRINTERFTPUSER,PRINTERFTPPWD)
    orders = []
    if not ftp:
        return
    try:
        files = ftp.nlst()
        statuslist = [x for x in files if x.endsWith(".STA")]
        statuslist.sort(reverse=True)
        statusio = StringIO.StringIO()
        status = []
        for fn in statuslist:
            ftp.retrbinary("RETR "+fn,lambda x:statusio.write(x))
            status.append(statusio.getvalue())
        for fn in [x for x in files if x[-3:] in status]:
            v = StringIO.StringIO()
            ftp.retrbinary("RETR "+fn,lambda x:v.write(x))
            orders.append(Order.fromFile(fn,v.getvalue(),status))
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

def demo(d,s3,title,color=None,orientation=None,puzzle_type=None):
    order = Order()
    order.puzzle_s3 = s3
    order.puzzle_title = title
    order.puzzle_id = "2153432"
    order.order_id = "837642"
    if color:
        order.color = color
    if orientation:
        order.orientation = orientation
    if puzzle_type:
        order.puzzle_type = puzzle_type
    return order.write(d)

