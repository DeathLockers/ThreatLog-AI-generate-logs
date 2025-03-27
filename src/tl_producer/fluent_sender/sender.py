

class FluentSender:
    def __init__(self, config):
        self.config = config
        self.fluent = Fluent(config['host'], config['port'], config['tag'])

    def send(self):
        self.fluent.send(self.config['message'])

    def start(self):
        self.fluent.start()

    def stop(self):
        self.fluent.stop()