import tkinter
import sys
import json

def main(string, correctionLevel):
    root = tkinter.Tk()
    root.geometry('300x300')
    root.resizable(False, False)
    canvas = tkinter.Canvas(root, width=300, height=300)
    createQRCodeIn(canvas, string, correctionLevel)
    return 0

def createQRCodeIn(canvas, string, correctionLevel):
    encodedString = encodeWithEfficientMode(string, correctionLevel)
    print(encodedString)
    

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
    requiredBits = numberOfCodewords[str(version)+'-'+str('LMQH'[correctionLevel])]*8
    bitString += '0'*min(4, requiredBits-len(bitString))
    bitString += '0'*(8-len(bitString)%8)
    for i in range((requiredBits - len(bitString))//8):
        if i%2==0:
            bitString += '11101100'
        else:
            bitString += '00010001'
    return bitString
    

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
    main('HELLO WORLD', 2)
