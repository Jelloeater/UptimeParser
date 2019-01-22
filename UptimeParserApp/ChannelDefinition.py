#!..\..\redist\Python34
# -*- coding: utf-8 -*-

import json

# # interpret first command line parameter as json object
# data = json.loads(sys.argv[1])
#
# # create sensor result
# result = CustomSensorResult("This sensor is added to " + data['host'])
#
# # add primary channel
# result.add_channel(channel_name="Percentage", unit="Percent", value=87, is_float=False, primary_channel=True,
#                    is_limit_mode=True, limit_min_error=10, limit_max_error=90,
#                    limit_error_msg="Percentage too high")
# # add additional channel
# result.add_channel(channel_name="Response Time", unit="TimeResponse", value="4711")
# # print sensor result to std
# print(result.get_json_result())

class CustomSensorResult:
    def __init__(self, sensor_message="OK"):
        self.channels = []
        self.has_error = False
        self.sensor_message = sensor_message

    def add_channel(
            self,
            channel_name,
            is_limit_mode=False,
            limit_max_error=None,
            limit_max_warning=None,
            limit_min_error=None,
            limit_min_warning=None,
            limit_error_msg=None,
            limit_warning_msg=None,
            decimal_mode=None,
            mode=None,
            value=None,
            unit='Custom',
            is_float=False,
            value_lookup=None,
            show_chart=True,
            warning=False,
            primary_channel=False
    ):
        channel = {}

        if is_float:
            channel['Value'] = float(value)
        else:
            channel['Value'] = int(value)

        if self.__if_custom_unit(unit):
            channel['CustomUnit'] = unit
        else:
            channel['Unit'] = unit

        channel['Channel'] = channel_name

        if is_limit_mode:
            channel['LimitMode'] = 1
            if limit_max_error is not None:
                channel['LimitMaxError'] = limit_max_error
            if limit_max_warning is not None:
                channel['LimitMaxWarning'] = limit_max_warning
            if limit_min_error is not None:
                channel['LimitMinError'] = limit_min_error
            if limit_min_warning is not None:
                channel['LimitMinWarning'] = limit_min_warning
            if limit_error_msg is not None:
                channel['LimitErrorMsg'] = limit_error_msg
            if limit_warning_msg is not None:
                channel['LimitWarningMsg'] = limit_warning_msg

        if mode is not None:
            channel['Mode'] = mode

        if is_float:
            channel['DecimalMode'] = 'All'
            channel['Float'] = 1

        if decimal_mode is not None:
            channel['DecimalMode'] = decimal_mode

        if value_lookup is not None:
            channel['ValueLookup'] = value_lookup

        if not show_chart:
            channel['ShowChart'] = 0
        if warning:
            channel['Warning'] = 1

        if primary_channel:
            self.channels.insert(0, channel)
        else:
            self.channels.append(channel)

    @staticmethod
    def __if_custom_unit(unit):

        valid_units = {
            "BytesBandwidth",
            "BytesMemory",
            "BytesDisk",
            "Temperature",
            "Percent",
            "TimeResponse",
            "TimeSeconds",
            "Custom",
            "Count",
            "CPU",
            "BytesFile",
            "SpeedDisk",
            "SpeedNet",
            "TimeHours"
        }

        if unit not in valid_units:
            return True
        else:
            return False

    def add_primary_channel(self, channel_name, unit=None, value=None, is_float=True):
        self.add_channel(channel_name=channel_name, value=value, unit=unit, is_float=is_float, primary_channel=True)

    def add_error(self, error_text):

        self.channels = {
            'Error': 1,
            'Text': error_text
        }
        self.has_error = True

    def get_result(self):
        result = str()
        if self.has_error:
            result = {'prtg': self.channels}
        else:
            result = {'prtg': {'text': self.sensor_message, 'result': self.channels}}
        return result

    def get_json_result(self):
        result = self.get_result()
        result_json = json.dumps(result)
        return result_json
