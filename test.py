import time, asyncio
from miio import AirConditioningCompanion, DeviceException

device = AirConditioningCompanion('192.168.1.106', 'e7d17baf8f9e05103b502afa163ee0a7')

''' 发码
ir_command = 'FE00000000000000000000000004009622BA003600A601D4138822010001010000010000010000010100010101010000000001000000010101010000000000000100000101010101000101022201000101000001000001000001010001010001010101010100010000000000000000010000000000010100010101010102220100010100000100000100000101000101000101010101010001000000000000000001000000000001010001010101010301'
state = device.status()
air_condition_model = state.air_condition_model.hex()
if air_condition_model is not None:
    device.send_ir_code(air_condition_model, ir_command)
'''