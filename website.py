from xml.sax.handler import ContentHandler
from xml.sax import parse
import os

class Handler(ContentHandler):
    def callback(self, prefix, name, attrs = None):
        method = getattr(self, prefix + name, None)
        if callable(method): 
            args = ()
        else:
            method = getattr(self, prefix + "default", None)
            args = name, 
        if prefix == "start_": args += attrs,
        if callable(method): method(*args)
    def startElement(self, name, attrs):
        self.callback('start_', name, attrs)
    def endElement(self, name):
        self.callback('end_', name, None)
        
class XMLHandler(Handler):
    passthrough = False
    def __init__(self, directory):
        self.directory = [directory]
        self.ensure_directory()
    def ensure_directory(self):
        path = os.path.join(*self.directory)
        if not os.path.isdir(path): os.makedirs(path)
    def start_page(self, attrs):
        self.passthrough = True
        filename = os.path.join(*self.directory + [attrs['name'] + '.html'])
        self.out = open(filename, 'w')
        self.out.write("<html>\n<head><title>%s</title></head>" % attrs['title'])
        self.out.write("<body>\n")
    def end_page(self):
        self.passthrough = False
        self.out.write("\n</body>\n</html>\n")
        self.out.close()
    def start_directory(self, attrs):
        self.directory.append(attrs['name'])
        self.ensure_directory()
    def end_directory(self):
        self.directory.pop()
    def characters(self, string):
        if self.passthrough and string.strip(): 
            self.out.write("%s\n" % string)
    def start_default(self, name, attrs):
        if self.passthrough:
            self.out.write("<%s" % name)
            for key, val in attrs.items():
                self.out.write(" %s = %s" % (key, val))
            self.out.write(">\n")
    def end_default(self, name):
        if self.passthrough:
            self.out.write("</%s>\n" % name)
parse("website.xml", XMLHandler("test"))
