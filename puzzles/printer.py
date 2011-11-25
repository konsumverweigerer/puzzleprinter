from puzzle-settings import *

import ConfigParser,StringIO
from boto.utils import fetch_file
import md5,os
from reportlab.lib import colors
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Frame
from PIL import Image

if not os.path.exists(PRINTERDIR):
  os.mkdir(PRINTERDIR)

def rendercover(template,canvas,image,title,width,height):
    pass

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
    order_id = ""
    puzzle_type = "1000"
    puzzle_s3 = None
    puzzle_data = None
    puzzle_title = "Mein Puzzle"
    state = "ODR"
    template = "std"
    shipping_name = ""
    shipping_street = ""
    shipping_number = ""
    shipping_zipcode = ""
    shipping_city = ""
    shipping_country = ""
    additionaldata = None
    printing_status = None

    def generatebarcode(self):
        if len(PRINTERKN)==2:
            return PRINTERKN+str(int(md5.md5(order_id).hexdigest(),16)%10000000000)
        elif len(PRINTERKN)==3:
            return "0"+PRINTERKN+str(int(md5.md5(order_id).hexdigest(),16)%100000000)
        return ""

    def generateboktype(self):
        for t in PUZZLETYPES:
            if t[0]==self.puzzle_type:
                return t[1]
        return ""

    def getimage(self):
        if self.puzzle_data:
            return self.puzzle_data
        if self.puzzle_s3:
            f = fetch_file(puzzle_s3,username=AWSKEYID,password=AWSSECRET)
            self.puzzle_data = f.read()
            return self.puzzle_data
        return None

    def createpuzzle(self):
        dimensions = (100,100,100,100)
        for t in PUZZLETYPES:
            if t[0]==self.puzzle_type:
                dimensions = t[2]
        puzzle = ""
        puzzleio = StringIO.StringIO()
        coverio = StringIO.StringIO()
        image = Image.open(self.getimage())
        c = Canvas(puzzleio,pagesize=(dimensions[0]*mm,dimensions[1]*mm))
        c.drawInlineImage(image,0,0,width=dimensions[0]*mm,height=dimensions[1]*mm)
        c.showPage()
        c.save()
        c = Canvas(coverio,pagesize=(dimensions[2]*mm,dimensions[3]*mm))
        rendercover(self.template,c,image,self.puzzle_title,dimensions[2],dimensions[3])
        c.showPage()
        c.save()
        return (puzzleio.buf,coverio.buf)

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

    def read(self,filename):
        data = MyConfigParser()
        pass

    @static
    def fromFile(filename):
        o = Order()
        o.read(filename)
        return o
