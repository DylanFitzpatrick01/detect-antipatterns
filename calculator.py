def main():
    choice = input("Press 1 to add, 2 to sub, 3 to div, 4 to mul, 5 for exponential, 6 for mul by mul by 10 to chosen power, 7 for bigger" )
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
    else:
        bigger(num1, num2)

def add(x, y):
    '''
    print sum
    '''
    print(x+y)

def sub(x, y):
    '''
    print sub
    '''
    print("hello world")

def mul(x, y):
    '''
    print product
    '''
    print("hello world")

def div(x, y):
    '''
    print divison
    '''
    print("hello world")

def exp(x, y):
    '''
    print x^y (use **)
    '''
    print("hello world")

def ten(x, y):
    '''
    print x*10^y (use **)
    '''
    print("hello world")

def bigger(x, y):
    '''
    print the bigger number
    '''
    print("hello world")                        

if __name__ == "__main__":
    main()
