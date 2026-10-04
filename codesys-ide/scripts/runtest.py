# CODESYS with UI
import sys, os
import helper

# redirect output, as in UI mode no output is printed on the console
sys.stdout = open('.codesys.output.txt', 'w')

# disable prompts, as those are enabled in UI mode by default
system.prompt_handling = PromptHandling.None

# compile category GUID
CompileCategory = Guid("{97F48D64-A2A3-4856-B640-75C046E37EA9}")

def runtest():
#    devId = device_repository.create_device_identification(4096, '0000 0001', '3.5.15.0')
    devId = None
    devices = device_repository.get_all_devices("CODESYS Control Win V3")
    for device in devices:
        devId = device.device_id
    proj = projects.primary
    
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

    # set device to simulation mode
    devs = proj.find('testdev')
    if len(devs) > 0:
        devs[0].set_simulation_mode(True)

    # login
    onlineapp = online.create_online_application(app)
    try:
        onlineapp.login(OnlineChangeOption.Try, True)
    except:
        print("Error: compile error")
        # Get message objects which contain all the data
        severities = {
            Severity.FatalError : "Fatal error", Severity.Error : "Error",
            Severity.Warning : "Warning", Severity.Information : "Information",
            Severity.Text : "Text"
        }
        msgs = system.get_message_objects(CompileCategory, Severity.FatalError|Severity.Error)
        for msg in msgs:
            sev = severities[msg.severity]
            print("{} {}{}: {}".format(sev, msg.prefix, msg.number, msg.text))
        return False

    # run program
    onlineapp.start()

    # wait until project finishes
    for timeout in range(10):
        system.delay(1000)
        xready = onlineapp.read_value("PRG_RUNTEST.xReady")
        if str(xready) == "TRUE":
            break
    # check for error
    xerror = onlineapp.read_value("PRG_RUNTEST.xError")

    # display value in message view or command line
    print("Info: State Results of Test: xError: %s, xReady: %s" % (xerror, xready))



    try:
        szMessage = onlineapp.read_value("PRG_RUNTEST.szMessage")
        print("*** Test Messages:")
        print(szMessage)
        print("*** end")
    except:
        pass
              
    if not str(xerror) == "FALSE":
        print("Error: Test failed")
        onlineapp.logout()
        return False
    else:
        print("Info: Test passed")
        onlineapp.logout()
        return True

class SearchBuildDo(helper.SearchBuild):
    # Test rules for:
    # - *.library
    def doit(self, filename):
        artifacts = list()
        helper.install_requirements(filename, librarymanager)
        
        if filename.endswith(".library"):
            print("\n\n*** Test: %s" % filename)
            proj = projects.open(filename)
            if not runtest():
                self.error = True
            proj.close()

        return artifacts

scriptpath = os.path.abspath(os.path.dirname(sys.argv[0]))

sb = SearchBuildDo()
sb.search(".library", ".")
sb.save(".", ".drone-artifacts")

if sb.error:
    system.exit(1)
system.exit()
