import enum


class WebSockekProtocol(enum.Enum):
    CHAT = "chat"
    ACTION = "action"
    DEFAULT = "default"