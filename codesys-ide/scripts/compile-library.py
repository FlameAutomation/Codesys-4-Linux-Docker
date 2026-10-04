import sys, os
import helper

class SearchBuildDo(helper.SearchBuild):
    # Build rules for:
    # - *.library -> *.compiled-library
    def doit(self, filename):
        artifacts = list()

        if filename.endswith(".library"):
            destination = filename.replace(".library", ".compiled-library")
            artifacts.append(destination)

            print("%s -> %s\n" % (filename, destination))

            proj = projects.open(filename)
            proj.save_as_compiled_library(destination)
            proj.close()

        return artifacts

scriptpath = os.path.abspath(os.path.dirname(sys.argv[0]))

sb = SearchBuildDo()
sb.search(".library", ".")
sb.save(".", ".drone-artifacts")
