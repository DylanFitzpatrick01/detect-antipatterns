def main():
    choice = input("Press 1 to add, 2 to sub, 3 to div, 4 to mul, 5 for exponential, 6 for mul by mul by 10 to chosen power, 7 for bigger, 8 for root" )
    num1 = float(input("1st number: "))
    num2 = float(input("2nd number: "))

    if choice == "1":
        add(num1, num2)
    elif choice == "2":
        sub(num1, num2)
    elif choice == "3":
        mul(num1, num2)
    elif choice == "4":
        div(num1, num2)
    elif choice == "5":
        exp(num1, num2)
    elif choice == "6":
        ten(num1, num2)
    elif choice == "7":
        bigger(num1, num2)
    elif choice == "8":
        root(num1, num2)
    else:
        print("Error, choice invalid!")

def add(x,y):
    return x+y

def sub(x, y):
    return x-y

def mul(x, y):
    return x * y

def div(x, y):
    return x/y

def exp(x, y):
    return x**y

def ten(x, y):
    return (x * (10**y))

def bigger(x, y):
    return x if x > y else y

def root(x, y):       
    return x**(1 / y)               

if __name__ == "__main__":
    main()
