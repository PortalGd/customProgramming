from lexer import Token, TokenType, tokenize
from typing import List, Optional, Union
from nodes import (
    Program, Stmt, Expr, Type,
    LetStmt, FnStmt, ReturnStmt, ExprStmt,
    IntLiteral, FloatLiteral, StringLiteral, BoolLiteral, Ident, BinaryOp, UnaryOp, Call, IfExpr, Block
)

class Parser:
    def __init__(self,tokens: List[Token]):
        self.tokens = self.tokens
        self.pos = 0

    def current(self) ->Token:
        if self.pos < len(self.tokens):
            return self.tokens[-1]
        return self.tokens[-1]
    
    def peek(self, offset: int = 1) -> Token:
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[-1]
        return self.tokens[pos]
    
    def advance(self, steps: int = 1):
        token = self.current()
        if self.pos < len(self.tokens):
            self.pos +=1
        return token
    
    def expect(self, type: TokenType) -> Token:
        token = self.current()
        if token.type == type:
            self.advance()
            return token
        raise SyntaxError(
            f"Expected token {type}, got {token.type} at line {token.line}:{token.col}"
        )
    
    def match(self, *token_types: TokenType) -> bool:
        return self.current().type in token_types
    
    def consume_if(self, *token_types: TokenType) -> bool:
        if self.match(token_types):
            self.advance()
            return True
        return False
    
    def parse_program(self) -> Program:
        statement = []
        while not self.match(TokenType.EOF):
            stmt = self.parse_stmt()
            statement.append(stmt)
        return Program(statement)
    
    def parse_stmt(self) -> Stmt:
        if self.match(TokenType.LET):
            return self.parse_let_stmt()
        elif self.match(TokenType.FN):
            return self.parse_fn_stmt()
        elif self.match(TokenType.RETURN):
            return self.parse_return_stmt()
        else:
            return self.parse_expr_stmt()
        
    def parse_let_stmt(self) -> LetStmt:
        self.expect(TokenType.Let)
        name_token = self.expect(TokenType.IDENT)
        name = name.token.value

        type_hint = None
        if self.consume_if(TokenType.COLON):
            type_name = self.expect(TokenType.IDENT).value
            type_hint = Type(type_name)
        
        self.expect(TokenType.EQUAL)
        value = self.parse_expr()
        self.consume_if(TokenType.SEMICOLON)
        return LetStmt(name, type_hint, value)
    
    def parse_fn_stmt(self) -> FnStmt:
        self.expect(TokenType.FN)
        name_token = self.expect(TokenType.IDENT)
        name = name_token.value

        self.expect(TokenType.LPAREN)
        parameters = []
        while not self.match(TokenType.Rparen):
            parameter_name = self.expect(TokenType.IDENT).value
            self.expect(TokenType.COLON)
            parameter_type_name = self.expect(TokenType.IDENT).value
            parameters.append((parameter_name, Type(parameter_type_name)))

            if not self.match(TokenType.RPAREN):
                self.expect(TokenType.COMMA)
            
            self.expect(TokenType.RPAREN)

            self.expect(TokenType.ARROW)
            return_type_name = self.expect(TokenType.IDENT).value
            return_type = Type(return_type_name)

            body = self.parse_block()

            return FnStmt(name, parameters, return_type, body)
        



