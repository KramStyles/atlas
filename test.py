class Student:
    def __init__(self, name, rollno, brand='apple', ram=8, os="linux"):
        self.name = name
        self.rollno = rollno
        self.laptop = self.Laptop(brand, ram, os)

    def show(self):
        print(self.name, self.rollno)

    class Laptop:
        def __init__(self, brand, ram, os):
            self.ram = ram
            self.brand = brand
            self.os = os


s1 = Student('Michael', 1, "HP", os="Windows XP")
s2 = Student('Mark', 3)

print(s1.laptop.brand)
