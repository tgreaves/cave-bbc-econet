#!/usr/bin/env python
#
# (c) 2007 Matt Godbolt.
# Use however you like, as long as you put credit where credit's due.
# Some information obtained from source code from RISC OS Open.
# v0.01 - first release.  Doesn't deal with GOTO line numbers.

# source: http://xania.org/200711/BBCBasicToText.py
# 2016 jmechnich, prints and handles line numbers now, can use stdin and stdout


import struct, re, getopt, sys

# The list of BBC BASIC V tokens:
# Base tokens, starting at 0x7f
tokens = [
    'OTHERWISE', # 7f
    'AND', 'DIV', 'EOR', 'MOD', 'OR', 'ERROR', 'LINE', 'OFF',
    'STEP', 'SPC', 'TAB(', 'ELSE', 'THEN', '<line>' # TODO
        , 'OPENIN', 'PTR',

    'PAGE', 'TIME', 'LOMEM', 'HIMEM', 'ABS', 'ACS', 'ADVAL', 'ASC',
    'ASN', 'ATN', 'BGET', 'COS', 'COUNT', 'DEG', 'ERL', 'ERR',

    'EVAL', 'EXP', 'EXT', 'FALSE', 'FN', 'GET', 'INKEY', 'INSTR(',
    'INT', 'LEN', 'LN', 'LOG', 'NOT', 'OPENUP', 'OPENOUT', 'PI',

    'POINT(', 'POS', 'RAD', 'RND', 'SGN', 'SIN', 'SQR', 'TAN',
    'TO', 'TRUE', 'USR', 'VAL', 'VPOS', 'CHR$', 'GET$', 'INKEY$',

    'LEFT$(', 'MID$(', 'RIGHT$(', 'STR$', 'STRING$(', 'EOF',
        '<ESCFN>', '<ESCCOM>', '<ESCSTMT>',
    'WHEN', 'OF', 'ENDCASE', 'ELSE' # ELSE2
        , 'ENDIF', 'ENDWHILE', 'PTR',

    'PAGE', 'TIME', 'LOMEM', 'HIMEM', 'SOUND', 'BPUT', 'CALL', 'CHAIN',
    'CLEAR', 'CLOSE', 'CLG', 'CLS', 'DATA', 'DEF', 'DIM', 'DRAW',

    'END', 'ENDPROC', 'ENVELOPE', 'FOR', 'GOSUB', 'GOTO', 'GCOL', 'IF',
    'INPUT', 'LET', 'LOCAL', 'MODE', 'MOVE', 'NEXT', 'ON', 'VDU',

    'PLOT', 'PRINT', 'PROC', 'READ', 'REM', 'REPEAT', 'REPORT', 'RESTORE',
    'RETURN', 'RUN', 'STOP', 'COLOUR', 'TRACE', 'UNTIL', 'WIDTH', 'OSCLI']

# Referred to as "ESCFN" tokens in the source, starting at 0x8e.
cfnTokens = [
    'SUM', 'BEAT']
# Referred to as "ESCCOM" tokens in the source, starting at 0x8e.
comTokens = [
    'APPEND', 'AUTO', 'CRUNCH', 'DELET', 'EDIT', 'HELP', 'LIST', 'LOAD',
    'LVAR', 'NEW', 'OLD', 'RENUMBER', 'SAVE', 'TEXTLOAD', 'TEXTSAVE', 'TWIN'
    'TWINO', 'INSTALL']
# Referred to as "ESCSTMT", starting at 0x8e.
stmtTokens= [
    'CASE', 'CIRCLE', 'FILL', 'ORIGIN', 'PSET', 'RECT', 'SWAP', 'WHILE',
    'WAIT', 'MOUSE', 'QUIT', 'SYS', 'INSTALL', 'LIBRARY', 'TINT', 'ELLIPSE',
    'BEATS', 'TEMPO', 'VOICES', 'VOICE', 'STEREO', 'OVERLAY']

def Detokenise(line):
    """Replace all tokens in the line 'line' with their ASCII equivalent."""
    # Internal function used as a callback to the regular expression
    # to replace tokens with their ASCII equivalents.
    def ReplaceFunc(match):
        ext, token = match.groups()
        tokenOrd = ord(token[0])
        if ext: # An extended opcode, CASE/WHILE/SYS etc
            if ext == '\xc6':
                return ' ' + cfnTokens[tokenOrd-0x8e]
            if ext == '\xc7':
                return ' ' + comTokens[tokenOrd-0x8e]
            if ext == '\xc8':
                return ' ' + stmtTokens[tokenOrd-0x8e]
            raise Exception, "Bad token"
        else: # Normal token, plus any extra characters
            if token[0] == '\x8d':
                # decode line number (The BASIC ROM User Guide p.41)
                n1,n2,n3 = [ ord(i) for i in token[1:] ]
                n1  = (n1*4)&0xff
                n2 ^= (n1&0xc0)
                n1  = (n1*4)&0xff
                n3 ^= n1
                return str(n3*256+n2)
            else:
                return tokens[tokenOrd-127] + token[1:]

    # This regular expression is essentially:
    # (Optional extension token) followed by
    # (REM token followed by the rest of the line)
    #     -- this ensures we don't detokenise the REM statement itself
    # OR
    # (any token)
    return re.sub(r'([\xc6-\xc8])?(\xf4.*|[\x7f-\x8c\x8e-\xff]|\x8d.{3})', ReplaceFunc, line)

def ReadLines(data):
    """Returns a list of [line number, tokenised line] from a binary
       BBC BASIC V format file."""
    lines = []
    while True:
        if len(data) < 2:
            raise Exception, "Bad program: data too short"
        if data[0] != '\r':
            print `data`
            raise Exception, "Bad program: data not starting with \\r"
        if data[1] == '\xff':
            break
        lineNumber, length = struct.unpack('>hB', data[1:4])
        lineData = data[4:length]
        lines.append([lineNumber, lineData])
        data = data[length:]
    return lines

def Decode(data, output):
    """Decode binary data 'data' and write the result to 'output'."""
    lines = ReadLines(data)
    for lineNumber, line in lines:
        lineData = Detokenise(line)
        output.write("%5s%s\n" % (str(lineNumber),lineData))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: %s INPUT OUTPUT" % sys.argv[0]
        sys.exit(1)
    infile, outfile = sys.argv[1:]
    if infile == '-':
        entireFile = sys.stdin.read()
    else:
        with open(infile, 'rb') as f:
            entireFile = f.read()
    if outfile == '-':
        output = sys.stdout
    else:
        output = open(outfile, 'w')
    Decode(entireFile, output)
    output.close()
