import sys, os
import helper
import zipfile

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            if not file.endswith(".package"):
                filename=os.path.join(root, file)
                archname=filename[len(path)+1:]
                print("Adding file: %s -> %s" % (filename, archname))
                ziph.write(filename, arcname=archname)

class SearchBuildDo(helper.SearchBuild):
    # Build rules for:
    # - package.manifest -> *.package
    def doit(self, filename):
        artifacts = list()

        if filename.endswith("package.manifest"):
            packageDir = os.path.dirname(filename)
            if packageDir == ".":
                destination = "master.package"
            else:
                destination = packageDir + ".package"
            artifacts.append(destination)
            print("%s -> %s\n" % (filename, destination))

            zipf = zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED)
            zipdir(packageDir, zipf)
            zipf.close()

        return artifacts

scriptpath = os.path.abspath(os.path.dirname(sys.argv[0]))

sb = SearchBuildDo()
sb.search("package.manifest", ".")
sb.save(".", ".drone-artifacts")


