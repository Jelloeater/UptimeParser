import logging
from datetime import timedelta

logging.basicConfig(filename="uptime.log",
                    format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                    level=logging.WARNING)

import datetime
from pysnmp.hlapi import *


def get_uptime_datetime(address_in, snmp_comm_in='public', snmp_port_in=161):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(snmp_comm_in, mpModel=0),
               UdpTransportTarget((address_in, snmp_port_in)),
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
            logging.error(' = '.join([x.prettyPrint() for x in varBind]))


    ticks = int(varBinds[0][1])
    seconds = ticks / 100
    return datetime.timedelta(seconds=seconds)


def get_device_up_time_list():
    device_list = []
    devices = str(open('devices.txt').read()).splitlines()
    for i in devices:
        x = device()
        x.name = i
        x.up_time = get_uptime_datetime(i)
        device_list.append(x)
    return device_list




class device:
    up_time: timedelta

    def __init__(self):
        self.name = ""
        self.up_time = datetime.timedelta

    def is_over_x_hours(self, over_hours=24):
        dt = datetime.timedelta(hours=over_hours)
        if self.up_time > dt:
            return True
        else:
            return False


def main():
    ut_list = get_device_up_time_list()
    for i in ut_list:
        print(i.is_over_x_hours())


if __name__ == "__main__":
    main()
