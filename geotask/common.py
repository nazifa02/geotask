"""The common module contains common functions and classes used by the other modules.
"""

def hello_world():
    """Prints "Hello World!" to the console.
    """
    print("Hello World!")

def hello (name):
    """Prints "Hello {name}!" to console.

    Args:
       name (str): The name to print.
    """
    print(f"Hello {name}!")
    

def random_number():
    """Returns a random number between 0 and 1.

    Returns:
        float: A random number between 0 and 1.
    """
    import random
    return random.random()







