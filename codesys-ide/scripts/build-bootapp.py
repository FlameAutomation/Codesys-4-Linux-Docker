import sys, os
import helper

# disable prompts, as those are enabled in UI mode by default
system.prompt_handling = PromptHandling.None

# compile category GUID
CompileCategory = Guid("{97F48D64-A2A3-4856-B640-75C046E37EA9}")

class SearchBuildDo(helper.SearchBuild):
    # Build rules for:
    # - *.project -> *.app (boot application)
    def doit(self, filename):
        artifacts = list()
        if filename.endswith(".project"):
            destination = filename.replace(".project", ".app")
            crcfile = filename.replace(".project", ".crc")
            artifacts.append(destination)
            artifacts.append(crcfile)

            print("%s -> %s\n" % (filename, destination))
            proj = projects.open(filename)
            helper.update_device(proj, device_repository)
            helper.install_missing_libraries(proj, librarymanager)
            try:
                print("*** Create Bootapplication")
                proj.active_application.create_boot_application(os.path.basename(destination))
                print("... finished.")
                #proj.active_application.create_boot_application(destination)
            except:
                print("Error: Creation of bootapplication failed")
                # Get message objects which contain all the data
                severities = {
                    Severity.FatalError : "Fatal error", Severity.Error : "Error",
                    Severity.Warning : "Warning", Severity.Information : "Information",
                    Severity.Text : "Text"
                }
            finally:
                print("*** compile messages...")
                msgs = system.get_message_objects(CompileCategory, Severity.FatalError|Severity.Error)
                xError = False
                for msg in msgs:
                    sev = severities[msg.severity]
                    if msg.severity == Severity.FatalError:
                        xError = True
                    print("%s %s%s: %s" % (sev, msg.prefix, msg.number, msg.text))
                if xError:
                    return None
            proj.close()
        return artifacts

scriptpath = os.path.abspath(os.path.dirname(sys.argv[0]))

sb = SearchBuildDo()
sb.search(".project", ".")
sb.save(".", ".drone-artifacts")


