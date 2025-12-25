import enum


class WebSockekProtocol(enum.Enum):
    CHAT = "chat"
    ACTION = "action"
    STATE = "state"
    DEFAULT = "default"