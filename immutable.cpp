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

// So what's wrong here? 

// We have a concept called "immutable objects" which basically means that all of the state inside the object 
// is const (another way of saying that it cannot change after the object is created).

// Immutable objects are inherently thread safe as no one can write to any of the members, so its safe to have
// concurrent readers, even without locks/mutexes.

// However, it's easy to forget to mark one member as const, therefore making the object not immuatable.

int main()
{
    auto contactRecord = Contact{ "Joe Blogs", "123 Fake Street", "Europe/Dublin", true, "2000/01/01" };

    //contactRecord.name = "Steve";             // Doesnt compile as name is a const member. 

    contactRecord.dateOfBirth = "1999/12/25";   // Uh-oh, this object isnt immutable after all!

}

// We should be able to detect when something "looks like" it was intended to be immutable (nearly all the 
// members are const), but we then have one member that isnt const.

// This isnt a hard rule as we cannot fully know the intent of the programmer. But, it is a suspicous 
// pattern and we can build a hueristic around it, and provide a warning. 

// "Are you sure you want just this one member you're adding to be non const? The object is no longer immutable."
