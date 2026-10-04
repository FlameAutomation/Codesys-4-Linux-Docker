###########################################################################################
# Helper classes for the different CI commands
###########################################################################################
import sys, os, re
import shutil
from System.Net import WebClient

class SearchBuild:
    def __init__(self):
        self.artifacts = list()
        self.error = False

    # search for files with a given file-ending, and call the method
    # doit() for every occurance
    def search(self, ending, folder):
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(ending):
                    self.artifacts += self.doit(os.path.join(root, file))
        print("%u artifact(s) created" % len(self.artifacts))

    def save(self, basepath, destination):
        for filename in self.artifacts:
            dirname = os.path.dirname(os.path.relpath(filename, basepath))
            if dirname.startswith(".."):
                dirname = os.path.dirname(filename).lstrip("/")
            destdir = os.path.join(destination, dirname)
            if not os.path.exists(destdir):
                os.mkdir(destdir)
            shutil.copy2(filename, destdir)
            print("%s => %s" % (filename, destdir))


    # dummy rule
    def doit(self, filename):
        artifacts = list()
        return artifacts

#
# Install a library from a URL (starting with http(s))
#
def install_library(url, librarymanager):
    if not url.startswith("http"):
        return
    downloaddir = os.path.join(os.environ["USERPROFILE"], "downloads")
    if not os.path.exists(downloaddir):
        os.makedirs(downloaddir)
    basename, extension = os.path.splitext(url)
    localname = os.path.join(downloaddir, "dl" + extension)
    print("*** download %s to %s\n" % (url, localname))

    web_client = WebClient()
    web_client.DownloadFile(url, localname)
    repo = librarymanager.repositories[0]
    print("*** installing %s from %s to %s\n" % (localname, url, repo))
    librarymanager.install_library (localname, repo, True)


#
# Check if there is a *.requirements file, and install
# all requirements from there. The parameter is a library
# URL, while we are checking if a *.requirements file exists
# beside this library.
#
def install_requirements(library_filename, librarymanager):
    reqfilename = os.path.splitext(library_filename)[0] + ".requirements"
    if os.path.isfile(reqfilename):
        reqfile = open(reqfilename, "r")
        for req in reqfile:
            req = req.strip()
            print("installing requirement '%s'." % req.strip())
            install_library(req, librarymanager)

#
# search for missing libraries in current primary project
#
def install_missing_libraries(proj, librarymanager):
    print("*** install missing libraries")
    # compile a regular expression to match lib placeholders
    p = re.compile('[^,]+, [^(]+\([^)]+\)')
    # search for libman
    objects = proj.get_children(recursive=True)
    for object in objects:
        if object.is_libman:
            print("*** parsing library manager...")
            libs = list()
            try:
                libs = iter(object)
            except:
                pass

            for libref in libs:
                libInfo = str(libref)
                # check if this library object has all attribute objects, that we need
                if not hasattr(libref, 'name'):
                    print("library has no attribute 'name'")
                    continue
                if not hasattr(libref, 'default_resolution'):
                    print("library has no attribute 'default_resolution'")
                    continue
                if not hasattr(libref, 'effective_resolution'):
                    print("library has no attribute 'effective_resolution'")
                    continue
                if not hasattr(libref, 'is_placeholder'):
                    print("library has no attribute 'is_placeholder'")
                    continue

                print("placeholder: %s: %s => %s" % (libref.name, libref.default_resolution, libref.effective_resolution))
                if libref.is_placeholder:
                    params = libref.parameters
                    for name in params:
                        print("   param: %s => %s" % (name, params[name]))

                    if libref.effective_resolution is None and libref.default_resolution is not None:
                        libInfo = str(libref.default_resolution)
                        m = re.findall('([^,]+), ([^(]+) \(([^)]+)\)', libInfo)
                        if len(m) > 0:
                            libname, libversion, libvendor = m[0]
                            if libversion == "*":
                                print("***")
                                print("*** %s has no effective resolution version. You need to set an effective version in the project!" % libInfo)
                                print("***")
                            indexurl = "https://store.codesys.com/CODESYSLibs/%s/%s/%s/index" % (libvendor, libname, libversion)
                            web_client = WebClient()
                            try:
                                filename = web_client.DownloadString(indexurl).rstrip()
                            except:
                                filename = None

                            try:
                                if filename != None:
                                    liburl = "https://store.codesys.com/CODESYSLibs/%s/%s/%s/%s" % (libvendor, libname, libversion, filename)
                                    install_library(liburl, librarymanager)
                                    print("---- finished install.")
                            except:
                                print("***  installation of library %s failed" % libInfo)
                elif libref.is_managed:
                    print("library: %s: %s" % (libref.name, libref.managed_library.version))
                else:
                    print("library: " + libref.name)
            print("... ended parsing library manager")


#
# update all devices in project
#
def update_device(proj, device_repository):
    print("*** update device")
    # search for devices to update
    objects = proj.get_children(recursive=True)
    for object in objects:
        if object.is_device:
            print("*** found device")
            DeviceId = object.get_device_identification()
            devices = device_repository.get_all_devices()
            for device in devices:
                if device.device_id.type == DeviceId.type and device.device_id.id == DeviceId.id:
                    deviceToUpdate = device
            if deviceToUpdate != None:
                print ("*** found device to update %s" % deviceToUpdate.device_id)
                object.update(device=deviceToUpdate.device_id)


