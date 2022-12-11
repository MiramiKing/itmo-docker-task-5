"""Test module"""


def inc(value):
    """Mock function"""
    return value + 1


def test_1():
    """Test 3+1"""
    assert inc(3) == 4


def test_2():
    """Test 4+1"""
    assert inc(4) == 5


def test_3():
    """Test 0+1"""
    assert inc(0) == 1
