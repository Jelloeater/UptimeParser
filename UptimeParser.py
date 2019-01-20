import logging
import os
import threading
from multiprocessing.pool import ThreadPool
from typing import List
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from pysnmp.error import PySnmpError
import device_list

logging.basicConfig(filename="uptime.log",
                    format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                    level=logging.DEBUG)

import datetime
from pysnmp.hlapi import *


def get_device_list():
    d_list = []
    devices_txt_list = device_list.device_list

    for i in devices_txt_list:
        d_list.append(device(i))

    return d_list


class device():
    # name: str
    # up_time: datetime.timedelta

    def __init__(self, name_in):
        self.name = name_in
        self.up_time = None

    def update_uptime(self, snmp_comm_in='public', snmp_port_in=161):
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(snmp_comm_in, mpModel=0),
                   UdpTransportTarget((self.name, snmp_port_in)),
                   ContextData(),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysUpTime', 0)))
        )

        if errorIndication:
            logging.error(errorIndication)
        elif errorStatus:
            logging.error('%s at %s' % (errorStatus.prettyPrint(),
                                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            for varBind in varBinds:
                logging.info(' = '.join([x.prettyPrint() for x in varBind]))

        try:
            ticks = int(varBinds[0][1])
            seconds = ticks / 100
            self.up_time = datetime.timedelta(seconds=seconds)
        except IndexError:
            self.up_time = False

    def is_over_x_hours(self, over_hours=24):
        dt = datetime.timedelta(hours=over_hours)
        if self.up_time > dt:
            return True
        else:
            return False


def update_device_obj_uptime(device_obj: device) -> device:
    '''Takes in device object and updates it's uptime property'''
    logging.debug(threading.current_thread())
    try:
        device_obj.update_uptime()
    except PySnmpError:
        logging.error("Bad Address: " + device_obj.name)
    return device_obj


def main():
    device_list: List[device] = get_device_list()

    # This takes a list of device objects (missing uptime), and then maps them to a threadpool
    # This pool then gets executed and the results of the static helper function and passed into a list

    pool = ThreadPool()
    results = pool.map(update_device_obj_uptime,
                       device_list)  # Takes function to work against, and itterable list to work on
    pool.close()
    pool.join()

    devices_over_time_limit = 0
    for i in results:
        if i.up_time:
            if i.is_over_x_hours():
                devices_over_time_limit = devices_over_time_limit + 1
        else:
            logging.error("Cannot get up time from: " + str(i.name))

    pool.terminate()

    # Generate XML Output
    top = Element('prtg')

    result1 = SubElement(top, 'result')
    channel = SubElement(result1, 'channel')
    channel.text = 'Device count'
    valuel = SubElement(result1, 'value')
    valuel.text = str(device_list.__len__())

    result2 = SubElement(top, 'result')
    channel2 = SubElement(result2, 'channel')
    channel2.text = 'Device over time limit'
    valuel2 = SubElement(result2, 'value')
    valuel2.text = str(devices_over_time_limit)

    # Clean XML output for PRTG, strip extra junk
    reparsed = minidom.parseString(tostring(top).decode())
    return str(reparsed.toprettyxml(indent="")).replace('<?xml version="1.0" ?>', "").strip()


if __name__ == "__main__":
    logging.info("START")
    logging.info(str(os.getcwd()))

    out = main()
    print(out)
