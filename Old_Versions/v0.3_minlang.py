"""
MinLang Interpreter — v0.3
Added conditionals (if / el) and comparison/logical operators.
Booleans (T / F) introduced as first-class values.
New keywords:  if  el  T  F
New operators: == != < > <= >= && ||  !
"""

import sys
import re

# ─── TOKENIZER ───────────────────────────────────────────────────

TOKEN_PATTERNS = [
    ('COMMENT',  r'##.*'),
    ('STRING',   r'"(?:[^"\\]|\\.)*"'),
    ('FLOAT',    r'\d+\.\d+'),
    ('INT',      r'\d+'),
    ('BOOL',     r'\b(T|F)\b'),
    # Two-char ops must come before single-char
    ('OP_EQ',    r'=='),
    ('OP_NEQ',   r'!='),
    ('OP_LTE',   r'<='),
    ('OP_GTE',   r'>='),
    ('OP_AND',   r'&&'),
    ('OP_OR',    r'\|\|'),
    ('OP_NOT',   r'!(?!=)'),
    ('ASSIGN',   r'='),
    ('OP',       r'[+\-*/%<>]'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('LBRACE',   r'\{'),
    ('RBRACE',   r'\}'),
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
# Grammar additions (v0.3):
#   statement  += if_stmt
#   if_stmt    := 'if' expr block ('el' block)?
#   block      := '{' statement* '}'
#
#   Expressions with precedence (lowest→highest):
#   expr       := or
#   or         := and ('||' and)*
#   and        := compare ('&&' compare)*
#   compare    := additive (cmpop additive)?
#   additive   := multiplicative (('+' | '-') multiplicative)*
#   ...

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

    def parse_block(self):
        self.expect('LBRACE')
        stmts = []
        while True:
            self.skip_newlines()
            if self.current()[0] == 'RBRACE':
                self.advance()
                break
            if self.current()[0] == 'EOF':
                raise SyntaxError("Unclosed block — missing '}'")
            stmts.append(self.parse_statement())
        return ('BLOCK', stmts)

    def parse_statement(self):
        self.skip_newlines()
        tok = self.current()

        if tok[0] == 'IDENT' and tok[1] == 'L':
            self.advance()
            name = self.expect('IDENT')[1]
            self.expect('ASSIGN')
            return ('LET', name, self.parse_expr())

        if tok[0] == 'IDENT' and tok[1] == 'pt':
            self.advance()
            return ('PRINT', self.parse_expr(), False)

        if tok[0] == 'IDENT' and tok[1] == 'ptl':
            self.advance()
            return ('PRINT', self.parse_expr(), True)

        if tok[0] == 'IDENT' and tok[1] == 'if':
            return self.parse_if()

        # Reassignment
        if tok[0] == 'IDENT':
            save = self.pos
            self.advance()
            if self.current()[0] == 'ASSIGN':
                self.advance()
                return ('ASSIGN', tok[1], self.parse_expr())
            self.pos = save

        # Expression statement (e.g. bare call in future versions)
        expr = self.parse_expr()
        return ('EXPR_STMT', expr)

    def parse_if(self):
        self.advance()   # consume 'if'
        cond = self.parse_expr()
        body = self.parse_block()
        else_body = None
        self.skip_newlines()
        if self.current()[0] == 'IDENT' and self.current()[1] == 'el':
            self.advance()
            else_body = self.parse_block()
        return ('IF', cond, body, [], else_body)

    # ── Expression levels ────────────────────────────────────────

    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.current()[0] == 'OP_OR':
            self.advance()
            left = ('BINOP', '||', left, self.parse_and())
        return left

    def parse_and(self):
        left = self.parse_compare()
        while self.current()[0] == 'OP_AND':
            self.advance()
            left = ('BINOP', '&&', left, self.parse_compare())
        return left

    def parse_compare(self):
        left = self.parse_additive()
        while self.current()[0] in ('OP_EQ', 'OP_NEQ', 'OP_LTE', 'OP_GTE', 'OP'):
            op = self.current()[1]
            if op in ('==', '!=', '<=', '>=', '<', '>'):
                self.advance()
                left = ('BINOP', op, left, self.parse_additive())
            else:
                break
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.current()[0] == 'OP' and self.current()[1] in ('+', '-'):
            op = self.advance()[1]
            left = ('BINOP', op, left, self.parse_multiplicative())
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.current()[0] == 'OP' and self.current()[1] in ('*', '/', '%'):
            op = self.advance()[1]
            left = ('BINOP', op, left, self.parse_unary())
        return left

    def parse_unary(self):
        if self.current()[0] == 'OP' and self.current()[1] == '-':
            self.advance()
            return ('UNOP', '-', self.parse_unary())
        if self.current()[0] == 'OP_NOT':
            self.advance()
            return ('UNOP', '!', self.parse_unary())
        return self.parse_primary()

    def parse_primary(self):
        tok = self.current()
        if tok[0] == 'INT':
            self.advance(); return ('INT', int(tok[1]))
        if tok[0] == 'FLOAT':
            self.advance(); return ('FLOAT', float(tok[1]))
        if tok[0] == 'BOOL':
            self.advance(); return ('BOOL', tok[1] == 'T')
        if tok[0] == 'STRING':
            self.advance()
            val = tok[1][1:-1].replace('\\n', '\n').replace('\\t', '\t')
            return ('STRING', val)
        if tok[0] == 'IDENT':
            self.advance(); return ('VAR', tok[1])
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
        self.exec_block(ast)

    def exec_block(self, node):
        _, stmts = node
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
                raise NameError(f"Undefined variable '{name}'")
            self.env[name] = self.eval(val_node)

        elif kind == 'PRINT':
            _, val_node, newline = node
            print(self.to_str(self.eval(val_node)), end='\n' if newline else '')

        elif kind == 'IF':
            _, cond, body, _, else_body = node
            if self.eval(cond):
                self.exec_block(body)
            elif else_body:
                self.exec_block(else_body)

        elif kind == 'EXPR_STMT':
            self.eval(node[1])

    def eval(self, node):
        kind = node[0]
        if kind == 'INT':    return node[1]
        if kind == 'FLOAT':  return node[1]
        if kind == 'BOOL':   return node[1]
        if kind == 'STRING': return node[1]
        if kind == 'VAR':
            if node[1] not in self.env:
                raise NameError(f"Variable '{node[1]}' is not defined")
            return self.env[node[1]]
        if kind == 'BINOP':
            _, op, l, r = node
            lv, rv = self.eval(l), self.eval(r)
            if op == '+':  return lv + rv
            if op == '-':  return lv - rv
            if op == '*':  return lv * rv
            if op == '/':  return lv / rv
            if op == '%':  return lv % rv
            if op == '<':  return lv < rv
            if op == '>':  return lv > rv
            if op == '<=': return lv <= rv
            if op == '>=': return lv >= rv
            if op == '==': return lv == rv
            if op == '!=': return lv != rv
            if op == '&&': return lv and rv
            if op == '||': return lv or rv
        if kind == 'UNOP':
            _, op, val = node
            v = self.eval(val)
            if op == '-': return -v
            if op == '!': return not v
        raise RuntimeError(f"Unknown node: {node}")

    def to_str(self, val):
        if val is True:  return "T"
        if val is False: return "F"
        return str(val)


# ─── RUNNER ──────────────────────────────────────────────────────

def run_code(source):
    try:
        tokens = tokenize(source)
        ast    = Parser(tokens).parse()
        Interpreter().run(ast)
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
        print("MinLang v0.3 — usage: python minlang.py <file.ll>")
