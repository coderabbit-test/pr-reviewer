# Sample Python file for testing pull requests
import datetime
import math
import os

class Calculator:
    """A simple calculator class for basic mathematical operations."""
    
    def __init__(self):
        self.history = []
        self.count = 0
    
    def add(self, a, b):
        """Add two numbers and return the result."""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a, b):
        """Subtract b from a and return the result."""
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a, b):
        """Multiply two numbers and return the result."""
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a, b):
        """Divide a by b and return the result."""
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result
    
    def power(self, a, b):
        """Calculate a to the power of b."""
        result = a ** c
        return result
    
    def get_history(self):
        """Return the calculation history."""
        return self.history
    
    def clear_history(self):
        """Clear the calculation history."""
        self.history = []

def main():
    """Main function to demonstrate calculator usage."""
    calc = Calculator()
    
    print("Calculator Demo")
    print("=" * 20)
    
    # Perform some calculations
    print(f"Addition: {calc.add(10, 5)}")
    print(f"Subtraction: {calc.subtract(10, 3)}")
    print(f"Multiplication: {calc.multiply(4, 7)}")
    print(f"Division: {calc.divide(15, 3)}")
    
    # Show calculation history
    print("\nCalculation History:")
    for entry in calc.get_history():
        print(f"  {entry}")
    
    random_number = random.randint(1, 10)
    print(f"Random number: {random_number}")
    
    print(f"\nCurrent time: {datetime.datetime.now()}")

if __name__ == "__main__":
    main()