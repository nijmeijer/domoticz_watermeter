#!/usr/bin/env python

import Domoticz
import socket

class watermeter:

    infopackage_pre = 'w'
    m_counter = 1
    token = None
    m_key = None
    m_iv = None
 
    deviceid = None
    stamp = None
    packagelength = 0
    header = None
    headertemp = None

    def __init__(self, host=None, port=None): #54321
        self.host = host
        self.port = int(port)
        try:
            #Domoticz.Debug ('Socket open...')
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
            self.s.settimeout(2)
            #Domoticz.Debug ('Socket opened')

        except socket.error as msg:
            Domoticz.Debug ('Error Code: ' + str(msg))
        return


    def request_info(self):
        try:

            #Domoticz.Debug ('about to sent ')
            self.s.connect((self.host, self.port))
            self.s.send(b'watermeter')
            #Domoticz.Debug ('sent ')

            # receive data from client 
            reply = self.s.recv(1024)

            #Domoticz.Debug  ('Response= '+repr(reply))

        except (ConnectionResetError, socket.timeout, OSError)  as e:
           #print("A problem occur please retry...")
           Domoticz.Debug  ('socket problem')

        try:
          str1 = reply.decode("utf-8", errors="ignore")
          #Domoticz.Debug(str1)
          numbers = [int(word) for word in str1.split() if word.isdigit()]
          #Domoticz.Debug(repr(numbers))
          if numbers[0]==numbers[1] :
            return numbers[0]
        except:
           Domoticz.Debug  ('decode problem')
           return
