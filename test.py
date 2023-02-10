from calculator import add, sub, mul, bigger, ten, root, exp, div

def test_add():
    assert add(10,10) == 20
    
def test_sub():
    assert sub(20,10) == 10

def test_ten():
    assert ten(5, 1) == 50
    
def test_bigger():
    assert bigger(300, 10) == 300
    assert bigger(-5, -1) == -1
    assert bigger(10, 10) == 10

def test_mul():
    assert mul(10,20) == 200

def test_root():
    assert root(4,2) == 2

def test_exp():
    assert exp(10,2) == 100

def test_div():
    assert div(20,10) == 2