from constants import DATABASE, DEBUG

class UIContainers:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UIContainers, cls).__new__(cls)
            cls._instance.containers = []
            cls._instance.containernames = []            
        return cls._instance

    def init(cls):
        if cls._instance is not None:
            cls._instance.containers = []
            cls._instance.containernames = []            

    def add(self, name, uiel):
        if name not in self.containernames:
            self.containernames.append(name)
            self.containers.append(uiel)

    def get(self, name):
        for ix, n in enumerate(self.containernames):
            if n==name:
                return self.containers[ix]
        return None

    def get_all(self):
        return self.containers


