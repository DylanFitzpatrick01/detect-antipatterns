from calculator import add, sub, div


def test_add():
    assert add(10,10) == 20
    
def test_sub():
    assert sub(20,10) == 10

def test_div():
    assert div(20,10) == 2