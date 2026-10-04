import sys, os, re, shutil
import helper
from System.Xml.Xsl import XslCompiledTransform

scriptpath = os.path.abspath(os.path.dirname(sys.argv[0]))
xslfile=os.path.join(scriptpath, "plcopenxml.xslt")

class ER(ExportReporter):
    def error(self, object, message):   
        system.write_message(Severity.Error, "Error exporting %s: %s" % (object, message))
    def warning(self, object, message):   
        system.write_message(Severity.Warning, "Warning exporting %s: %s" % (object, message))
    def nonexportable(self, object):   
        system.write_message(Severity.Information, "Object not exportable: %s" % object)
    @property
    def aborting(self):
        return False;


def parseObj(treeobj, depth=0):
    objs = list()
    if not treeobj.is_device:
       objs.append(treeobj)
    for child in treeobj.get_children(False):
        objs += parseObj(child, depth+1)
    return objs

def parseProj(proj):
    objs = list()
    for obj in proj.get_children():
       objs += parseObj(obj)
    return objs

class SearchBuildDo(helper.SearchBuild):
    # Build rules for:
    # - *.library -> *.compiled-library
    def doit(self, filename):
        reporter = ER()
        artifacts = list()

        tempname = filename + ".xml"
        mdname = filename + ".md"

        print("%s -> %s\n" % (filename, mdname))

        proj = projects.open(filename)
        objs = parseProj(proj)
        # proj.export_xml(reporter, proj.get_children(False), tempname, recursive = True)
        proj.export_xml(reporter, objs, tempname, recursive = False, declarations_as_plaintext = True)

        # XSLT transform
        print("Transform file with %s" % xslfile)
        xsl = XslCompiledTransform()
        xsl.Load(xslfile)
        xsl.Transform(tempname, mdname)
        # hacky fixup for XML preamble
        f = open(mdname, "r")
        if f:
            c = f.read()
            f.close()
            f = open(mdname, "w")
            if f:
                f.write(c[41:].replace("&lt;", "<").replace("&gt;", ">"));
                f.close()
        artifacts.append(mdname)

        proj.close()

        return artifacts


scriptpath = os.path.abspath(os.path.dirname(sys.argv[0]))

sb = SearchBuildDo()
sb.search(".library", ".")
sb.search(".project", ".")
sb.save(".", ".drone-artifacts")


