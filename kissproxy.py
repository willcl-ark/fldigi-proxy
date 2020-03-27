#!/usr/bin/python3.7

from time import sleep
import pyfldigi

# Test starting of fldigi, text encode/decode, and accepting messages to pass to fldigi
# over a TCP/IP socket

# default ports: 7322 for ARQ, 7342 for TCP/IP, 7362 for XML, 8421 for fllog

class fl_instance:
    host_ip = '127.0.0.1'
    xml_port = 7362
    tcp_port = 7342
    start_delay = 5
    stop_delay = 3

    # we assume no port collisions / no other instance of fldigi is running
    # TODO: check for other fldigi instances before starting
    def __init__(self, host=host_ip, port=xml_port, headless=False, wfall_only=False, start_delay=start_delay):
        self.host_ip = host
        self.xml_port = port
        self.start_delay = start_delay
        self.fl_client = pyfldigi.Client(hostname=self.host_ip, port=self.xml_port)
        self.fl_app = pyfldigi.ApplicationMonitor(hostname=self.host_ip, port=self.xml_port)
        self.fl_app.start(headless=headless, wfall_only=wfall_only)
        sleep(self.start_delay)

    def port_info(self):
        print("IP", self.host_ip, "XML-RPC port:", self.xml_port, "TCP port:", self.tcp_port)

    def version(self):
        return self.fl_client.version


    def stop(self):
        self.fl_client.terminate(save_options=True)
        sleep(self.stop_delay)
        self.fl_app.kill()

fl_main = fl_instance()
print(fl_main.version())
fl_main.port_info()
fl_main.stop()