"""HT3 Tokens
Tokens are the things that is used for parser to parse."""

# Define numbers, operators and the letters.
ASCII_NUMBERS = "0123456789"
ASCII_ALPHA   = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
OPERS         = "*=-+/"
DOUBLE_OPERS  = ["**", "++", "--", "//", "+=", "-=", "*=", "/=", "=="]
TYPES         = [
    "str",
    "int",
    "list",
    "float",
    "char",
]

# Define token names.
# -----------------
#      Decimal
T_INT    = "INT" #   -> ASCII_NUMBERS without dot.
T_FLOAT  = "FLOAT" # -> ASCII_NUMBERS with dot.
# -----------------
#       Alpha
T_IDENT  = "IDENT" # -> Identifier (WORD)
T_STRING = "STRING" #-> String ("WORD")
T_CHAST  = "CHAST" # -> Char String ('C')
# -----------------
#       Symbols
T_OPER   = "OPER" #  -> Operators (=*+-/)
T_DOOPER = "DOOPER" #-> Double Operators (==, *=, **, ++, +=, ...)
T_DOT    = "DOT" #   -> Dot (.)
T_DODOT  = "DODOT" # -> Double Dot (..)
T_DDOT   = "DDOT" #  -> : (Forgo its name)
T_SCOPE  = "SCOPE" # -> Scope (::)
T_COMMA  = "COMMA" # -> Comma (,)
T_LPRM   = "LPRM" #  -> Left Param ( ( )
T_RPRM   = "RPRM" #  -> Right Param ( ) )
T_LBRC   = "LBRC" #  -> Left Brace ( { )
T_RBRC   = "RBRC" #  -> Right Brace ( } )
T_LBRK   = "LBRK" #  -> Left Bracket ( [ ) 
T_RBRK   = "RBRK" #  -> Right Bracket ( ] )
T_ORTT   = "ORTT" #  -> OR Token (|)
T_BSLH   = "BSLH" #  -> Backslash Token (\)
T_ORORTT = "ORORTT" #-> Double OR Token (||)
T_UNOT   = "UNOT" #  -> !
T_DOLLAR = "DOLLAR" #-> $
T_AND    = "AND" #   -> &

# these doesn't follows the comment align ;-;
T_COMMENT_LINE = "COMMENT_LINE"
T_COMMENT_BLOCK = "COMMENT_BLOCK"
# -----------------
#   BSLH Approved
BSLH_APPROVED = [
    "n",
    "r",
    "t",
    "\\",
    "a",
    "b",
    "f",
    "v",
    "\'",
    "\"",
    "?",
    "0",
]

###########################################################################
#                      Characters that are allowed                        #
###########################################################################
#         #      NUMF       #     SYMBOLS     #      ASCIS      #         #
#         #     W./NUM      #     OP/ASYM     #      ALPHA      #         #
###########################################################################
# -- NUMF : 012346789 | 0.1 2.3 4.5 6.7 8.9
# -- SYMB : *-/+=     | {} () [] ; , .      | .. ** *= += -= -- ++ // /= ::
# -- ASCI : A..Z a..z | STRING: all
###########################################################################

LRToToken = {
    "{": T_LBRC,
    "}": T_RBRC,
    "[": T_LBRK,
    "]": T_RBRK,
    "(": T_LPRM,
    ")": T_RPRM,
    ",": T_COMMA,
    "!": T_UNOT,
    "$": T_DOLLAR,
    "&": T_AND
}