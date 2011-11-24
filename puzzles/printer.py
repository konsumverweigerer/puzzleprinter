from puzzle-settings import *

import ConfigParser,StringIO
from boto.utils import fetch_file
import md5,os
from reportlab.lib import colors
from reportlab.graphics.shapes import *
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Frame
from reportlab.graphics import renderPDF

if not os.path.exists(PRINTERDIR):
  os.mkdir(PRINTERDIR)

class MyConfigParser(ConfigParser.SafeConfigParser):
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
            fp.write("\r\n")ser):

class Order:
    order_id=""
    puzzle_type="1000"
    puzzle_s3=None
    puzzle_data=None
    state="ODR"
    template="std"
    shipping_name=""
    shipping_street=""
    shipping_number=""
    shipping_zipcode=""
    shipping_city=""
    shipping_country=""
    additionaldata=None

    def generatebarcode(self):
        if len(PRINTERSN)==2:
            return PRINTERSN+str(int(md5.md5(order_id).hexdigest(),16)%10000000000)
        elif len(PRINTERSN)==3:
            return "0"+PRINTERSN+str(int(md5.md5(order_id).hexdigest(),16)%100000000)
        return ""

    def generateboktype(self):
        for t in PUZZLETYPES:
            if t[0]==self.puzzle_type:
                return t[1]
        return ""

    def getimage(self):
        if puzzle_data:
            return puzzle_data
        if puzzle_s3:
            f = fetch_file(puzzle_s3,username=AWSKEYID,password=AWSSECRET)
            return f.read()
        return None

    def createpuzzle(self):
        dimensions = (100,100,100,100)
        for t in PUZZLETYPES:
            if t[0]==self.puzzle_type:
                dimensions = t[2]
        puzzle = ""
        d = Drawing(dimensions[0]*mm,dimensions[1]*mm)
        renderPDF
        return (puzzle,"")

    def write(self):
        if "ODR"!=state:
            return
        basename = self.generatebarcode()
        filename = basename+"."+self.state
        tmpname = basename+".TMP"
        data = MyConfigParser()
        puzzlepdf = os.path.join(basename,"I"+basename+".pdf")
        coverpdf = os.path.join(basename,"U"+basename+".pdf")
        dirname = os.path(PRINTERDIR,basename)
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        (puzzle,cover) = self.createpuzzle(basename)
        open(puzzlepdf,"w").write(puzzle)
        open(coverpdf,"w").write(cover)
        data.add_section("Order")
        data.set("Order","CustomersShortName",PRINTERSN)
        data.set("Order","CustomersOrderNumber",self.order_id)
        data.add_section("Book")
        data.set("Book","BarcodeNumber",basename)
        data.set("Book","BookType",self.generateboktype())
        data.set("Book","PageCount",1)
        data.set("Book","BookCount",1)
        data.set("Book","PdfNameBook",puzzlepdf.replace("/","\\"))
        data.set("Book","BookMd5",md5.md5(puzzle).hexdigest())
        data.set("Book","PdfNameCover",coverpdf.replace("/","\\"))
        data.set("Book","CoverMd5",md5.md5(cover).hexdigest())

        data.set("Book","DeliveryAddressCount",1)
        data.set("Book","Delivery0BookCount",0)
        data.set("Book","Delivery0ParcelService",0)
        data.set("Book","Delivery0Name",self.shipping_name)
        data.set("Book","Delivery0Street",self.shipping_street)
        data.set("Book","Delivery0HouseNumber",self.shipping_number)
        data.set("Book","Delivery0ZipCode",slef.shipping_zipcode)
        data.set("Book","Delivery0City",self.shipping_city)
        data.set("Book","Delivery0Country",self.shipping_country)

        if self.additionaldata:
            additionalpdf = os.path.join(basename,"additional.pdf")
            open(additionalpdf,'w').write(self.additionaldata)
            data.set("Book","Delivery0AdditionalDocuments",self.additionalpdf.replace("/","\\"))
        data.write(open(os.path.join(PRINTERDIR,tmpname),'w'))
        os.rename(os.path.join(PRINTERDIR,tmpname),os.path.join(PRINTERDIR,filename))

