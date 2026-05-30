from lexer import Token, TokenType, tokenize
from typing import List, Optional, Union
import nodes
from nodes import Program, Stmt, Expr, Type, LetStmt, FnStmt, ReturnStmt, ExprStmt
from nodes import IntLiteral, FloatLiteral, StringLiteral, BoolLiteral, Ident, BinaryOp, UnaryOp, Call, IfExpr, Block


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Token:
        """Return current token."""
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # Return EOF
        return self.tokens[self.pos]
    
    def peek(self, offset: int = 1) -> Token:
        """Look ahead."""
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[pos]
    
    def advance(self, steps: int = 1) -> Token:
        """Move forward and return current token."""
        token = self.current()
        self.pos += steps
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        """Expect a specific token type."""
        token = self.current()
        if token.type != token_type:
            raise SyntaxError(
                f"Expected {token_type}, got {token.type} at {token.line}:{token.col}"
            )
        return self.advance()
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any type."""
        return self.current().type in token_types
    
    def consume_if(self, *token_types: TokenType) -> bool:
        """Consume token if it matches."""
        if self.match(*token_types):
            self.advance()
            return True
        return False
    
    def parse_program(self) -> Program:
        """Parse entire program."""
        statements = []
        while not self.match(TokenType.EOF):
            stmt = self.parse_stmt()
            statements.append(stmt)
        return Program(statements)
    
    def parse_stmt(self) -> Stmt:
        """Parse a single statement."""
        if self.match(TokenType.LET):
            return self.parse_let_stmt()
        elif self.match(TokenType.FN):
            return self.parse_fn_stmt()
        elif self.match(TokenType.RETURN):
            return self.parse_return_stmt()
        else:
            return self.parse_expr_stmt()
        
    def parse_let_stmt(self) -> LetStmt:
        """Parse: let x = 5;"""
        self.expect(TokenType.LET)
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value

        type_hint = None
        if self.consume_if(TokenType.COLON):
            type_name = self.expect(TokenType.IDENTIFIER).value
            type_hint = Type(type_name)
        
        self.expect(TokenType.EQUAL)
        value = self.parse_expr()
        self.consume_if(TokenType.SEMICOLON)
        return LetStmt(name, type_hint, value)
    
    def parse_fn_stmt(self) -> FnStmt:
        """Parse: fn name(a: int, b: int) -> int { ... }"""
        self.expect(TokenType.FN)
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value

        self.expect(TokenType.LPAREN)
        parameters = []
        while not self.match(TokenType.RPAREN):
            param_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)
            param_type_name = self.expect(TokenType.IDENTIFIER).value
            parameters.append((param_name, Type(param_type_name)))

            if not self.match(TokenType.RPAREN):
                self.expect(TokenType.COMMA)
        
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.ARROW)
        return_type_name = self.expect(TokenType.IDENTIFIER).value
        return_type = Type(return_type_name)

        body = self.parse_block()

        return FnStmt(name, parameters, return_type, body)

    def parse_return_stmt(self) -> ReturnStmt:
        """Parse: return expr;"""
        self.expect(TokenType.RETURN)
        value = None 
        if not self.match(TokenType.SEMICOLON, TokenType.RBRACE):
            value = self.parse_expr()
        self.consume_if(TokenType.SEMICOLON)
        return ReturnStmt(value)
    
    def parse_expr_stmt(self) -> ExprStmt:
        """Parse: expr;"""
        expr = self.parse_expr()
        self.consume_if(TokenType.SEMICOLON)
        return ExprStmt(expr)
    
    def parse_block(self) -> Block:
        """Parse: { stmt; stmt; ... }"""
        self.expect(TokenType.LBRACE)
        stmts = []
        while not self.match(TokenType.RBRACE):
            stmts.append(self.parse_stmt())
        self.expect(TokenType.RBRACE)
        return Block(stmts)
    
    def parse_expr(self) -> Expr:
        """Parse expression."""
        return self.parse_or()
    
    def parse_or(self) -> Expr:
        """Parse: a || b"""
        left = self.parse_and()
        while self.consume_if(TokenType.OR_OR):
            right = self.parse_and()
            left = BinaryOp(left, '||', right)
        return left
    
    def parse_and(self) -> Expr:
        """Parse: a && b"""
        left = self.parse_equality()
        while self.consume_if(TokenType.AND_AND):
            right = self.parse_equality()
            left = BinaryOp(left, '&&', right)
        return left

    def parse_equality(self) -> Expr:
        """Parse: a == b, a != b"""
        left = self.parse_comparison()
        while True:
            if self.consume_if(TokenType.EQUAL_EQUAL):
                right = self.parse_comparison()
                left = BinaryOp(left, '==', right)
            elif self.consume_if(TokenType.NOT_EQUAL):
                right = self.parse_comparison()
                left = BinaryOp(left, '!=', right)
            else:
                break
        return left

    def parse_comparison(self) -> Expr:
        """Parse: a < b, a > b, etc."""
        left = self.parse_additive()
        while True:
            if self.consume_if(TokenType.LESS):
                right = self.parse_additive()
                left = BinaryOp(left, '<', right)
            elif self.consume_if(TokenType.LESS_EQUAL):
                right = self.parse_additive()
                left = BinaryOp(left, '<=', right)
            elif self.consume_if(TokenType.GREATER):
                right = self.parse_additive()
                left = BinaryOp(left, '>', right)
            elif self.consume_if(TokenType.GREATER_EQUAL):
                right = self.parse_additive()
                left = BinaryOp(left, '>=', right)
            else:
                break
        return left
    
    def parse_additive(self) -> Expr:
        """Parse: a + b, a - b"""
        left = self.parse_multiplicative()
        while True:
            if self.consume_if(TokenType.PLUS):
                right = self.parse_multiplicative()
                left = BinaryOp(left, '+', right)
            elif self.consume_if(TokenType.MINUS):
                right = self.parse_multiplicative()
                left = BinaryOp(left, '-', right)
            else:
                break
        return left
    
    def parse_multiplicative(self) -> Expr:
        """Parse: a * b, a / b"""
        left = self.parse_unary()
        while True:
            if self.consume_if(TokenType.MULTIPLY):
                right = self.parse_unary()
                left = BinaryOp(left, '*', right)
            elif self.consume_if(TokenType.DIVIDE):
                right = self.parse_unary()
                left = BinaryOp(left, '/', right)
            elif self.consume_if(TokenType.PERCENT):
                right = self.parse_unary()
                left = BinaryOp(left, '%', right)
            else:
                break
        return left
    
    def parse_unary(self) -> Expr:
        """Parse: -x, !x"""
        if self.consume_if(TokenType.BANG):
            operand = self.parse_unary()
            return UnaryOp('!', operand)
        elif self.consume_if(TokenType.MINUS):
            operand = self.parse_unary()
            return UnaryOp('-', operand)
        else:
            return self.parse_postfix()
    
    def parse_postfix(self) -> Expr:
        """Parse: func(args)"""
        expr = self.parse_primary()
        while True:
            if self.consume_if(TokenType.LPAREN):
                args = []
                if not self.match(TokenType.RPAREN):
                    while True:
                        args.append(self.parse_expr())
                        if not self.match(TokenType.RPAREN):
                            self.expect(TokenType.COMMA)
                        else:
                            break
                self.expect(TokenType.RPAREN)
                expr = Call(expr, args)
            else:
                break
        return expr
    
    def parse_primary(self) -> Expr:
        """Parse: literals, identifiers, parenthesized expressions, if-expressions."""
        if self.match(TokenType.INT):
            token = self.advance()
            return IntLiteral(int(token.value))
        
        if self.match(TokenType.FLOAT):
            token = self.advance()
            return FloatLiteral(float(token.value))
        
        if self.match(TokenType.STRING):
            token = self.advance()
            return StringLiteral(token.value)
        
        if self.consume_if(TokenType.TRUE):
            return BoolLiteral(True)
        
        if self.consume_if(TokenType.FALSE):
            return BoolLiteral(False)
        
        if self.match(TokenType.IDENTIFIER):
            token = self.advance()
            return Ident(token.value)
        
        if self.consume_if(TokenType.LPAREN):
            expr = self.parse_expr()
            self.expect(TokenType.RPAREN)
            return expr
        
        if self.consume_if(TokenType.IF):
            condition = self.parse_expr()
            then_branch = self.parse_block()
            else_branch = None
            if self.consume_if(TokenType.ELSE):
                else_branch = self.parse_block()
            return IfExpr(condition, then_branch, else_branch)
        
        if self.match(TokenType.LBRACE):
            return self.parse_block()
        
        raise SyntaxError(f"Unexpected token: {self.current().type} at {self.current().line}:{self.current().col}")
    

def parse(tokens: List[Token]) -> Program:
    """Convenience function: parse tokens into AST."""
    parser = Parser(tokens)
    return parser.parse_program()


if __name__ == "__main__":
    # Test 1: Simple let binding
    code1 = "let x = 5;"
    print("Test 1:", code1)
    tokens1 = tokenize(code1)
    ast1 = parse(tokens1)
    print(ast1)
    print()
    
    # Test 2: Function definition
    code2 = "fn add(a: int, b: int) -> int { a + b }"
    print("Test 2:", code2)
    tokens2 = tokenize(code2)
    ast2 = parse(tokens2)
    print(ast2)
    print()
    
    # Test 3: If expression
    code3 = "if x > 5 { 10 } else { 20 }"
    print("Test 3:", code3)
    tokens3 = tokenize(code3)
    ast3 = parse(tokens3)
    print(ast3)
    print()
    
    # Test 4: Complex expression
    code4 = "let result = (x + 3) * 2;"
    print("Test 4:", code4)
    tokens4 = tokenize(code4)
    ast4 = parse(tokens4)
    print(ast4)
