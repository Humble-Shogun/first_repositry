'''
m = [2,7,5]
n = [7,8,2,4]
o = [9,4]
print(list(map(lambda x,y,z:x+y+z,m,n,o)))

import functools
n = [7,8,2,4]
print(functools.reduce(lambda x,y:x+y,n))


import functools
li = ["sindhu","r","pai"]
print(functools.reduce(lambda x,y:x+y[0],li,""))
'''
k = [2,4,5,6,8,99,32]
#print(list(filter(lambda x:x%2==0,k)))

#sindhurpai@pes.edu

#2 Generate a set of numbers from given list of numbers which are divisible by 3 and 5

r = [15,35,45,36,46]
print(set(filter(lambda x:x%3==0 and x%5==0,r)))


#3 convert all the elements of a list into numbers and store it in a list

#4 create a list char for every string in a list

#5 concatenate the elements of alist and create a new list
















