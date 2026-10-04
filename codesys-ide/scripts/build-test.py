import sys, os
import helper

# disable prompts, as those are enabled in UI mode by default
system.prompt_handling = PromptHandling.None

# compile category GUID
CompileCategory = Guid("{97F48D64-A2A3-4856-B640-75C046E37EA9}")


def createtest(filename):
    destination = filename + ".app"
    devId = None
    devices = device_repository.get_all_devices("CODESYS Control for Linux SL")
    for device in devices:
        devId = device.device_id
    proj = projects.primary

    # check if this is a unit test project
    prg_runtest = proj.find('PRG_RUNTEST')
    if len(prg_runtest) == 0:
        proj.close()
        print("warning: no POU PRG_RUNTEST found. Will not create a test application.")
        return None

    # delete existing testdev device
    existing = proj.find('testdev')
    if len(existing) > 0:
        existing[0].remove()
 
    # add device
    proj.add('testdev', devId)
    apps = proj.find('Application', True)
    if len(apps) > 0:
        app = apps[0]
        tc = app.create_task_configuration()

    # add task to call PRG_RUNTEST
    task = tc.create_task('Task')
    task.pous.add('PRG_RUNTEST')

    helper.install_missing_libraries(proj, librarymanager)
    #    proj.save()
    print("create bootapp '%s'" % destination)
    try:
        proj.active_application.create_boot_application(os.path.basename(destination))
    except:
        print("Error: Creation of bootapplication failed")
        # Get message objects which contain all the data
        severities = {
            Severity.FatalError : "Fatal error", Severity.Error : "Error",
            Severity.Warning : "Warning", Severity.Information : "Information",
            Severity.Text : "Text"
        }
        msgs = system.get_message_objects(CompileCategory, Severity.FatalError|Severity.Error)
        xError = False
        for msg in msgs:
            sev = severities[msg.severity]
            if msg.severity == Severity.FatalError:
                xError = True
            print("%s %s%s: %s" % (sev, msg.prefix, msg.number, msg.text))
        if not xError:
            return None
    proj.close()
    return destination


class SearchBuildDo(helper.SearchBuild):
    # Test rules for:
    # - *.library
    def doit(self, filename):
        artifacts = list()
        helper.install_requirements(filename, librarymanager)

        if filename.endswith(".library"):
            print("\n\n*** Create test application for: %s" % filename)
            proj = projects.open(filename)
            artifact = createtest(filename)
            if artifact != None:
                artifacts.append(artifact)

        return artifacts

scriptpath = os.path.abspath(os.path.dirname(sys.argv[0]))

sb = SearchBuildDo()
sb.search(".library", ".")
sb.save(".", ".drone-artifacts")

