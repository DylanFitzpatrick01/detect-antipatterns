void a();
void b();
void c();
void d();
void e();

void a()
{
    b();
}

void b()
{
    c();
}

void c()
{
    d();
}

void d()
{
    if(true)
    {
        c();
    } else
    {
        e();
    }
}

void e()
{

}

int main()
{
    a();

    return 0;
}