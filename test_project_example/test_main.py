"""
Tests for the main module.
"""

import pytest
from main import greet, calculate_sum


def test_greet():
    """Test the greet function."""
    result = greet("World")
    assert "Hello, World!" in result
    assert "Phase 2 testing" in result


def test_calculate_sum():
    """Test the calculate_sum function."""
    assert calculate_sum(2, 3) == 5
    assert calculate_sum(0, 0) == 0
    assert calculate_sum(-1, 1) == 0
    assert calculate_sum(10, -5) == 5


def test_greet_empty_name():
    """Test greet with empty name."""
    result = greet("")
    assert "Hello, !" in result


def test_calculate_sum_large_numbers():
    """Test calculate_sum with large numbers."""
    assert calculate_sum(1000000, 2000000) == 3000000
