class Host:

    def __init__(self, mn_host):
        self.mn_host = mn_host
        self.process = None
        self.app = None

    #TODO: this should terminate the running process
    def _stop(self):
        pass

    @property
    def name(self):
        return self.mn_host.name

    @property
    def ip(self):
        return self.mn_host.IP()

    def cmd(self, *args, **kwargs):
        return self.mn_host.cmd(*args, **kwargs)

    def popen(self, *args, **kwargs):
        self.process = self.mn_host.popen(*args, **kwargs)
        return self.process

    def launch_app(self, app):
        if self.app is not None:
            raise RuntimeError(f'Host {self.name} already has an application running')

        self.app = app
        self.process = self.popen(app.command())