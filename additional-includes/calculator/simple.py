__all__ = ['add', 'minus', 'multiply', 'devide']

def add(left, right):
    return left + right

def minus(left, right):
    return left - right

def multiply(left, right):
    return left * right

def devide(numerator, denominator):
    if denominator == 0:
        print ("Invalid denominator, current value is 0")
        return "N/A"
    else:
        return numerator/denominator