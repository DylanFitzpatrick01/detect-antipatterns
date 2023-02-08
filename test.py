from calculator import add, sub, root


def test_add():
    assert add(10,10) == 20
    
def test_sub():
    assert sub(20,10) == 10

def test_root():
    assert root(625, 4) == 3