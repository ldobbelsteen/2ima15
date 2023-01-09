class Rationals:
    def __init__(self,numerator,denominator=1):
        self.num = numerator
        self.den = denominator
    
    def __eq__(self, other):
        self.num * other.den == other.num * self.den 

    def __ge__(self, other):
        self.num * other.den >= other.num * self.den  

    def __le__(self, other):
        self.num * other.den <= other.num * self.den  

    def __gt__(self, other):
        self.num * other.den > other.num * self.den  

    def __lt__(self, other):
        self.num * other.den < other.num * self.den 
