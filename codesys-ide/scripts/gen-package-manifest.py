import sys, os, glob
import uuid
import helper

ManifestSkeleton="""<?xml version="1.0" encoding="ISO-8859-1"?>
<Package>
  <Strings>
    <String Id="GeneralName">
      <Neutral>%s</Neutral>
    </String>
    <String Id="GeneralVendor">
      <Neutral>%s</Neutral>
    </String>
    <String Id="GeneralCopyright">
      <Neutral>%s</Neutral>
    </String>
    <String Id="GeneralDescription">
      <Neutral>%s</Neutral>
    </String>    
    <String Id="license">
      <Neutral>%s</Neutral>
    </String>        
    <String Id="TargetDir">
      <Neutral>Target directory</Neutral>
    </String>
    <String Id="TargetDirDescription">
      <Neutral>The target directory where the projects are saved.</Neutral>
    </String>
  </Strings>
  <General>
    <Id>{%s}</Id>
    <Version>1.0.0.0</Version>
    <Name>$GeneralName</Name>
    <Vendor>$GeneralVendor</Vendor>
    <Copyright>$GeneralCopyright</Copyright>
    <Description>$GeneralDescription</Description>    
    <LicenseAgreement>$license</LicenseAgreement>        
    <RequiredInstallerVersion>3.5.10.0</RequiredInstallerVersion>
  </General>
  <TargetDirectoryDefinitions>  
    <TargetDirectoryDefinition>
      <Id>1</Id>
      <Name>$TargetDir</Name>
      <Description>$TargetDirDescription</Description>
      <PromptUser>True</PromptUser>
      <DefaultValue>%%USERPROFILE%%\CODESYS Projects\</DefaultValue>
    </TargetDirectoryDefinition>
  </TargetDirectoryDefinitions>
  <Components>                
    <Component>
      <General>
    <Id>1</Id>
    <Name>Default</Name>
    <Description>Default Package</Description>
    <Selectable>false</Selectable>
    <SelectedByDefault>true</SelectedByDefault>
      </General>
      <Dependencies>            
      </Dependencies>
      <Items>
%s
      </Items>            
    </Component>     
  </Components>
</Package>
"""

ManifestItemLibrary = """
        <Library>
          <Path>%s</Path>
        </Library>
"""

ManifestItemDevDesc = """
        <DeviceDescription>
          <Path>%s</Path>
        </DeviceDescription>
"""

ManifestItemProject = """
        <File>
          <Path>%s</Path>
          <IgnoreArchiveFolder>True</IgnoreArchiveFolder>
          <TargetFolder>$1</TargetFolder>
          <Overwrite>
            <Option>Yes</Option>
          </Overwrite>
        </File>
"""


class SearchBuildDo(helper.SearchBuild):
    basepath=''
    packageItems=''
    license=''

    # define basepath of the package
    def setbasepath(self, path):
       self.basepath=path

    # Build rules for:
    # - package.manifest
    # search for all files that we want to pack
    def doit(self, filename):
        artifacts = list()

        archname=filename[len(self.basepath)+1:]
        if filename.endswith(".project"):
            self.packageItems += ManifestItemProject % (archname)
        if filename.endswith(".devdesc.xml"):
            self.packageItems += ManifestItemDevDesc % (archname)
        if filename.endswith(".library"):
            self.packageItems += ManifestItemLibrary % (archname)
        if filename == "license.txt":
            self.license = archname;

        return artifacts

    def write(self, name, vendor, copyright, description):
        # add an empty license file if none was found
        if self.license == '':
            file = open(os.path.join(self.basepath, "license.txt"), "w")
            if file:
                file.write("No license file found.")
                file.close();
            self.license = "license.txt"

        guid = uuid.uuid1();
        packageManifest = ManifestSkeleton % (name, vendor, copyright, description, self.license, guid, self.packageItems)

        filename = os.path.join(self.basepath, 'package.manifest')
        if not os.path.isfile(filename):
            file = open(filename, "w")
            if file:
                file.write(packageManifest)
                file.close();
        self.artifacts.append(filename)


packageFolders = list()
# add trunk / master
if os.path.isdir('trunk'):
    packageFolders.append('trunk')
else:
    packageFolders.append('.')

# add all branches
if os.path.isdir('branches'):
    for filename in glob.iglob('branches/**'):
        if os.path.isdir(filename):
            packageFolders.append(filename)



for folder in packageFolders:
    print ("creating manifest for folder '%s'." % folder)
    sb = SearchBuildDo()
    sb.setbasepath(folder)
    sb.search(".library", ".")
    sb.search(".project", ".")
    sb.search(".devdesc.xml", ".")
    sb.search("license.txt", ".")

    name = folder
    if name == ".":
        name = "master"
    print("writing package manifest for '%s'." % name)
    sb.write(name, "unknown vendor", "unknown copyright", "no description")

sb.save(".", ".drone-artifacts")

