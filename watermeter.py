#!/usr/bin/env python

import Domoticz
import socket

class watermeter:
   
    def __init__(self, host=None, port=None): #54321
        self.host = host
        self.port = int(port)
        try:
            Domoticz.Debug ('Socket open...')
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
            self.s.settimeout(2)
            Domoticz.Debug ('Socket opened')
            self.s.connect((self.host, self.port))
            Domoticz.Debug ('Socket connected')


        except socket.error as msg:
            Domoticz.Debug ('Error Code: ' + str(msg))
        return


    def request_info(self):
        try:

            #Domoticz.Debug ('about to sent ')
            self.s.send(b'watermeter')
            #Domoticz.Debug ('sent ')

            # receive data from client 
            reply = self.s.recv(1024)

            #Domoticz.Debug  ('Response= '+repr(reply))

        except (ConnectionResetError, socket.timeout, OSError)  as e:
           #print("A problem occur please retry...")
           Domoticz.Debug  ('socket problem')

        try:
          # replay format "watermeter 24 24" 
          # the numbers should be the same (if not => transmission error)
          str1 = reply.decode("utf-8", errors="ignore")
          #Domoticz.Debug(str1)
          # split the string in numbers for validity check
          numbers = [int(word) for word in str1.split() if word.isdigit()]
          #Domoticz.Debug(repr(numbers))
          if numbers[0]==numbers[1] :
            return numbers[0]
        except:
           Domoticz.Debug  ('decode problem')
           return
