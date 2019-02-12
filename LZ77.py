from bitarray import *
import math
import time

def readFile(fileName):
    data = bitarray(endian="big")
    with open(fileName, "rb") as file:
        data.fromfile(file)
    return data



def match(data, currentIndex, ws, ls):
    found = False #if this becomes true, then a match in the window has been found

    endOfLB = min(len(data) - 1, currentIndex + ls) #this is to find the last possible index given the current index and the look-ahead size
    startIndex = max(0, (currentIndex - ws)) #either we start at the beginning or depending on window size
    distanceBack = 0 #how many characters you go back (d)
    charCopy = 0 #how many characters you copy (l)
    foundIndex = -1 #initializing foundIndex


    for x in range(endOfLB, currentIndex - 1, -1):
        subText = data[currentIndex:x + 1]

        foundIndex = data.rfind(subText, startIndex, currentIndex)

        if(foundIndex >=0):
            found = True
            charCopy = len(subText)
            distanceBack = currentIndex - foundIndex
            break
        
    if(found):
        return(distanceBack, charCopy)

    return(0,0)



def compress(input_fileName, output_fileName, ws, ls): #ws is window size, ls is lookahead buffer size
    start = time.time()
    wBitSize = math.ceil(math.log((ws+1),2)) # amount of bits needed for window size (d)
    lBitSize = math.ceil(math.log((ls+1),2)) # amount of bits needed for look-ahead buffer (l), the character will always be 8 bits
    data = readFile(input_fileName).to01()
    size = len(data)

    result = "" #will be a big string to be put into the bitarray at the end
    result = result + (("{:08b}").format(wBitSize)) + (("{:08b}").format(lBitSize)) #metadata to pass wBitSize and lBitSize to the decoder
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
        result = result + (("{:0" + str(wBitSize) + "b}").format(distanceBack)) + (("{0:0" + str(lBitSize) + "b}").format(charCopy)) + tupleChar

    resultBitArray = bitarray(result)
    resultBitArray.fill() #makes it so everything that number is a multiple of 8

    print("Percentage Compressed: " + str(100.0-((len(resultBitArray)/size)*100)) + "%")
    end = time.time()
    print("Time it took to compress: " + str(end-start))

    with open(output_fileName, "wb") as output_file:
        resultBitArray.tofile(output_file)
        print("done") #just to check actual size of a file



def decompress(input_fileName, output_fileName):
    start = time.time()
    data = readFile(input_fileName).to01()
    wBitSize = int(data[0:8],2)
    lBitSize = int(data[8:16],2)
    data = data[16:]

    tupleSize = wBitSize + lBitSize + 1 #is the size of each tuple in bits
    result = "" #will be a big string to be put into the bitarray at the end
    currentPointer = 0 #index of where we are in result
    relativePointer = 0 #index of pointer that goes back

    while(len(data) >= tupleSize):
        distanceBack = int(data[0:wBitSize],2)
        charCopy = int(data[wBitSize:wBitSize + lBitSize], 2)
        tupleChar = data[wBitSize + lBitSize]
        data = data[tupleSize:]

        if(distanceBack == 0 and charCopy == 0):
            result = result + tupleChar
            currentPointer = currentPointer + 1
        else:
            relativePointer = currentPointer - distanceBack
            copiedChar = result[relativePointer:relativePointer + charCopy]
            result = result + copiedChar + tupleChar
            currentPointer = currentPointer + charCopy + 1
            
    resultBitArray = bitarray(result)
    end = time.time()
    print("Time it took to decompress: " + str(end-start))

    with open(output_fileName, "wb+") as output_file:
        resultBitArray.tofile(output_file)
        print("done") #just to check actual size of a file
                
            
