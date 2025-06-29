class Message:

    def __init__(self, author, text):
        self.author = author
        self.text = text

class DialogManager:

    def __init__(self):
        self.messages: list[Message] = []

    def add_message(self, message: Message):
        self.messages.append(message)
