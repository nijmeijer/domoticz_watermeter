"""
<plugin key="Watermeter2" name="Watermeter Sensor2" author="nijmeijer" version="1.0.2">
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="192.168.1.86"/>
        <param field="Port" label="Port" width="50px" required="true" default="5001"/>
        <param field="Mode2" label="Poll Period (min)" width="75px" required="true" default="1"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
from watermeter2 import watermeter2
import json

class BasePlugin:

    def __init__(self):
        self.pollPeriod = 0
        self.pollCount = 0
        self.PrevSample = 0
        self.IdleCount = 0
        return

    def onStart(self):

        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)

        if (len(Devices) == 0):
            Domoticz.Device(Name="WaterMeter Neads2", Unit=1, TypeName="Counter Incremental", Type=243, Subtype=28, Used=1).Create()

        Domoticz.Debug("Device created.")
        DumpConfigToLog()

        self.pollPeriod = 1 * int(Parameters["Mode2"])
        self.pollCount = self.pollPeriod - 1

        self.watermeterapi = watermeter2(Parameters['Address'],Parameters['Port'])

        Domoticz.Heartbeat(2)



    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data, Status, Extra):
        Domoticz.Log('received')
        strData = Data.decode("utf-8", "ignore")
        Domoticz.Debug("onMessage called with Data: '"+str(Data)+"'")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")
        self.isConnected = False 

    def onHeartbeat(self):
        # Domoticz.Debug("onHeartBeat called:"+str(self.pollCount)+"/"+str(self.pollPeriod))
        if self.pollCount >= self.pollPeriod*30: #PollPeriod is 0...n minutes, PollCount increments every 2 secs
            #watermeterapi = watermeter(Parameters['Address'],Parameters['Port'])
            #self.watermeterapi = watermeter2(Parameters['Address'],Parameters['Port'])

            if 1==1 :
                curmeas = self.watermeterapi.request_info()
                Domoticz.Debug("watermeter2 plugin received: " + repr(curmeas))
                # Domoticz.Debug("watermeter2 current value: " + repr(Devices[1].nValue))
                Domoticz.Debug("watermeter2 my prevsample: " + repr(self.PrevSample))
                # if we are sure that we have a valid increment, pass it on to Domoticz
                if self.PrevSample>0 and curmeas > 0 and curmeas>self.PrevSample :
                  #if curmeas > 0 and curmeas>self.PrevSample :
                  newval = Devices[1].nValue + curmeas - self.PrevSample
                  Domoticz.Debug("Updating device")
                  UpdateDevice(1,(curmeas - self.PrevSample),(curmeas - self.PrevSample))
                  Domoticz.Debug("Device updated")
                  self.PrevSample=curmeas
                  self.IdleCount = 0
                else :
                 if curmeas>0 :
                   self.PrevSample=curmeas
            self.pollCount = 0 #Reset Pollcount
        else:
            self.pollCount += 1

        # Update Anyway, even if the counter stands still.
        # it triggers a display update
        self.IdleCount = self.IdleCount + 1
        if self.IdleCount > (5-1) :
            UpdateDevice(1,0,0)
            self.IdleCount = 0
 


global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data, Status, Extra):
    global _plugin
    _plugin.onMessage(Connection, Data, Status, Extra)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def UpdateDevice(Unit, nValue, sValue):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
            Devices[Unit].Update(nValue, str(sValue))
            Domoticz.Debug("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
