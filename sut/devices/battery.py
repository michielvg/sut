
from enum import Enum

from sut.devices.device import Device
from sut.message_dispatcher import MessageDirection, MessageDispatcher
from sut.messages.empty import EmptyMsg
from sut.messages.message import Msg, MsgType


class BatteryModel(Enum):
    BT_E6000 = "BT-E6000"
    BT_E6000_A = "BT-E6000-A"
    BT_E6001 = "BT-E6001"
    BT_E6001_A = "BT-E6001-A"
    BT_E8010 = "BT-E8010"
    BT_E8010_A = "BT-E8010-A"
    BT_E8014 = "BT-E8014"
    BT_E8014_A = "BT-E8014-A"
    BT_E8016 = "BT-E8016"
    BT_E8016_A = "BT-E8016-A"
    BT_E8020 = "BT-E8020"
    BT_E8035 = "BT-E8035"
    BT_E8035_A = "BT-E8035-A"
    BT_E8035_L = "BT-E8035-L"
    BT_E8035_L_A = "BT-E8035-L-A"
    BT_E8036 = "BT-E8036"
    BT_E8036_A = "BT-E8036-A"
    BT_EN404 = "BT-EN404"
    BT_EN404_A = "BT-EN404-A"
    BT_EN405 = "BT-EN405"
    BT_EN405_A = "BT-EN405-A"
    BT_EN604 = "BT-EN604"
    BT_EN604_A = "BT-EN604-A"
    BT_EN605 = "BT-EN605"
    BT_EN605_A = "BT-EN605-A"
    BT_EN606 = "BT-EN606"
    BT_EN606_A = "BT-EN606-A"
    BT_EN805 = "BT-EN805"
    BT_EN805_A = "BT-EN805-A"
    BT_EN805_L = "BT-EN805-L"
    BT_EN805_L_A = "BT-EN805-L-A"
    BT_EN806 = "BT-EN806"
    BT_EN806_A = "BT-EN806-A"
    BT_EN817_B = "BT-EN817-B"  # This battery is the only one not using the same charger, not sure if it uses the same protocol.

class Battery(Device):
    def __init__(self, model: BatteryModel, dispatcher: MessageDispatcher):
        super().__init__(model, dispatcher)


    def setup(self):
        for msg_type in self._msg_map:
            self.dispatcher.subscribe(
                msg_type,
                self._generic_request_handler,
                MessageDirection.RX
            )

        self.register_message_types()

    def register_message_types(self):
        for msg_type, msg_cls in self._msg_map.items():
            self.dispatcher.register_type(msg_type, msg_cls)

    def _generic_request_handler(self, msg: Msg, disp: MessageDispatcher, direction: MessageDirection):
        msg_cls = self._msg_map.get(msg.type)
        if msg_cls is None:
            return

        # Avoid replying to own messages
        if msg_cls != EmptyMsg and isinstance(msg, msg_cls):
            return

        # Allow subclass override
        reply = self.build_reply(msg, msg_cls)

        if reply is not None:
            disp.send_message(reply)

    def build_reply(self, msg: Msg, msg_cls):
        """Default reply behavior (can be overridden)"""
        if msg.type == MsgType.EMPTY:
            if msg.sender == 0x40:
                return msg_cls.reply_for_msg(msg)
            return None

        return msg_cls.reply_for_msg(msg)