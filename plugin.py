"""
<plugin key="Watermeter2" name="Watermeter Sensor2" author="nijmeijer" version="1.0.4">
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
        self.prevtime = 0
        self.LastIncrementAge = 0
        self.prevtime = 0
        self.PosFlowDurationSec = 0

        return

    def onStart(self):

        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)

        if (len(Devices) == 0):
            Domoticz.Device(Name="WaterMeter Neads2", Unit=1, TypeName="Counter Incremental", Type=243, Subtype=28, Used=1).Create()
            Domoticz.Device(Name="WaterMeter Neads2 - Flow", Unit=2, TypeName="Waterflow", Type=243, Subtype=30, Used=0).Create()
            #Domoticz.Device(Name="WaterMeter Duration Min", Unit=3,  Type=243, Subtype=28, Switchtype=5, Used=0).Create() # counter incremental, Time

        if (len(Devices) == 1):
            Domoticz.Device(Name="WaterMeter Neads2 - Flow", Unit=2, Type=243, Subtype=30, Used=0).Create()
            #Domoticz.Device(Name="WaterMeter Duration Min", Unit=3,  Type=243, Subtype=28, Switchtype=5, Used=0).Create() # counter incremental, Time

        if (len(Devices) == 2):
            Domoticz.Device(Name="WaterMeter Duration Min", Unit=3,  Type=243, Subtype=28, Switchtype=5, Used=0).Create() # counter incremental, Time
            #pass

        UpdateDevice(3,0,-1) # initialize timer svalue=neg
        Domoticz.Debug("Devices created.")
        DumpConfigToLog()

        self.pollPeriod = 1 * int(Parameters["Mode2"])
        self.pollCount = self.pollPeriod - 1

        self.watermeterapi = watermeter2(Parameters['Address'],Parameters['Port'])
        self.watermeterapi.open_socket()

        self.PosFlowDurationSec = 0
        self.prevtime = 0

        # Initialize flow to 0
        UpdateDevice(2,0,0)
        # increment duration by 0
        UpdateDevice(3,0,0) 

        Domoticz.Heartbeat(10)



    def onStop(self):
        Domoticz.Debug("onStop called")
        self.watermeterapi.close_socket()
        self.isConnected = False

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
        self.watermeterapi.close_socket()
        self.isConnected = False

    def onHeartbeat(self):
        duration_between_updates = 0
        flow = 0
        # Domoticz.Debug("onHeartBeat called:"+str(self.pollCount)+"/"+str(self.pollPeriod))
        if self.pollCount >= self.pollPeriod*30: #PollPeriod is 0...n minutes, PollCount increments every 2 secs
            #watermeterapi = watermeter(Parameters['Address'],Parameters['Port'])
            #self.watermeterapi = watermeter2(Parameters['Address'],Parameters['Port'])

            if 1==1 :
                curmeas, currenttime = self.watermeterapi.request_info()
                Domoticz.Debug("watermeter2 flow current/prev time: " + repr(currenttime) + "/" +repr(self.prevtime))

                if self.prevtime>0 : #and (currenttime - self.prevtime) > 1000 :  # flow=0 when time unchanged
                  try :
                     duration_between_updates = (currenttime -  self.prevtime)
                     flow=round(60*1000/(currenttime -  self.prevtime)) # ms/tick -> liters/min
                     UpdateDevice(2,0,flow)
                  except :
                    flow=0
                    duration_between_updates = 0
                else :
                  flow=0

                #last increment is too long ago, assume flow=0
                Domoticz.Debug("watermeter2 flow timeout check ")
                if (self.LastIncrementAge > 60/2 ) : #   one minute -> #heartbeats
                  flow=0
                  Domoticz.Debug("watermeter2 flow set to 0 because of timeout " + repr(self.LastIncrementAge) )
                  UpdateDevice(2,0,flow)

                if currenttime > 0 :
                  self.prevtime=currenttime

                if (self.PrevSample != curmeas) :
                  self.LastIncrementAge = 0
                self.LastIncrementAge +=  1

                #Domoticz.Debug("watermeter2 plugin received: " + repr(curmeas))
                Domoticz.Debug("watermeter2 my prevsample: " + repr(self.PrevSample) + " new received: " + repr(curmeas))
                # if we are sure that we have a valid increment, pass it on to Domoticz
                if self.PrevSample>0 and curmeas > 0 and curmeas>self.PrevSample :
                  #if curmeas > 0 and curmeas>self.PrevSample :
                  newval = Devices[1].nValue + curmeas - self.PrevSample
                  UpdateDevice(1,(curmeas - self.PrevSample),(curmeas - self.PrevSample))
                  self.PrevSample=curmeas
                  self.IdleCount = 0
                else :
                 if curmeas>0 :
                   self.PrevSample=curmeas
            self.pollCount = 0 #Reset Pollcount
        else:
            # not polling
            self.pollCount += 1

        # Update Anyway, even if the counter stands still.
        # it triggers a display update
        self.IdleCount = self.IdleCount + 1
        if self.IdleCount > (5-1) :
            UpdateDevice(1,0,0)
            self.IdleCount = 0

        # keep track of time for a flow>0
        if flow > 0 :
           UpdateDevice(3,0,duration_between_updates/1000) # increment by 2 seconds


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

#def UpdateDevice_sonly(Unit, sValue):
#  # Make sure that the Domoticz device still exists (they can be deleted) before updating it
#  try:
#    a=print("{0:f}".format(sValue))
#    if (Unit in Devices):
#         Devices[Unit].Update(0, a)
#         Domoticz.Debug("Update "+a+" (" + Devices[Unit].Name+")")
#    return
#  except:
#    pass


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
