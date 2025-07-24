#!/usr/bin/env python3
"""
Test Python Project for Phase 2 Integration Testing

This is a simple Python project to test the Phase 2 integration
of virtual environment management and Git operations.
"""

def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}! Welcome to Phase 2 testing."


def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers."""
    return a + b


def main():
    """Main function to demonstrate the test project."""
    print(greet("Windsurf Framework"))
    print(f"2 + 3 = {calculate_sum(2, 3)}")
    print("Phase 2 integration test project is working!")


if __name__ == "__main__":
    main()
