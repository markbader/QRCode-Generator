import tkinter
import sys
import json

def main(string, correctionLevel):
    root = tkinter.Tk()
    root.geometry('300x300')
    canvas = tkinter.Canvas(root,  bg='white')
    canvas.pack(fill='both', expand=1)
    createQRCodeIn(canvas, string, correctionLevel)
    return 0

def createQRCodeIn(canvas, string, correctionLevel):
    qrCode = createQRCode(string, correctionLevel)
    

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
        
    messagePolynomial = createMessagePolynomial(encodedString)
    generatorPolynomial = createGeneratorPolynomial(encodedString, version, correctionLevel)
    errorCorrectionCodeword = generateErrorCorrectionCodeword(messagePolynomial, generatorPolynomial)
    return encodedString

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

def isKanji(string):
    'TBD: implement Kanji encoding'
    return False

def chooseVersion(string, encoding, correctionLevel):
    versionInfo = json.loads(open('QRVersionInfo.json', 'r').read())
    i = 0
    if encoding == '0001':
        while len(string) > versionInfo[i*4+correctionLevel][2]:
            i += 1
        return versionInfo[i*4][0]
    elif encoding == '0010':
        while len(string) > versionInfo[i*4+correctionLevel][3]:
            i += 1
        return versionInfo[i*4][0]
    elif encoding == '0100':
        while len(string) > versionInfo[i*4+correctionLevel][4]:
            i += 1
        return versionInfo[i*4][0]
    elif encoding == '1000':
        while len(string) > versionInfo[i*4+correctionLevel][5]:
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
        elif mode == '1000':
            return f'{length:08b}'
    elif version <= 26:
        if mode == '0001':
            return f'{length:012b}'
        elif mode == '0010':
            return f'{length:011b}'
        elif mode == '0100':
            return f'{length:016b}'
        elif mode == '1000':
            return f'{length:010b}'
    else:
        if mode == '0001':
            return f'{length:014b}'
        elif mode == '0010':
            return f'{length:013b}'
        elif mode == '0100':
            return f'{length:016b}'
        elif mode == '1000':
            return f'{length:012b}'

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

def kanjiEncoding(string, version, correctionLevel):
    pass


if __name__=="__main__":
    main('HELLO WORLD', 1)
