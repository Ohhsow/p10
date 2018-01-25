class Human():
    def __init__(self, age, name):
        self.name = name
        self.age = age


    def print_info(self):
        print(self.name, self.age)




john = Human(22, "John")


anna = Human(18, "Anna")


print(john.name, john.age)
print(anna.name, anna.age)

john.print_info()
anna .print_info()

class MyObject():
    class_atribute = 8
    def __init__(self):
        self.atribute = 42

    def return_atr(self):
        print (self.atribute)

    @staticmethod
    def static_metod():
        print (MyObject.class_atribute)

if __name__ == "__main__":
    MyObject.static_metod()
    obj = MyObject()
    obj.return_atr()
    obj.static_metod()


class Ractangle():
    def __init__(self, side_a, side_b):
        self.side_a = side_a
        self.side_b = side_b

    def __repr__(self):
        return "rectangle(%.1f, %.1f)" % (self.side_a, self.side_b)


class Circle():
    def __init__(self, radius):
        self.radius = radius

    def __repr__(self):
        return "radius(%.1f)" % (self.radius)

    @classmethod
    def from_retangle(cls, retangle):
        radius = (retangle.side_a ** 2 + retangle.side_b ** 2) ** 0.5 / 2
        return cls(radius)

def main():
    retangle = Ractangle(3, 4)
    print (retangle)

    first_circle = Circle (1)
    print (first_circle)

    seconf_circle = Circle.from_retangle(retangle)
    print (seconf_circle)


a = main()
print(a)