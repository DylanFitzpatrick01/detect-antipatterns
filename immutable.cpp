#include <iostream>
#include <string>

struct Contact
{
    const std::string name;
    const std::string address;
    const std::string timezone;
    const bool isActive;
    std::string dateOfBirth;
};



int main()
{
    auto contactRecord = Contact{ "Joe Blogs", "123 Fake Street", "Europe/Dublin", true, "2000/01/01" };


    contactRecord.dateOfBirth = "1999/12/25";   

}


