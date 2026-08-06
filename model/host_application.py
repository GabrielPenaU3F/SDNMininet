import threading


class HostApplication:

    def __init__(self, sender, receiver):
        self.sender = sender
        self.receiver = receiver

    def run(self):

        sender_thread = threading.Thread(
            target=self.sender.run
        )

        receiver_thread = threading.Thread(
            target=self.receiver.run
        )


        sender_thread.start()
        receiver_thread.start()

        sender_thread.join()
        receiver_thread.join()
