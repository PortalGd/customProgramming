# nodes.py
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Type:
    """A type annotation."""
    name: str


@dataclass
class Expr:
    """Base class for expressions."""
    pass


@dataclass
class IntLiteral(Expr):
    value: int


@dataclass
class FloatLiteral(Expr):
    value: float


@dataclass
class StringLiteral(Expr):
    value: str


@dataclass
class BoolLiteral(Expr):
    value: bool


@dataclass
class Ident(Expr):
    name: str


@dataclass
class BinaryOp(Expr):
    left: Expr
    op: str
    right: Expr


@dataclass
class UnaryOp(Expr):
    op: str
    expr: Expr


@dataclass
class Call(Expr):
    func: Expr
    args: List[Expr]


@dataclass
class IfExpr(Expr):
    cond: Expr
    then_body: 'Block'
    else_body: Optional['Block'] = None


@dataclass
class Block(Expr):
    stmts: List['Stmt']


# Statements

@dataclass
class Stmt:
    """Base class for statements."""
    pass


@dataclass
class LetStmt(Stmt):
    name: str
    type_hint: Optional[Type]
    value: Expr


@dataclass
class FnStmt(Stmt):
    name: str
    params: List[tuple]
    return_type: Type
    body: Block


@dataclass
class ReturnStmt(Stmt):
    value: Optional[Expr] = None


@dataclass
class ExprStmt(Stmt):
    expr: Expr


@dataclass
class Program:
    """Root node: entire program."""
    stmts: List[Stmt]
