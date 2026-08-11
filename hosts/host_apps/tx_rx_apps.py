import threading
from abc import ABC, abstractmethod

from hosts.host_app import HostApp


class TXRXHostApp(HostApp, ABC):

    # Sender and receivers are functions to be defined by subclasses
    def __init__(self, sender, receiver):
        self.sender = sender
        self.receiver = receiver

    def run(self):
        sender_thread = threading.Thread(
            target=self.sender
        )

        receiver_thread = threading.Thread(
            target=self.receiver
        )


        sender_thread.start()
        receiver_thread.start()

        sender_thread.join()
        receiver_thread.join()


class BaseListenerHostApp(TXRXHostApp, ABC):

    def __init__(self, port):
        super().__init__(lambda: '', self.listen)
        self.port = port

    @abstractmethod
    def listen(self):
        pass


class BaseSpeakerHostApp(TXRXHostApp, ABC):

    def __init__(self, dst_ip, port):
        super().__init__(self.send, lambda: '')
        self.dst_ip = dst_ip
        self.port = port

    @abstractmethod
    def send(self):
        pass
