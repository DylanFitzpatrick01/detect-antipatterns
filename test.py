from calculator import add, sub, ten


def test_add():
    assert add(10,10) == 20
    
def test_sub():
    assert sub(20,10) == 10

def test_ten():
    assert ten(5, 1) == 50
