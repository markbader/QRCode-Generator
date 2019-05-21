import tkinter
import sys
import json

def main(string, correctionLevel):
    root = tkinter.Tk()
    root.geometry('400x400')
    root.resizable(False,False)
    canvas = tkinter.Canvas(root,  bg='white')
    canvas.pack(fill='both', expand=1)
    createQRCodeIn(canvas, string, correctionLevel)
    root.mainloop()
    return 0

def createQRCodeIn(canvas, string, correctionLevel):
    qrCode = createQRCode(string, correctionLevel)
    canvas.create_image(200,200, image=qrCode)
    canvas.image = qrCode
    

def createQRCode(string, correctionLevel):
    if isNumeric(string):
        version = chooseVersion(string, '0001', correctionLevel)
        encodedString = numericEncoding(string, version, correctionLevel)
    elif isAlphanumeric(string):
        version = chooseVersion(string, '0010', correctionLevel)
        encodedString = alphanumericEncoding(string, version, correctionLevel)
    elif isByte(string):
        version = chooseVersion(string, '0100', correctionLevel)
        encodedString = byteEncoding(string, version, correctionLevel)
    elif isKanji(string):
        version = chooseVersion(string, '1000', correctionLevel)
        encodedString = kanjiEncoding(string, version, correctionLevel)
    else:
        print('character set is not supported')
        sys.exit(1)
    data = divideInBlocks(version, correctionLevel, encodedString)
    qrCode = drawQRCode(data, version, correctionLevel)
    return qrCode

def drawQRCode(data, version, correctionLevel):
    size = (((version - 1) * 4) + 21)
    image = [[42 for i in range(size)] for j in range(size)]
    addToImage(image, [0, 0], [[10,10,10,10,10,10,10,11],[10,11,11,11,11,11,10,11],[10,11,10,10,10,11,10,11],[10,11,10,10,10,11,10,11],[10,11,10,10,10,11,10,11],[10,11,11,11,11,11,10,11],[10,10,10,10,10,10,10,11],[11,11,11,11,11,11,11,11]])
    addToImage(image, [0,(((version-1)* 4)+ 21) - 8], [[11,10,10,10,10,10,10,10],[11,10,11,11,11,11,11,10],[11,10,11,10,10,10,11,10],[11,10,11,10,10,10,11,10],[11,10,11,10,10,10,11,10],[11,10,11,11,11,11,11,10],[11,10,10,10,10,10,10,10],[11,11,11,11,11,11,11,11]])
    addToImage(image, [(((version-1)* 4)+ 21) - 8, 0], [[11,11,11,11,11,11,11,11],[10,10,10,10,10,10,10,11],[10,11,11,11,11,11,10,11],[10,11,10,10,10,11,10,11],[10,11,10,10,10,11,10,11],[10,11,10,10,10,11,10,11],[10,11,11,11,11,11,10,11],[10,10,10,10,10,10,10,11]])
    insertAlignmentPattern(image, version)
    addToImage(image, [8,6], ([[10],[11]]*(size//2))[:-15])
    addToImage(image, [6,8], [([10,11]*(size//2))[:-15]])
    addToImage(image, [0,8], [[2],[2],[2],[2],[2],[2]])#format information
    addToImage(image, [size-8,8], [[2],[2],[2],[2],[2],[2],[2],[2]])
    addToImage(image, [7,7], [[11,2],[2,2]])
    addToImage(image, [8,0], [[2,2,2,2,2,2]])
    addToImage(image, [8, size-8], [[10,2,2,2,2,2,2,2]])
    if version >= 7: #version information
        addToImage(image, [0,size-11], [[2,2,2],[2,2,2],[2,2,2],[2,2,2],[2,2,2],[2,2,2]])
        addToImage(image, [size-11,0], [[2,2,2,2,2,2],[2,2,2,2,2,2],[2,2,2,2,2,2]])
    placeData(image, data)
    image = dataMasking(image)
    img = tkinter.PhotoImage(width=size, height=size)
    for i in range(len(image)):
        for j in range(len(image)):
            if image[i][j] == 1:
                img.put('#ffffff', (i,j))
            elif image[i][j] == 0:
                img.put('#000000', (i,j))
            elif image[i][j] == 11:
                img.put('#ffffff', (i,j))
            elif image[i][j] == 10:
                img.put('#000000', (i,j))
            elif image[i][j] == 2:
                img.put('#0000ff', (i,j))
            else:
                img.put('#555555', (i,j))
    img = img.zoom(400//size, 400//size)
    return img

def dataMasking(image):
    masks = []
    masks.append(mask(image, lambda row,column: (row+column)%2 == 0))
    masks.append(mask(image, lambda row,column: (row)%2 == 0))
    masks.append(mask(image, lambda row,column: (column)%3 == 0))
    masks.append(mask(image, lambda row,column: (row+column)%3 == 0))
    masks.append(mask(image, lambda row,column: (row//2+column//3)%2 == 0))
    masks.append(mask(image, lambda row,column: (row*column)%2+(row+column)%3 == 0))
    masks.append(mask(image, lambda row,column: ((row*column)%2+(row*column)%3)%2 == 0))
    masks.append(mask(image, lambda row,column: ((row+column)%2+(row*column)%3)%2 == 0))
    penalties = []
    for i in range(len(masks)):
        penalty = 0
        penalty += rule1(masks[i])
        penalty += rule2(masks[i])
        penalty += rule3(masks[i])
        penalty += rule4(masks[i])
        penalties.append(penalty)
    return masks[penalties.index(min(penalties))]

def rule1(image):
    penalty = 0
    aktList = []
    for i in range(len(image)):
        for j in range(len(image)):
            if image[i][j] == 1:
                pass
    return 1

def rule2(image):
    return 1

def rule3(image):
    return 1

def rule4(image):
    return 1

def deepCopy(listOfLists):
    return [list(listOfLists[i]) for i in range(len(listOfLists))]

def mask(image, function):
    maskImage = deepCopy(image)
    for i in range(len(image)):
        for j in range(len(image)):
            if function(i, j):
                if image[i][j] in [0,1]:
                    maskImage[i][j] = (image[i][j]+1)%2
    return maskImage


def placeData(image, data):
    size = len(image)
    position = [size-1, size-1]
    up = True
    for i in data:
        while not isAreaFree(image, [position, position]):
            if up:
                if position[0] % 2 == 0:
                    position[0] -= 1
                else:
                    position[0] += 1
                    position[1] -= 1
                if position[1] == -1:
                    position[0] -= 2
                    position[1] = 0
                    up = False
            else:
                if position[0] % 2 == 0:
                    position[0] -= 1
                else:
                    position[0] += 1
                    position[1] += 1
                if position[1] == size:
                    position[0] -= 2
                    position[1] = size - 1
                    up = True
        addToImage(image, position, [[(int(i)+1)%2]])

def insertAlignmentPattern(image, version):
    alignmentPositions = json.loads(open('alignmentPattern.json','r').read())[str(version)]
    alignmentPattern = [[10,10,10,10,10],[10,11,11,11,10],[10,11,10,11,10],[10,11,11,11,10],[10,10,10,10,10]]
    for i in alignmentPositions:
        for j in alignmentPositions:
            if isAreaFree(image, [[i-2,j-2], [i+3,j+3]]):
                addToImage(image, [i-2,j-2], alignmentPattern)
            

def addToImage(image, position, element):
    #position is represented by [x, y]
    for i in range(len(element)):
        for j in range(len(element[0])):
            image[position[0]+i][position[1]+j] = element[i][j]
    return image

def isAreaFree(image, area):
    #area is [[x1, y1], [x2, y2]] with x1 < x2 and y1 < y2
    for i in range(area[0][0], area[1][0]+1):
        for j in range(area[0][1], area[1][1]+1):
            if image[i][j] != 42:
                return False
    return True

def createMessagePolynomial(string):
    polynomial = []
    for i in range(0, len(string), 8):
        polynomial.append([int(string[i:i+8], 2), len(string)//8-i//8-1])
    return polynomial

def createGeneratorPolynomial(string, version, correctionLevel):
    numberOfCodewords = json.loads(open('numberOfCodewords.json','r').read())
    generatorPolynomials = json.loads(open('generatorPolynoms.json','r').read())
    degreeOfPolynomial = numberOfCodewords[str(version)+'-'+str('LMQH'[correctionLevel])][1]-2
    return generatorPolynomials[degreeOfPolynomial]

def generateErrorCorrectionCodeword(message, generator):
    result = multiplyPolynomials(message, [generator[0]])
    factor = antilog(message[0][0])
    for i in range(len(message)):
        modifiedGenerator = multiplyPolynomials(generator, [[factor,result[0][1]-generator[0][1]]])
        modifiedGenerator = [[log(j[0]), j[1]] for j in modifiedGenerator]
        result = subtract(result, modifiedGenerator)
        factor = antilog(result[0][0])
    return result

def subtract(message, generator):
    terms = message[0][1]+1
    result = [[0, terms-1-i] for i in range(terms)]
    for i in message:
        result[terms-1-i[1]][0] = i[0]
    for i in generator:
        result[terms-1-i[1]][0] = result[terms-1-i[1]][0] ^ i[0]
    result2 = []
    for i in result:
        if i[0] != 0:
            result2.append(i)
    return sorted(result2, key=lambda x:x[1], reverse=True)

def divideInBlocks(version, correctionLevel, bitstring):
    numberOfCodewords = json.loads(open('numberOfCodewords.json','r').read())
    amountErrors = numberOfCodewords[str(version)+'-'+str('LMQH'[correctionLevel])][1]
    blocksGroup1 = numberOfCodewords[str(version)+'-'+str('LMQH'[correctionLevel])][2]
    amountGroup1 = numberOfCodewords[str(version)+'-'+str('LMQH'[correctionLevel])][3]
    blocksGroup2 = numberOfCodewords[str(version)+'-'+str('LMQH'[correctionLevel])][4]
    amountGroup2 = numberOfCodewords[str(version)+'-'+str('LMQH'[correctionLevel])][5]
    group1 = [bitstring[start*amountGroup1*8:start*amountGroup1*8+amountGroup1*8] for start in range(blocksGroup1)]
    group2 = [bitstring[blocksGroup1*amountGroup1*8+start*amountGroup2*8:blocksGroup1*amountGroup1*8+start*amountGroup2*8+amountGroup2*8] for start in range(blocksGroup2)]
    data1 = []
    data2 = []
    error = []
    for i in range(len(group1)):
        message = createMessagePolynomial(group1[i])
        data1.append([message[i][0] for i in range(len(message))])
        generator = createGeneratorPolynomial(group1[i], version, correctionLevel)
        errorWords = generateErrorCorrectionCodeword(message, generator)
        error.append([errorWords[i][0] for i in range(len(errorWords))])
    for i in range(len(group2)):
        message = createMessagePolynomial(group2[i])
        data2.append([message[i][0] for i in range(len(message))])
        generator = createGeneratorPolynomial(group2[i], version, correctionLevel)
        errorWords = generateErrorCorrectionCodeword(message, generator)
        error.append([errorWords[i][0] for i in range(len(errorWords))])
    data = createInterlacedData(data1, data2, error, version)
    return data
    
def createInterlacedData(group1, group2, errors, version):
    remainderBits = json.loads(open('remainderBits.json','r').read())
    groups = group1 + group2
    data = ''
    for i in range(len(groups[0])+1):
        for j in range(len(groups)):
            try:
                data += f'{groups[j][i]:08b}'
            except:
                pass
    for i in range(len(errors[0])):
        for j in range(len(errors)):
            try:
                data += f'{groups[j][i]:08b}'
            except:
                pass
    data += '0'*remainderBits[str(version)]
    return data
            

def isNumeric(string):
    for i in string:
        if (ord(i)<48) or (ord(i)>57):
            return False
    return True

def isAlphanumeric(string):
    liste = json.loads(open('alphanumericEncodingTable.json', 'r').read())
    alphanumericCharSet = list(liste.keys())
    for i in string:
        if i not in alphanumericCharSet:
            return False
    return True

def isByte(string):
    try:
        string.encode('iso-8859-1')
        return True
    except:
        return False

def chooseVersion(string, encoding, correctionLevel):
    versionInfo = json.loads(open('QRVersionInfo.json', 'r').read())
    i = 0
    if encoding == '0001':
        while len(string) >= versionInfo[i*4+correctionLevel][2]:
            i += 1
        return versionInfo[i*4][0]
    elif encoding == '0010':
        while len(string) >= versionInfo[i*4+correctionLevel][3]:
            i += 1
        return versionInfo[i*4][0]
    elif encoding == '0100':
        while len(string) >= versionInfo[i*4+correctionLevel][4]:
            i += 1
        return versionInfo[i*4][0]
    else:
        sys.exit(1)

def characterCount(length, version, mode):
    if version <= 9:
        if mode == '0001':
            return f'{length:010b}'
        elif mode == '0010':
            return f'{length:09b}'
        elif mode == '0100':
            return f'{length:08b}'
    elif version <= 26:
        if mode == '0001':
            return f'{length:012b}'
        elif mode == '0010':
            return f'{length:011b}'
        elif mode == '0100':
            return f'{length:016b}'
    else:
        if mode == '0001':
            return f'{length:014b}'
        elif mode == '0010':
            return f'{length:013b}'
        elif mode == '0100':
            return f'{length:016b}'

def addNeededZeros(bitString, version, correctionLevel):
    numberOfCodewords = json.loads(open('numberOfCodewords.json', 'r').read())
    requiredBits = numberOfCodewords[str(version)+'-'+str('LMQH'[correctionLevel])][0]*8
    bitString += '0'*min(4, requiredBits-len(bitString))
    bitString += '0'*(8-len(bitString)%8)
    for i in range((requiredBits - len(bitString))//8):
        if i%2==0:
            bitString += '11101100'
        else:
            bitString += '00010001'
    return bitString

def multiplyPolynomials(polynom1, polynom2):
    #a polynom (a^0x^2-a^1x^0) is represented as [[0,2],[1,0]]
    result = []
    for i in polynom1:
        for j in polynom2:
            result.append([i[0]+j[0], i[1]+j[1]])
    result2 = sorted(result, key=lambda x:x[1], reverse=True)
    result = []
    counter = 0
    while counter < len(result2):
        aktX = [result2[counter][1], []]
        while result2[counter][1] == aktX[0]:
            aktX[1].append(result2[counter][0])
            counter += 1
            if counter == len(result2):
                break
        result.append([antilog(xOr(aktX[1])), aktX[0]])
        
    return result

def xOr(array):
    result = log(array[0])
    for i in range(1, len(array)):
        result = log(array[i]) ^ result
    return result

def log(number):
    table = json.loads(open('log.json').read())
    return table[number%255]

def antilog(number):
    table = json.loads(open('antilog.json').read())
    return table[number-1%255]

def numericEncoding(string, version, correctionLevel):
    splitString = [str(int(string[start:start+3])) for start in range(0, len(string), 3)]
    encodedString = ''
    for i in range(len(splitString)):
        if len(splitString[i])==3:
            encodedString += f'{int(splitString[i]):010b}'
        elif len(splitString[i])==2:
            encodedString += f'{int(splitString[i]):07b}'
        else:
            encodedString += f'{int(splitString[i]):04b}'
    return addNeededZeros('0001'+characterCount(len(string), version, '0001')+encodedString, version, correctionLevel)

def alphanumericEncoding(string, version, correctionLevel):
    table = json.loads(open('alphanumericEncodingTable.json', 'r').read())
    splitString = [string[start:start+2] for start in range(0, len(string), 2)]
    encodedString = ''
    for i in range(len(splitString)):
        if len(splitString[i])==2:
            encodedString += f'{table[splitString[i][0]]*45+table[splitString[i][1]]:011b}'
        else:
            encodedString += f'{table[splitString[i][0]]:06b}'
    return addNeededZeros('0010'+characterCount(len(string), version, '0010')+encodedString, version, correctionLevel)

def byteEncoding(string, version, correctionLevel):
    encodedString = ''
    for i in string.encode('iso-8859-1'):
        encodedString += f'{i:08b}'
    return addNeededZeros('0100'+characterCount(len(string), version, '0100')+encodedString, version, correctionLevel)

if __name__=="__main__":
    main('Hello World!', 2)
