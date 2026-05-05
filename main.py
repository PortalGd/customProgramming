print("Hello World")
print("Welcome to Python programming!")



def tokenize(code):
    tokens = []
    i = 0
    while i < len(code):
        if code[i].isspace():
            i += 1
        elif code[i:i+3] == 'let':
            tokens.append(('LET', 'let'))
            i += 3  
        return tokens
    
if __name__ == "__main__":
    code = "let x = 5"
    tokens = tokenize(code)
    print(tokens)

