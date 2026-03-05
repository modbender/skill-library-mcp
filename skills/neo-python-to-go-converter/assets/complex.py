def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def sum_range(start: int, end: int) -> int:
    total = 0
    for i in range(start, end):
        total += i
    return total

def first_even() -> int:
    nums = [1, 3, 5, 8, 10]
    for x in nums:
        if x % 2 == 0:
            return x
    return -1

def assert_demo(x: int):
    assert x > 0, "x must be positive"
    print("x is positive:", x)

def main():
    print("Factorial 5:", factorial(5))
    print("Sum 1..9:", sum_range(1, 10))
    print("First even:", first_even())
    assert_demo(42)
