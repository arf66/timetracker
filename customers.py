from constants import DB_STATUSES

class CustomersManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CustomersManager, cls).__new__(cls)
            cls._instance.customers = []
        return cls._instance

    def add(self, customername):
        if customername not in self.customers:
            self.customers.append(customername)

    def load(self, user, list):
        for s in DB_STATUSES:
            for el in list[user][s]:
                self.add(el['customer'])
    
    def get_all(self):
        return self.customers
        