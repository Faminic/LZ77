import bitarray as bitarray
import math

def readFile(fileName):
    data = bitarray.bitarray(endian="big") #will hold the file as a set of bits
    with open(fileName, "rb") as file:
        data.fromfile(file)
    return data

def match(data, currentIndex, ws, ls): #data is the bitarray containing the file to be compressed, currentIndex is the location of the current pointer, ws is the window size, ls is the look-ahead buffer size
    found = False #if this becomes true, then a match in the window has been found

    endOfLB = min(len(data) - 1, currentIndex + ls) #this is to find the last possible index given the current index and the look-ahead size
    startIndex = max(0, (currentIndex - ws)) #either we start at the beginning or depending on window size
    distanceBack = 0 #how many characters you go back (d)
    charCopy = 0 #how many characters you copy (l)
    foundIndex = -1 #initializing foundIndex

    for x in range(currentIndex + 1, endOfLB + 2): #it is "currentIndex+1" since every possible subtext starts at currentIndex
                                                   #it is endOfLB + 2 because one "+1" since last one isnt included in range and one "+1" since last one isnt included in the slicing
        subText = data[currentIndex:x]
##
##        Think about instead of starting with smaller subtexts to going to bigger subtext, start at bigger subtexts.
##        May be more efficient for different input types
##        
        tempFoundIndex = data.rfind(subText, startIndex, currentIndex)

        if tempFoundIndex>=0:
            foundIndex = tempFoundIndex
            charCopy = len(subText)
            distanceBack = currentIndex - foundIndex

    if foundIndex >= 0:
        found = True #making found true since you have a match

    if found:
        return(distanceBack, charCopy)
    else:
        return(0,0)

def compress(fileName, ws, ls): #fileName is the name of file to be compressed, ws is the window size, ls is the look-ahead buffer size
    wBitSize = math.ceil(math.log((ws+1),2)) # amount of bits needed for window size (d)
    lBitSize = math.ceil(math.log((ls+1),2)) # amount of bits needed for look-ahead buffer (l), the character will always be 8 bits
    data = readFile(fileName)
    size = len(data) 
        
    result = bitarray.bitarray(endian="big") # will store all information about triple -> in the form (d,l,x) where x is a character

    currentIndex = 0 #location of current pointer

    while currentIndex < size:
        distanceBack, charCopy = match(data, currentIndex, ws, ls)
        currentIndex = currentIndex + charCopy
        if(currentIndex >= size):
            tupleChar = ""
        else:
            tupleChar = data[currentIndex] #this is the character at the end of the tuple
            currentIndex = currentIndex + 1

        
        
        
        

        
            
            
    
    
