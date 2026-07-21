import threading


class Host:

    def __init__(self, sender, receiver):
        self.sender = sender
        self.receiver = receiver

    def run(self):

        receiver_thread = threading.Thread(
            target=self.receiver.begin
        )

        sender_thread = threading.Thread(
            target=self.sender.begin
        )

        receiver_thread.start()
        sender_thread.start()

        receiver_thread.join()
        sender_thread.join()
