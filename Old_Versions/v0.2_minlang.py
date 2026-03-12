"""
MinLang Interpreter — v0.2
Added arithmetic expressions with proper operator precedence.
Variables can now hold computed values.
New:  + - * /  operators, parenthesised expressions, pt/ptl distinction.
"""

import sys
import re

# ─── TOKENIZER ───────────────────────────────────────────────────

TOKEN_PATTERNS = [
    ('COMMENT',  r'##.*'),
    ('STRING',   r'"(?:[^"\\]|\\.)*"'),
    ('FLOAT',    r'\d+\.\d+'),
    ('INT',      r'\d+'),
    ('ASSIGN',   r'='),
    ('OP',       r'[+\-*/%]'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('NEWLINE',  r'\n'),
    ('INDENT',   r'[ \t]+'),
    ('IDENT',    r'[A-Za-z_][A-Za-z0-9_]*'),
]

def tokenize(code):
    tokens = []
    pos = 0
    while pos < len(code):
        matched = False
        for ttype, pattern in TOKEN_PATTERNS:
            m = re.match(pattern, code[pos:])
            if m:
                val = m.group(0)
                if ttype not in ('COMMENT', 'INDENT'):
                    tokens.append((ttype, val))
                pos += len(val)
                matched = True
                break
        if not matched:
            raise SyntaxError(f"Unknown character: '{code[pos]}'")
    return tokens


# ─── PARSER ──────────────────────────────────────────────────────
#
# Grammar (v0.2):
#   statement  := let | assign | print_stmt
#   let        := 'L' IDENT '=' expr
#   assign     := IDENT '=' expr
#   print_stmt := ('pt'|'ptl') expr
#
#   Expressions with precedence:
#   expr       := additive
#   additive   := multiplicative (('+' | '-') multiplicative)*
#   multiplicative := unary (('*' | '/' | '%') unary)*
#   unary      := '-' unary | primary
#   primary    := INT | FLOAT | STRING | IDENT | '(' expr ')'

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ('EOF', '')

    def advance(self):
        tok = self.current()
        self.pos += 1
        return tok

    def skip_newlines(self):
        while self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'NEWLINE':
            self.pos += 1

    def expect(self, ttype, val=None):
        self.skip_newlines()
        tok = self.advance()
        if tok[0] != ttype:
            raise SyntaxError(f"Expected {ttype} but got {tok}")
        if val and tok[1] != val:
            raise SyntaxError(f"Expected '{val}' but got '{tok[1]}'")
        return tok

    def parse(self):
        stmts = []
        while True:
            self.skip_newlines()
            if self.current()[0] == 'EOF':
                break
            stmt = self.parse_statement()
            if stmt:
                stmts.append(stmt)
        return ('BLOCK', stmts)

    def parse_statement(self):
        self.skip_newlines()
        tok = self.current()

        if tok[0] == 'IDENT' and tok[1] == 'L':
            self.advance()
            name = self.expect('IDENT')[1]
            self.expect('ASSIGN')
            val = self.parse_expr()
            return ('LET', name, val)

        if tok[0] == 'IDENT' and tok[1] == 'pt':
            self.advance()
            val = self.parse_expr()
            return ('PRINT', val, False)

        if tok[0] == 'IDENT' and tok[1] == 'ptl':
            self.advance()
            val = self.parse_expr()
            return ('PRINT', val, True)

        # Reassignment: IDENT = expr
        if tok[0] == 'IDENT':
            save = self.pos
            self.advance()
            if self.current()[0] == 'ASSIGN':
                self.advance()
                val = self.parse_expr()
                return ('ASSIGN', tok[1], val)
            else:
                self.pos = save

        raise SyntaxError(f"Unknown statement: {tok}")

    # ── Expression parsing with precedence ───────────────────────

    def parse_expr(self):
        return self.parse_additive()

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.current()[0] == 'OP' and self.current()[1] in ('+', '-'):
            op = self.advance()[1]
            right = self.parse_multiplicative()
            left = ('BINOP', op, left, right)
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.current()[0] == 'OP' and self.current()[1] in ('*', '/', '%'):
            op = self.advance()[1]
            right = self.parse_unary()
            left = ('BINOP', op, left, right)
        return left

    def parse_unary(self):
        if self.current()[0] == 'OP' and self.current()[1] == '-':
            self.advance()
            val = self.parse_unary()
            return ('UNOP', '-', val)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.current()
        if tok[0] == 'INT':
            self.advance()
            return ('INT', int(tok[1]))
        if tok[0] == 'FLOAT':
            self.advance()
            return ('FLOAT', float(tok[1]))
        if tok[0] == 'STRING':
            self.advance()
            val = tok[1][1:-1].replace('\\n', '\n').replace('\\t', '\t')
            return ('STRING', val)
        if tok[0] == 'IDENT':
            self.advance()
            return ('VAR', tok[1])
        if tok[0] == 'LPAREN':
            self.advance()
            expr = self.parse_expr()
            self.expect('RPAREN')
            return expr
        raise SyntaxError(f"Unexpected token: {tok}")


# ─── INTERPRETER ─────────────────────────────────────────────────

class Interpreter:
    def __init__(self):
        self.env = {}

    def run(self, ast):
        _, stmts = ast
        for stmt in stmts:
            self.exec_stmt(stmt)

    def exec_stmt(self, node):
        kind = node[0]

        if kind == 'LET':
            _, name, val_node = node
            self.env[name] = self.eval(val_node)

        elif kind == 'ASSIGN':
            _, name, val_node = node
            if name not in self.env:
                raise NameError(f"Variable '{name}' not defined. Use 'L {name} = ...' to declare it.")
            self.env[name] = self.eval(val_node)

        elif kind == 'PRINT':
            _, val_node, newline = node
            val = self.eval(val_node)
            print(self.to_str(val), end='\n' if newline else '')

    def eval(self, node):
        kind = node[0]
        if kind == 'INT':    return node[1]
        if kind == 'FLOAT':  return node[1]
        if kind == 'STRING': return node[1]
        if kind == 'VAR':
            name = node[1]
            if name not in self.env:
                raise NameError(f"Variable '{name}' is not defined")
            return self.env[name]
        if kind == 'BINOP':
            _, op, l, r = node
            lv, rv = self.eval(l), self.eval(r)
            if op == '+': return lv + rv
            if op == '-': return lv - rv
            if op == '*': return lv * rv
            if op == '/': return lv / rv
            if op == '%': return lv % rv
        if kind == 'UNOP':
            return -self.eval(node[2])
        raise RuntimeError(f"Unknown node: {node}")

    def to_str(self, val):
        return str(val)


# ─── RUNNER ──────────────────────────────────────────────────────

def run_code(source):
    try:
        tokens = tokenize(source)
        parser = Parser(tokens)
        ast    = parser.parse()
        interp = Interpreter()
        interp.run(ast)
    except (SyntaxError, NameError, TypeError, RuntimeError, ZeroDivisionError) as e:
        print(f"[Error] {e}", file=sys.stderr)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            src = open(sys.argv[1], encoding='utf-8').read()
        except FileNotFoundError:
            print(f"[Error] File not found: {sys.argv[1]}", file=sys.stderr)
            sys.exit(1)
        run_code(src)
    else:
        print("MinLang v0.2 — usage: python minlang.py <file.ll>")
