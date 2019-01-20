import logging
logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                    level=logging.INFO)
import sys,os
sys.path.append(os.path.realpath('..'))

from UptimeParserApp import UptimeParserMain

class TestMainModule():
    test_data = {"some sensor": 42, "more data": "7"}
    def test_create_XML_device_data(self):
        logging.info("\n"+UptimeParserMain.main.generate_xml(TestMainModule.test_data)+"\n")

    def test_create_JSON_device_data(self):
        logging.info("\n"+UptimeParserMain.main.generate_json(TestMainModule.test_data)+"\n")