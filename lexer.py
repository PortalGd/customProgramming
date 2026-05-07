
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
    def __init__(self, type, value, line, col):
        self.type = type
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.line}, {self.col})"

class Lexer:

    def __init__(self,code:str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: list[Token] = []

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
            self.pos += steps

    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t':
            self.advance()

    def skip_comment(self):
        if self.current_char() == '/' and self.peek() == '/':
            while self.current_char() and self.current_char() != '\n':
                self.advance()

    def read_string(self, quote_char: str) -> str:
        value = ''
        self.advance()

        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\': 
                self.advance()
                if self.current_char() == 'n':
                    value += '\n'
                elif self.current_char() == 't':
                    value += '\t'
                elif self.current_char() == '\\':
                    value += '\\'
                else:
                    value += self.current_char()
                self.advance()
            else:
                value += self.current_char()
                self.advance()
        
        if self.current_char() == quote_char:
            self.advance() 
        return value

    def read_number(self) -> Token:
        sl = self.line
        sc = self.col
        num_str = ''

        while self.current_char() and (self.current_char().isdigit() or self.current_char() == "."):
            num_str += self.current_char()
            self.advance()
        token_type = TokenType.FLOAT if '.' in num_str else TokenType.INT
        return Token(token_type, num_str, sl, sc)
    
    def read_identifier(self) -> Token:
        sl = self.line
        sc = self.col
        id_str = ''

        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            id_str += self.current_char()
            self.advance()
        
        token_type = self.keywords.get(id_str, TokenType.IDENTIFIER)
        return Token(token_type, id_str, sl, sc)
    
    def tokenize(self) -> list[Token]:
        while self.pos < len(self.code):
            self.skip_whitespace()

            if self.pos >= len(self.code):
                break

            if self.current_char() == '/' and self.peek() == '/':
                self.skip_comment()
                continue

            sl = self.line
            sc = self.col
            char = self.current_char()

            if char == "\n":
                self.advance()
                continue

            if char in ('"', "'"):
                self.tokens.append(Token(TokenType.STRING, self.read_string(char), sl, sc))
                continue

            if char.isdigit():
                self.tokens.append(self.read_number())
                continue

            if char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
                continue

            if char == "!" and self.peek() == "=":
                self.tokens.append(Token(TokenType.NOT_EQUAL, '!=', sl, sc))
                self.advance(2)
                continue

            if char == "<" and self.peek() == "=":
                self.tokens.append(Token(TokenType.LESS_EQUAL, '<=', sl, sc))
                self.advance(2)
                continue

            if char == ">" and self.peek() == "=":
                self.tokens.append(Token(TokenType.GREATER_EQUAL, '>=', sl, sc))
                self.advance(2)
                continue

            if char == "&" and self.peek() == "&":
                self.tokens.append(Token(TokenType.AND_AND, '&&', sl, sc))
                self.advance(2)
                continue

            if char == "|" and self.peek() == "|":
                self.tokens.append(Token(TokenType.OR_OR, '||', sl, sc))
                self.advance(2)
                continue

            if char == '-' and self.peek() == '>':
                self.tokens.append(Token(TokenType.ARROW, '->', sl, sc))
                self.advance(2)
                continue

            single_char_tokens = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE,
                '%': TokenType.PERCENT,
                '=': TokenType.EQUAL,
                '<': TokenType.LESS,
                '>': TokenType.GREATER,
                '!': TokenType.BANG,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                ';': TokenType.SEMICOLON,
                ',': TokenType.COMMA,
                ':': TokenType.COLON,
            }

            if char in single_char_tokens:
                self.tokens.append(Token(single_char_tokens[char], char, sl, sc))
                self.advance()
                continue

            raise SyntaxError(f"Unexpected character '{char}' at line {sl}:{sc}")
        
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.col))
        return self.tokens

def tokenize(code: str) -> list[Token]:
    lexer = Lexer(code)
    return lexer.tokenize()

if __name__ == "__main__":
    code1 = "let x = 5;"
    print("Test 1:", code1)
    tokens1 = tokenize(code1)
    for token in tokens1:
        print(f"  {token}")
    print()
    code2 = "x + 3 * 2"
    print("Test 2:", code2)
    tokens2 = tokenize(code2)
    for token in tokens2:
        print(f"  {token}")
    print()
    code3 = "fn add(a: int, b: int) -> int { a + b }"
    print("Test 3:", code3)
    tokens3 = tokenize(code3)
    for token in tokens3:
        print(f"  {token}")
    print()
    code4 = 'let msg = "hello world";'
    print("Test 4:", code4)
    tokens4 = tokenize(code4)
    for token in tokens4:
        print(f"  {token}")


