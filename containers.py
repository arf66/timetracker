from constants import DATABASE, DEBUG

class UIContainers:
    _instance = {}

    def __new__(cls, username=None):
        if username is not None:
            if username not in cls._instance:
                cls._instance[username] = super(UIContainers, cls).__new__(cls)
                cls._instance[username].containers = []
                cls._instance[username].containernames = []
            return cls._instance[username]

    def init(cls, username=None):
        if username is not None and username in cls._instance:
            cls._instance[username].containers = []
            cls._instance[username].containernames = []

    def add(self, name, uiel, username=None):
        if username is not None:
            self = self._instance.get(username, None)
            if self is None:
                return
        if name not in self.containernames:
            self.containernames.append(name)
            self.containers.append(uiel)

    def get(self, name, username=None):
        if username is not None:
            self = self._instance.get(username, None)
            if self is None:
                return None
        for ix, n in enumerate(self.containernames):
            if n==name:
                return self.containers[ix]
        return None

    def get_all(self, username=None):
        if username is not None:
            self = self._instance.get(username, None)
            if self is None:
                return []
        return self.containers


