from calculator import add, sub, mul, bigger



def test_add():
    assert add(10,10) == 20
    
def test_sub():
    assert sub(20,10) == 10
    
def test_bigger():
    assert bigger(300, 10) == 300
    assert bigger(-5, -1) == -1
    assert bigger(10, 10) == 10

def test_mul():
    assert mul(10,20) == 200
