from calculator import add, sub, mul


def test_add():
    assert add(10,10) == 20
    
def test_sub():
    assert sub(20,10) == 10

def test_mul():
    assert mul(10,20) == 30