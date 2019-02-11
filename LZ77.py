import bitarray as bitarray
import math

def readFile(fileName):
    data = bitarray.bitarray(endian="big")
    with open(fileName, "rb") as file:
        data.fromfile(file)
    return data

def compress(fileName, ws, ls): #ws is window size, ls is lookahead buffer size
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
            tupleChar = data[-1] #make sure the last tuple has the last character as its additional bit
            charCopy = charCopy - 1

        else:
            tupleChar = data[currentIndex]
            currentIndex = currentIndex + 1

def match(data, currentIndex, ws, ls):
    found = False #if this becomes true, then a match in the window has been found

    endOfLB = min(len(data) - 1, currentIndex + ls) #this is to find the last possible index given the current index and the look-ahead size
    startIndex = max(0, (currentIndex - ws)) #either we start at the beginning or depending on window size
    distanceBack = 0 #how many characters you go back (d)
    charCopy = 0 #how many characters you copy (l)
    foundIndex = -1 #initializing foundIndex


    for x in range(endOfLB, currentIndex - 1, -1):
        subText = data[currentIndex:x + 1]
        subLength = len(subText)
        for j in range(startIndex, currentIndex):
            if((j + subLength)>currentIndex):
                continue
            potentialMatch = data[j:j + subLength]

            if(potentialMatch == subText):
                found = True
                charCopy = subLength
                distanceBack = currentIndex - j
        if(found):
            return(distanceBack, charCopy)

    return(0,0)
                
            
