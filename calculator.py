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
    '''
    print sum
    '''
    return x+y

def sub(x, y):
    '''
    print sub
    '''
    return x-y

def mul(x, y):
    '''
    print product
    '''
    return x * y

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
    print(x * (10**y))

def bigger(x, y):
    '''
    print the bigger number
    '''
    print(x if x > y else y)  

def root(x, y):
    '''
    print y-th root of x
    '''         
    print(x**(1 / y))               

if __name__ == "__main__":
    main()
