"""
author : Muhammad Emad
Date: 13/12/2024
Description: Creating a generator for numbers in Fibonacci sequence
"""


def fibonacci_sequence():
    num1 = 0
    num2 = 1
    while True:
        yield num1  # Generator
        num1, num2 = num2, num1 + num2



fib_gen = fibonacci_sequence()
for _ in range(20):
    print(next(fib_gen))
