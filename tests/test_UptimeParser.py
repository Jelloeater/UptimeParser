import logging
import sys

logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                    level=logging.INFO)

sys.path.append('./UptimeParserApp')  # Needed to import module properly

import UptimeParserApp.UptimeParserMain as UptimeParser
class TestMainModule():
    def test_create_XML_device_data(self):
        test_data = {"some sensor":42,"more data":"text"}
        logging.info("\n"+UptimeParser.main.generate_xml(test_data)+"\n")