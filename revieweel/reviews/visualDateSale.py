class VisualDateSale(object):
    def __init__(self, year, monthSale):
        self.year = year
        self.monthSale = monthSale

    def print_visualDateSale(self):
        print('%s: %s' % (self.year, self.monthSale))
