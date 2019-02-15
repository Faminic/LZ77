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
    ls = ols(ls) #making sure its not 0 or 1
    wBitSize = math.ceil(math.log((ws+1),2)) # amount of bits needed for window size (d)
    lBitSize = math.ceil(math.log((ls+1),2)) # amount of bits needed for look-ahead buffer (l), the character will always be 8 bits
    data = readFile(input_fileName).to01()
    size = len(data)

    result = bitarray() #will be a big string to be put into the bitarray at the end
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
        result = result + bitarray(("{:0" + str(wBitSize) + "b}").format(distanceBack)) + (("{0:0" + str(lBitSize) + "b}").format(charCopy)) + tupleChar

    resultBitArray = result
    resultBitArray.fill() #makes it so everything that number is a multiple of 8

    end = time.time()
    print("Percentage Compressed: " + str(100.0-((len(resultBitArray)/size)*100)) + "%")
    print("Compression Ratio: " + str(len(data)/len(resultBitArray.to01())))
    print("Time it took to compress: " + str(end-start))

    with open(output_fileName, "wb") as output_file:
        resultBitArray.tofile(output_file)



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

####
#Everything below are just test functions, please ignore :D
###

def test_file_size():

    for i in range(0,7):
        input_file_name = "test_files/file_size/test" + str(i+1) + ".txt"
        output_file_name = "test_files/file_size/binaryresult" + str(i+1) + ".bin"
        decompress_file_name = "test_files/file_size/decompressresult" + str(i+1) + ".txt"
        print("Compress: " + str(i+1))
        compress(input_file_name, output_file_name, 63, 50)
        print("")
        print("Decompress: " + str(i+1))
        decompress(output_file_name, decompress_file_name)
        print("")
        data1 = readFile(input_file_name).to01()
        data2 = readFile(decompress_file_name).to01()
        print("")
        if(data1 == data2):
            print("Case " + str(i+1) + " is correct")
        else:
            print("Case " + str(i+1) + " did not decompress properly")
        print("")
        
    print("Test is complete!")

def test_file_type():
    file_formats = ["bmp", "doc", "jpg", "MOV", "pdf", "png", "pptx", "txt", "wav"]

    for i in range(len(file_formats)):
        fileFormat = file_formats[i]
        print(fileFormat)
        input_file_name = "test_files/file_type/test." + fileFormat
        output_file_name = "test_files/file_type/binaryresult" + fileFormat + ".bin"
        decompress_file_name = "test_files/file_type/decompressresult." + fileFormat
        print("Compress: ")
        compress(input_file_name, output_file_name, 16383, 50)
        print("")
        print("Decompress: ")
        decompress(output_file_name, decompress_file_name)
        print("")
        data1 = readFile(input_file_name).to01()
        data2 = readFile(decompress_file_name).to01()
        if(data1 == data2):
            print("Case " + str(i+1) + " is correct")
        else:
            print("Case " + str(i+1) + " did not decompress properly")
        print("")
        print("")
    print("Test is complete!")

def test_window_size():
    print("Test for different window sizes - on 100KB text file and rainbow image bmp file with lookahead size 50")
    print("")
    print("")

    window_lengths = [15, 255, 4095, 16383, 65535, 262143]
    
    print("Text File Results")
    print("")
    print("")
    for i in range(len(window_lengths)):
        ws = window_lengths[i]
        print("Window Length: " + str(ws))
        print("")
        input_file_name = "test_files/window_length/wl_small.txt"
        output_file_name = "test_files/window_length/binaryresult" + str(ws) + ".bin"
        decompress_file_name = "test_files/window_length/decompressresult" + str(ws) + ".txt"
        compress(input_file_name, output_file_name, ws, 50)
        decompress(output_file_name, decompress_file_name)
        print("")
        data1 = readFile(input_file_name).to01()
        data2 = readFile(decompress_file_name).to01()
        if(data1 == data2):
            print("Case " + str(i+1) + " is correct")
        else:
            print("Case " + str(i+1) + " did not decompress properly")
        print("")
        print("")

##    print("BMP File Results")
##    print("")
##    print("")
##    for i in range(len(window_lengths)):
##        ws = window_lengths[i]
##        print("Window Length: " + str(ws))
##        print("")
##        input_file_name = "test_files/window_length/test.bmp"
##        output_file_name = "test_files/window_length/binaryresultBMP" + str(ws) + ".bin"
##        decompress_file_name = "test_files/window_length/decompressresultBMP" + str(ws) + ".bmp"
##        compress(input_file_name, output_file_name, ws, 50)
##        decompress(output_file_name, decompress_file_name)
##        print("")
##        data1 = readFile(input_file_name).to01()
##        data2 = readFile(decompress_file_name).to01()
##        if(data1 == data2):
##            print("Case " + str(i+1) + " is correct")
##        else:
##            print("Case " + str(i+1) + " did not decompress properly")
##        print("")
##        print("")
##    print("Test 1 is complete!")
##    print("")
##    print("")
##    print("")
##    print("")


def test_look_ahead():
    print("Test for different look ahead sizes sizes - on 100KB text file and rainbow image bmp file with window size 4095")
    print("")
    print("")

    window_lengths = [255, 511] #is actually look ahead sizes, just variable name is same
    
    print("Text File Results")
    print("")
    print("")
    for i in range(len(window_lengths)):
        ws = window_lengths[i]
        print("Look-ahead Length: " + str(ws))
        print("")
        input_file_name = "test_files/look_ahead_length/la_normal.txt"
        output_file_name = "test_files/look_ahead_length/binaryresult" + str(ws) + ".bin"
        decompress_file_name = "test_files/look_ahead_length/decompressresult" + str(ws) + ".txt"
        compress(input_file_name, output_file_name, 4095, ws)
        decompress(output_file_name, decompress_file_name)
        print("")
        data1 = readFile(input_file_name).to01()
        data2 = readFile(decompress_file_name).to01()
        if(data1 == data2):
            print("Case " + str(i+1) + " is correct")
        else:
            print("Case " + str(i+1) + " did not decompress properly")
        print("")
        print("")

    print("BMP File Results")
    print("")
    print("")
    for i in range(len(window_lengths)):
        ws = window_lengths[i]
        print("Look-ahead Length: " + str(ws))
        print("")
        input_file_name = "test_files/look_ahead_length/la_rainbow.bmp"
        output_file_name = "test_files/look_ahead_length/binaryresultBMP" + str(ws) + ".bin"
        decompress_file_name = "test_files/look_ahead_length/decompressresultBMP" + str(ws) + ".bmp"
        compress(input_file_name, output_file_name, 4095, ws)
        decompress(output_file_name, decompress_file_name)
        print("")
        data1 = readFile(input_file_name).to01()
        data2 = readFile(decompress_file_name).to01()
        if(data1 == data2):
            print("Case " + str(i+1) + " is correct")
        else:
            print("Case " + str(i+1) + " did not decompress properly")
        print("")
        print("")
    print("Test is complete!")

def ols(ls): #optimise look ahead size
    if(ls <= 1):
        ls = 2
    elif(float(math.log((ls+1),2)).is_integer()):
        ls = ls - 1
    return ls

def random_test():
    window_lengths = ["test2.txt", "test3.txt", "test4.txt"]
    for i in range(len(window_lengths)):
        ws = window_lengths[i]
        print(str(window_lengths[i]))
        print("")
        input_file_name = str(window_lengths[i])
        output_file_name = "binaryresult" + str(i+1) + ".bin"
        decompress_file_name = "decompressresult" + str(ws) + ".bmp"
        compress(input_file_name, output_file_name, 16383, 50)
        print("")
    
    
        
    
    
            
