import argparse
import datetime
import ipaddress
import logging
import os
import sys
import threading
from multiprocessing.pool import ThreadPool
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from pysnmp.smi.error import MibNotFoundError

from UptimeParserApp.ChannelDefinition import CustomSensorResult

logging.basicConfig(filename="uptime.log",
                    format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                    level=logging.DEBUG)
from pysnmp.hlapi import *


class device:
    # name: str
    # up_time: datetime.timedelta

    def __init__(self, name_in: str, snmp_in: str):
        self.name = name_in
        self.up_time = None
        self.snmp_comm = snmp_in

    def update_uptime(self, snmp_port_in=161):
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(self.snmp_comm, mpModel=0),
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


class main:

    @staticmethod
    def run_main():
        """ Take arguments and direct program """
        parser = argparse.ArgumentParser()

        parser.add_argument("-ip", help="IP address in CIDR notation (ex 192.168.1.0/24)",
                            required=True)

        parser.add_argument("-snmp", help="SNMP Community string (ex public)")

        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("-j",
                           action="store_true",
                           help="JSON Output")
        group.add_argument("-x",
                           action="store_true",
                           help="XML Output")

        args = parser.parse_args()
        if len(sys.argv) == 1:  # Displays help and lists servers (to help first time users)
            parser.print_help()
            sys.exit(0)

        main.main_logic(args)  # Pass args to logic

        logging.info("EOP")

    @staticmethod
    def main_logic(args_in: argparse):

        try:
            ip_obj = ipaddress.IPv4Network(args_in.ip)
        except ValueError:
            print("Invalid IP address")
            sys.exit(1)

        hosts = set()  # Create empty unordered set
        for h in ip_obj.hosts():
            hosts.add(h)

        if hosts.__len__() == 0:  # In case we input a /32, still create a host in the list
            hosts.add(ipaddress.IPv4Network(args_in.ip).network_address)

        # Feeds generated IP host list tp sensor data generator
        device_list = []
        for i in hosts:
            if args_in.snmp is None:
                device_list.append(device(name_in=str(i), snmp_in='public'))
            else:
                device_list.append(device(name_in=str(i), snmp_in=args_in.snmp))

        PRTG_data = main.generate_sensor_data(device_list)

        if args_in.x:
            print(main.generate_xml(PRTG_data))
        if args_in.j:
            print(main.generate_json(PRTG_data))

    @staticmethod
    def update_device_obj_uptime(device_obj: device) -> device:
        """Takes in device object and updates it's uptime property"""
        logging.debug(threading.current_thread())
        device_obj.update_uptime()
        try:
            device_obj.update_uptime()
        except MibNotFoundError:
            logging.critical("MISSING MIB Libs")
            sys.exit(1)  # PEACE OUT!
        return device_obj

    @staticmethod
    def generate_sensor_data(device_list_in: list) -> dict:

        # This takes a list of device objects (missing uptime), and then maps them to a thread pool
        # This pool then gets executed and the results of the static helper function and passed into a list

        pool = ThreadPool()
        results = pool.map(main.update_device_obj_uptime,
                           device_list_in)  # Takes function to work against, and iterable list to work on
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

        up_device_count = 0
        for i in device_list_in:
            if i.up_time != False:
                up_device_count = up_device_count + 1

        return {"Up Device count": up_device_count, "Device over time limit": devices_over_time_limit}

    @staticmethod
    def generate_xml(data_in: dict, message_in="Ok") -> str:
        top = Element('prtg')

        for k, v in data_in.items():
            result = SubElement(top, 'result')
            channel = SubElement(result, 'channel')
            channel.text = str(k)
            value = SubElement(result, 'value')
            if v is not int:
                try:
                    v = int(v)
                except ValueError:
                    raise Exception('Input value needs to be an int')
            value.text = str(v)
        result = SubElement(top, 'text')
        result.text = str(message_in)
        # Clean XML output for PRTG, strip extra junk
        clean_xml = minidom.parseString(tostring(top).decode())
        return str(clean_xml.toprettyxml(indent="")).replace('<?xml version="1.0" ?>', "").strip()

    @staticmethod
    def generate_json(data_in: dict, message_in="Ok") -> str:
        result = CustomSensorResult(str(message_in))
        for k, v in data_in.items():
            result.add_channel(channel_name=str(k), unit="Custom", value=str(v))
        return result.get_json_result()


if __name__ == "__main__":
    logging.info("START")
    logging.info(str(os.getcwd()))

    main.run_main()
