from csp import *

def generateMockUniversity():
    
    print("generateMockUniversity() running...\n")

    my_univ = generateUniv("ESILV")
    print(my_univ, "\n")

    print("Trying to access room with index 3: ")
    print(my_univ.rooms[3], "\n")
    print("Trying to access teacher with index 5: ")
    print(my_univ.teachers[5], "\n")
    print("Trying to access promotion with index 1: ")
    print(my_univ.promotions[1], "\n")
    print("Trying to access A2's subject list: ")
    for sub in my_univ.promotions[1].subjects:
        print(sub)