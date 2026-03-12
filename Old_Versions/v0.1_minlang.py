"""
MinLang Interpreter — v0.1
First concept. Variables and print only.
No expressions, no control flow, no functions.
Source files use the .ll extension.
"""

import sys
import re

# ─── TOKENIZER ───────────────────────────────────────────────────

TOKEN_PATTERNS = [
    ('COMMENT',  r'##.*'),
    ('STRING',   r'"(?:[^"\\]|\\.)*"'),
    ('INT',      r'\d+'),
    ('ASSIGN',   r'='),
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
# Grammar (v0.1):
#   program  := statement*
#   statement:= let | print
#   let      := 'L' IDENT '=' value
#   print    := 'pt' value
#   value    := INT | STRING | IDENT

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

    def expect(self, ttype):
        self.skip_newlines()
        tok = self.advance()
        if tok[0] != ttype:
            raise SyntaxError(f"Expected {ttype} but got {tok}")
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

        # L x = value
        if tok[0] == 'IDENT' and tok[1] == 'L':
            self.advance()
            name = self.expect('IDENT')[1]
            self.expect('ASSIGN')
            val = self.parse_value()
            return ('LET', name, val)

        # pt value
        if tok[0] == 'IDENT' and tok[1] == 'pt':
            self.advance()
            val = self.parse_value()
            return ('PRINT', val)

        raise SyntaxError(f"Unknown statement starting with: {tok}")

    def parse_value(self):
        tok = self.current()
        if tok[0] == 'INT':
            self.advance()
            return ('INT', int(tok[1]))
        if tok[0] == 'STRING':
            self.advance()
            val = tok[1][1:-1].replace('\\n', '\n').replace('\\t', '\t')
            return ('STRING', val)
        if tok[0] == 'IDENT':
            self.advance()
            return ('VAR', tok[1])
        raise SyntaxError(f"Expected a value but got {tok}")


# ─── INTERPRETER ─────────────────────────────────────────────────

class Interpreter:
    def __init__(self):
        self.env = {}   # flat global environment: name → value

    def run(self, ast):
        _, stmts = ast
        for stmt in stmts:
            self.exec_stmt(stmt)

    def exec_stmt(self, node):
        kind = node[0]

        if kind == 'LET':
            _, name, val_node = node
            self.env[name] = self.eval(val_node)

        elif kind == 'PRINT':
            _, val_node = node
            print(self.eval(val_node))

    def eval(self, node):
        kind = node[0]
        if kind == 'INT':    return node[1]
        if kind == 'STRING': return node[1]
        if kind == 'VAR':
            name = node[1]
            if name not in self.env:
                raise NameError(f"Variable '{name}' is not defined")
            return self.env[name]
        raise RuntimeError(f"Unknown node: {node}")


# ─── RUNNER ──────────────────────────────────────────────────────

def run_code(source):
    try:
        tokens = tokenize(source)
        parser = Parser(tokens)
        ast    = parser.parse()
        interp = Interpreter()
        interp.run(ast)
    except (SyntaxError, NameError, RuntimeError) as e:
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
        print("MinLang v0.1 — usage: python minlang.py <file.ll>")
