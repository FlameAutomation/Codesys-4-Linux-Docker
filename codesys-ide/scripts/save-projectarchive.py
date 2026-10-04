import sys, os
import helper

class SearchBuildDo(helper.SearchBuild):
    # Build rules for:
    # - *.project -> *.projectarchive
    def doit(self, filename):
        artifacts = list()

        if filename.endswith(".project"):
            destination = filename.replace(".project", ".projectarchive")
            artifacts.append(destination)

            print("%s -> %s\n" % (filename, destination))

            proj = projects.open(filename)
            helper.update_device(proj, device_repository)
            helper.install_missing_libraries(proj, librarymanager)
            proj.save_archive(destination)
            proj.close()

        return artifacts

scriptpath = os.path.abspath(os.path.dirname(sys.argv[0]))

sb = SearchBuildDo()
sb.search(".project", ".")
sb.save(".", ".drone-artifacts")
