
class TokenType:

    #literal types
    INT=1
    FLOAT = 2
    STRING = 3
    TRUE = 4
    FALSE = 5


    #keywords
    LET = 6
    FN = 7
    IF = 8
    ELSE = 9
    RETURN =10

    #identifiers
    IDENTIFIER = 11

    #operators
    PLUS = 12
    MINUS = 13
    MULTIPLY = 14
    DIVIDE = 15
    PERCENT = 16
    EQUAL = 17
    EQUAL_EQUAL = 18
    NOT_EQUAL = 19
    LESS = 20
    LESS_EQUAL = 21
    GREATER = 22
    GREATER_EQUAL = 23
    AND_AND = 24
    OR_OR = 25
    BANG = 26

    #delimiters
    LPAREN = 27
    RPAREN = 28
    LBRACE = 29
    RBRACE = 30
    LBRACKET = 31
    RBRACKET = 32
    SEMICOLON = 33
    COMMA = 34
    COLON = 35
    ARROW = 36

    #other
    EOF = 37
    NEWLINE = 38

class Token:
    type: TokenType
    value: str
    line: int
    col: int

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.line}, {self.col})"

class Lexer:

    def __init__(self,code:str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: List[Token] = []

        self.keywords = {
            'let': TokenType.LET,
            'fn': TokenType.FN,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'return': TokenType.RETURN,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE
        }

def current_char(self):
    if self.pos >= len(self.code):
        return None
    return self.code[self.pos]

def peek(self, offset: int = 1):
    pos = self.pos + offset
    if pos >= len(self.code):
        return None 
    return self.code[pos]

def advance(self, steps: int = 1):
    if self.pos < len(self.code):
        if self.code[self.pos] == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1

def skip_whitespace(self):
    while self.current_char() and self.current_char() in '\t':
        self.advance()

def skip_comment(self):
    if self.current_char() == '/' and self.peek() == '/':
        while self.current_char() and self.current_char() != '\n':
            self.advance()


