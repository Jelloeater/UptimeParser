import logging

logging.basicConfig(filename="uptime.log",
                    format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                    level=logging.WARNING)

import datetime
from pysnmp.hlapi import *



def get_device_up_time_list():
    device_list = []
    devices_txt_list = str(open('devices.txt').read()).splitlines()

    for i in devices_txt_list:
        x = device(i)
        x.get_uptime_datetime()
        device_list.append(x)

    return device_list


class device:
    name: str
    up_time: datetime.timedelta

    def __init__(self,name_in):
        self.name = name_in
        self.up_time = None

    def get_uptime_datetime(self,snmp_comm_in='public', snmp_port_in=161):
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


def main():
    ut_list = get_device_up_time_list()
    devices_over_time_limit = 0
    for i in ut_list:
        if i.up_time:
            if i.is_over_x_hours():
                devices_over_time_limit = devices_over_time_limit + 1
        else:
            logging.error("Cannot get up time from: " + str(i.name))
    print(devices_over_time_limit)


if __name__ == "__main__":
    main()