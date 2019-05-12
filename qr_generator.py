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
    encodedString = encodeWithEfficientMode(string, correctionLevel)
    messagePolynomial = createMessagePolynomial(encodedString)
    generatorPolynomial = createGeneratorPolynomial(encodedString)
    generateErrorCorrectionCodeword(messagePolynomial, generatorPolynomial)

def createMessagePolynomial(string):
    message = []
    for i in range(0, len(string), 8):
        message.append([int(string[i:i+8], 2), len(string)//8-i//8-1])
    return message

def createGeneratorPolynomial(string):
    pass

def generateErrorCorrectionCodeword(message, generator):
    pass

def encodeWithEfficientMode(string, correctionLevel):
    if isNumeric(string):
        return numericEncoding(string, chooseVersion(string, '0001', correctionLevel), correctionLevel)
    elif isAlphanumeric(string):
        return alphanumericEncoding(string, chooseVersion(string, '0010', correctionLevel), correctionLevel)
    elif isByte(string):
        return byteEncoding(string, chooseVersion(string, '0100', correctionLevel), correctionLevel)
    elif isKanji(string):
        return kanjiEncoding(string, chooseVersion(string, '1000', correctionLevel), correctionLevel)
    else:
        print('character set is not supported')
        sys.exit(1)

def isNumeric(string):
    for i in string:
        if (ord(i)<48) or (ord(i)>57):
            return False
    return True

def isAlphanumeric(string):
    liste = json.loads(open('alphanumericEncodingTable.json').read())
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
    versionInfo = json.loads(open('QRVersionInfo.json').read())
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
    numberOfCodewords = json.loads(open('numberOfCodewords.json').read())
    requiredBits = numberOfCodewords[str(version)+'-'+str('LMQH'[correctionLevel])][0]*8
    bitString += '0'*min(4, requiredBits-len(bitString))
    bitString += '0'*(8-len(bitString)%8)
    for i in range((requiredBits - len(bitString))//8):
        if i%2==0:
            bitString += '11101100'
        else:
            bitString += '00010001'
    return bitString

def multiplyPolynoms(polynom1, polynom2):
    #a polynom (a^0x^2-a^1x^0) is represented as [[0,2],[1,0]]
    result = []
    for i in polynom1:
        for j in polynom2:
            result.append([i[0]+j[0], i[1]+j[1]])
    result2 = sorted(result, key=lambda x:x[1], reverse=True)
    result = [[log(result2[0][0]), result2[0][1]]]
    for i in result2[1:]:
        if result[-1][1] == i[1]:
            result[-1][0] = (result[-1][0]) ^ (log(i[0]))
        else:
            result.append([log(i[0]), i[1]])
    for i in range(len(result)):
        result[i][0] = antilog(result[i][0])
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
    table = json.loads(open('alphanumericEncodingTable.json').read())
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
