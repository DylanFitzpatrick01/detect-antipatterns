import re
file_path1 = r"deadlock code"
file_path2 = r"test1"

ordered_list = []

with open(file_path1, "r") as f:
    contents = f.read()
    searchFor1 = "acquire"
    seachFor2 = "release"


    count = contents.count(searchFor1)
    count2 = contents.count(seachFor2)
    
    if count == count2:
     print("Even number of {seachFor1} and {seachFor2} found")

    else:
        print ("Error uneven number of {seachFor1} and {seachFor2} found")
        
        
    with open(file_path1, "r") as f:
  
        for line in f:
            if searchFor1 in line:
                ordered_list.append(searchFor1)
            elif seachFor2 in line:
                ordered_list.append(seachFor2)
                
    print(ordered_list)
    
    prev_index = None

    for i in range(1,len(ordered_list)):
        if ordered_list[i] == ordered_list[i-1]:
            if ordered_list[i] == searchFor1:
                print("error2" , searchFor1," is repeated twice")
            
            
                
                

        


   
