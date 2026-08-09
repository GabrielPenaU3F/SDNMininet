from errors import NetworkError


class Host:

    def __init__(self, mn_host):
        self.mn_host = mn_host
        self._active = False

    @property
    def is_active(self):
        return self._active

    @property
    def name(self):
        return self.mn_host.name

    @property
    def ip(self):
        return self.mn_host.IP()

    def _start(self):
        self._active = True

    def _stop(self):
        self._active = False

    def cmd(self, *args, **kwargs):
        if not self.is_active:
            raise NetworkError(f'Host {self.name} is not active')
        return self.mn_host.cmd(*args, **kwargs)

    def popen(self, *args, **kwargs):
        if not self.is_active:
            raise NetworkError(f'Host {self.name} is not active')
        return self.mn_host.popen(*args, **kwargs)
