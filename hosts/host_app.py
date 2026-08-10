import threading
from abc import ABC, abstractmethod


class HostApp(ABC):

    @abstractmethod
    def run(self):
        pass

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
