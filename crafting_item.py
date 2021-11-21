class CraftingItem(object):
    def __init__(self, name, quantity, station=None):
        self.name = name
        self.quantity = quantity
        self.station = station
        self.printname = "%s x%d" %(name, quantity)
    
    def get_name(self):
        return self.name
    def get_quantity(self):
        return self.quantity
    def get_station(self):
        return self.station
    def has_recipe(self):
        return self.station is not None