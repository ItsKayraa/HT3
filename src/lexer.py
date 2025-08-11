"""# HT3 Lexer

This module includes the lexer function and the module 'tokens' and 'errors' which could be used to tokenize the content and more."""

import tokens
import errors

def bslh(char: str):
    match char:
        case "n":
            return "\n"
        case "r":
            return "\r"
        case "t":
            return "\t"
        case "0":
            return "\0"
        case "b":
            return "\b"
        case "\\":
            return "\\"
        case "\'":
            return "\'"
        case "\"":
            return "\""
        case "\a":
            return "\a"

#       ----
# Lexer main function
#       ----

def lmain(content: str):
    # The tokens that will be returned
    result = []
    # (TOKENTYPE, TOKENCONTENT) -> Tuple
    errorsh = []
    error = False
    
    curline = 0
    lines = content.splitlines()

    # Character index
    i = 0
    while i < len(content):
        curchar  = content[i]
        nextchar = content[i+1] if i+1 < len(content) else None # Make the nextchar variable to either equal next character or none.
        
        # Pass if the curchar is something that doesn't needs to be tokenized.
        if curchar in ["\t", "\r", " "]:
            i+=1
        
        # Increase line amount for line check.
        elif curchar == "\n":
            i+=1
            curline+=1
        
        # Check if the current character will make a float or int decimal.
        elif curchar in tokens.ASCII_NUMBERS:
            TYP  = tokens.T_INT # The type which will be added to result.
            TEMP = ""# Temporary string for the token
            dota = 0 # Dot amounts (For detecting errors in float numbers.)

            # Loop to add characters to TEMP.
            while i < len(content) and (content[i] in tokens.ASCII_NUMBERS or content[i] == "."):
                c = content[i]
                if c == ".":
                    if dota == 1:
                        errorsh.append(errors.TokenizerError("Expected only 1 dots for a float number.", curchar, i, curline, lines[curline]))
                        error = True
                    else:
                        TYP = tokens.T_FLOAT
                TEMP += c
                i+=1
            result.append((TYP, TEMP)) # ("INT"|"FLOAT", {TEMP})
        
        # Check if the current character is an identifier.
        elif curchar in tokens.ASCII_ALPHA:
            TEMP = curchar
            i += 1
            while i < len(content) and (
                content[i] in tokens.ASCII_ALPHA or
                content[i] in tokens.ASCII_NUMBERS or
                content[i] == "_"
            ):
                TEMP += content[i]
                i += 1
            result.append((tokens.T_IDENT, TEMP))

        # String check.
        elif curchar == '"':
            TYP = tokens.T_STRING
            TEMP = ""
            i += 1
            while i < len(content):
                if content[i] == '"':
                    break
                if content[i] == "\\" and i + 1 < len(content):
                    TEMP += bslh(content[i+1]) or content[i+1]
                    i += 2
                    continue
                TEMP += content[i]
                i += 1
            else:
                errorsh.append(errors.TokenizerError("Unterminated string literal.", curchar, i, curline, lines[curline]))
                error = True
            i += 1
            result.append((TYP, TEMP))
        
        # ChaST check.
        elif curchar == "'":
            if i + 2 >= len(content) or content[i+2] != "'":
                errorsh.append(errors.TokenizerError("Expected closing quote for character literal.", curchar, i, curline, lines[curline]))
                error = True
            else:
                result.append((tokens.T_CHAST, content[i+1]))
            i += 3

        # Operator | Double Operator check
        elif curchar in tokens.OPERS:
            if nextchar and curchar + nextchar in tokens.DOUBLE_OPERS:
                result.append((tokens.T_DOOPER, curchar+nextchar))
                i += 2
            else:
                result.append((tokens.T_OPER, curchar))
                i += 1
        
        # LPRM | RPRM | LBRC | RBRC | LBRK | RBRK &&:check
        elif curchar in tokens.LRToToken:
            result.append((tokens.LRToToken[curchar], curchar)) # ({LRToToken[curchar]} | {curchar})
            i+=1
        
        elif curchar == "|":
            if nextchar == "|":
                result.append((tokens.T_ORORTT, "||"))
                i+=1
            else:
                result.append((tokens.T_ORTT, "|"))
            i+=1
        
        # Backslash check
        elif curchar == "\\":
            if nextchar == None:
                errorsh.append(errors.BackslashError("Expected type after backslash.", curchar, i, curline, lines[curline]))
            elif not nextchar in tokens.BSLH_APPROVED:
                print("Warning: unknown BSLHToken: ", nextchar)
            result.append((tokens.T_BSLH, nextchar))
            i+=2
        
        # Double Symbols
        elif curchar in [".", ":"]:
            DOUBLE = False
            if nextchar == curchar:
                DOUBLE = True
            if curchar == ".":
                if DOUBLE:
                    result.append((tokens.T_DODOT, ".."))
                    i+=2
                else:
                    result.append((tokens.T_DOT, "."))
                    i+=1
            else:
                if DOUBLE:
                    result.append((tokens.T_SCOPE, "::"))
                    i+=2
                else:
                    result.append((tokens.T_DDOT, ":"))
                    i+=1
        
        # Unknown character
        else:
            errorsh.append(errors.UnknownCharacter(f"Unknown character.", curchar, i, curline, lines[curline]))
            i+=1
            error = True

    
    return (result, error, errorsh)