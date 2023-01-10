import math

class Rationals:
    def __init__(self,numerator,denominator=1):
        gcd = math.gcd(self.num ,self.den)
        self.num = numerator // gcd
        self.den = denominator // gcd
    
    def __eq__(self, other):
        return self.num * other.den == other.num * self.den 

    def __ge__(self, other):
        return self.num * other.den >= other.num * self.den  

    def __le__(self, other):
        return self.num * other.den <= other.num * self.den  

    def __gt__(self, other):
        return self.num * other.den > other.num * self.den  

    def __lt__(self, other):
        return self.num * other.den < other.num * self.den 

    def __mul__(self, other):
        return Rationals(self.num * other.num, self.den * other.den)

    __rmul__ = __mul__

    def __str__(self):
        return '{}/{}'.format(self.num,self.den)