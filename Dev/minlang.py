"""
MinLang Interpreter — v1.3
A minimalist programming language. Maximum power, minimum keystrokes.
Source files use the .minl extension.

New in v1.3:
    ✦ Struct inheritance:   struct Cat extends Animal { ... }
    ✦ super keyword:        super.method(args)  inside child methods
    ✦ instanceof hierarchy: instanceof(cat, Animal) → T  (walks chain)
    ✦ Module namespaces:    import "utils.minl" as utils
                            utils.myFunc()  /  utils.myVar
    ✦ export keyword:       export myFunc   (inside module file)
                            (if no exports declared → all names exported)
    ✦ throw / typed errors: throw "oops"
                            throw MyError("msg")   (any value)
                            try { } catch e { }    e holds the thrown value
    ✦ Integer division:     17 // 5  → 3
    ✦ Bitwise operators:    & | ^ ~ << >>
    ✦ Deep recursion:       Python recursion limit raised to 10 000

Architecture:
    Source code (.minl file)
        │
        ▼
    Tokenizer  ── turns raw text into a flat list of (type, value, line) tokens
        │
        ▼
    Parser     ── turns tokens into an Abstract Syntax Tree (AST)
        │            statements are wrapped with SOURCELOC for line tracking
        ▼
    Interpreter── walks the AST and executes each node;
                tracks current line for runtime error reporting
"""

import sys
import re
import math
import os

# Raise Python's recursion limit so MinLang programs can recurse deeper.
# Each MinLang call uses ~8 internal Python frames, so we multiply accordingly.
sys.setrecursionlimit(50_000)


# ═══════════════════════════════════════════════════════════════
#  STAGE 1 — TOKENIZER
#  Reads raw source text and groups characters into named tokens.
#  Each token is now a (type, value, line) triple so that both
#  the parser and the interpreter can report accurate positions.
# ═══════════════════════════════════════════════════════════════

TOKEN_PATTERNS = [
    # Comments
    ('COMMENT',      r'##.*'),

    # Multiline strings MUST come before regular strings
    ('MLSTRING',     r'"""[\s\S]*?"""'),

    # F-strings and regular strings
    ('FSTRING',      r'f"(?:[^"\\]|\\.)*"'),
    ('STRING',       r'"(?:[^"\\]|\\.)*"'),

    # Numbers (floats before ints so 3.14 isn't split)
    ('FLOAT',        r'\d+\.\d+'),
    ('INT',          r'\d+'),

    # Booleans
    ('BOOL',         r'\b(T|F)\b'),

    # ── Multi-character operators (must precede single-char) ───

    # Power: ** before *
    ('OP_POW',       r'\*\*'),

    # Comparisons
    ('OP_EQ',        r'=='),
    ('OP_NEQ',       r'!='),
    ('OP_LTE',       r'<='),
    ('OP_GTE',       r'>='),
    ('OP_AND',       r'&&'),
    ('OP_OR',        r'\|\|'),

    # Compound assignment (before plain = and plain operators)
    ('PLUS_ASSIGN',  r'\+='),
    ('MINUS_ASSIGN', r'-='),
    ('MUL_ASSIGN',   r'\*='),
    ('DIV_ASSIGN',   r'/='),
    ('MOD_ASSIGN',   r'%='),

    # Logical NOT: ! but NOT !=
    ('OP_NOT',       r'!(?!=)'),

    # Arrow (reserved)
    ('ARROW',        r'->'),

    # Nil-safe dot (?.) before plain ?
    ('SAFE_DOT',     r'\?\.'),

    # Plain assignment
    ('ASSIGN',       r'='),

    # ── v1.3: bitwise / integer-division (before single-char OP) ──
    # Integer division //  before single /
    ('OP_IDIV',      r'//'),
    # Bit shifts << >> before < >
    ('OP_LSHIFT',    r'<<'),
    ('OP_RSHIFT',    r'>>'),
    # Bitwise AND &  (after &&)
    ('OP_BAND',      r'&'),
    # Bitwise OR  |  (after ||)
    ('OP_BOR',       r'\|'),
    # Bitwise XOR ^
    ('OP_BXOR',      r'\^'),
    # Bitwise NOT ~ (unary)
    ('OP_BNOT',      r'~'),

    # Arithmetic / comparison
    ('OP',           r'[+\-*/%<>]'),

    # Ternary question mark
    ('QMARK',        r'\?'),

    # Brackets and punctuation
    ('LPAREN',       r'\('),
    ('RPAREN',       r'\)'),
    ('LBRACE',       r'\{'),
    ('RBRACE',       r'\}'),
    ('LBRACKET',     r'\['),
    ('RBRACKET',     r'\]'),
    ('COMMA',        r','),
    ('COLON',        r':'),
    ('DOT',          r'\.'),

    # Newlines kept as tokens
    ('NEWLINE',      r'\n'),

    # Whitespace silently discarded
    ('INDENT',       r'[ \t]+'),

    # Identifiers — LAST so keywords aren't swallowed earlier
    ('IDENT',        r'[A-Za-z_][A-Za-z0-9_]*'),
]


def tokenize(code):
    """
    Convert a source string into a list of (type, value, line) token triples.
    Line numbers start at 1 and are bumped on every newline character.
    Raises SyntaxError on unrecognised characters.
    """
    tokens = []
    pos    = 0
    line   = 1
    while pos < len(code):
        matched = False
        for ttype, pattern in TOKEN_PATTERNS:
            m = re.match(pattern, code[pos:])
            if m:
                val = m.group(0)
                if ttype not in ('COMMENT', 'INDENT'):
                    tokens.append((ttype, val, line))
                # Advance line counter by any newlines inside the matched text
                # (handles multiline strings, comments with \n, and plain NEWLINE)
                line += val.count('\n')
                pos  += len(val)
                matched = True
                break
        if not matched:
            raise SyntaxError(f"[line {line}] Unknown character: '{code[pos]}'")
    return tokens


# ═══════════════════════════════════════════════════════════════
#  STAGE 2 — PARSER
#
#  Operator precedence (lowest → highest):
#    ternary (?:)  →  ||  →  &&
#    →  | (bor)  →  ^ (bxor)  →  & (band)     ← v1.3
#    →  comparisons (== != < > <= >=)
#    →  << >>  (shifts)                        ← v1.3
#    →  +/-  →  */% //  →  ** (right-assoc)
#    →  unary (-/!/~)  →  postfix  →  primary
#
#  v1.3: tokens are now (type, value, line) triples.
#        Helper current_line() exposes the line of the current token.
#        All SyntaxErrors include the offending line number.
#        Statements in every block are wrapped in SOURCELOC nodes
#        so the interpreter can track lines at runtime too.
# ═══════════════════════════════════════════════════════════════

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos    = 0

    # ── Navigation helpers ──────────────────────────────────────

    def skip_newlines(self):
        while self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'NEWLINE':
            self.pos += 1

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ('EOF', '', 0)

    def current_line(self):
        """Return the source line of the current token (1-based)."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos][2]
        if self.tokens:
            return self.tokens[-1][2]
        return 1

    def advance(self):
        tok = self.current()
        self.pos += 1
        return tok

    def expect(self, ttype, val=None):
        self.skip_newlines()
        tok = self.advance()
        if tok[0] != ttype:
            raise SyntaxError(
                f"[line {tok[2]}] Expected {ttype} but got '{tok[1]}'"
            )
        if val and tok[1] != val:
            raise SyntaxError(
                f"[line {tok[2]}] Expected '{val}' but got '{tok[1]}'"
            )
        return tok

    # ── Top-level entry point ────────────────────────────────────

    def parse(self):
        stmts = []
        while True:
            self.skip_newlines()
            if self.current()[0] == 'EOF':
                break
            line = self.current_line()
            stmt = self.parse_statement()
            if stmt:
                stmts.append(('SOURCELOC', line, stmt))
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
                raise SyntaxError(
                    f"[line {self.current_line()}] Unclosed block — missing '}}'"
                )
            line = self.current_line()
            stmt = self.parse_statement()
            if stmt:
                stmts.append(('SOURCELOC', line, stmt))
        return ('BLOCK', stmts)

    # ── Statement dispatcher ─────────────────────────────────────

    def parse_statement(self):
        self.skip_newlines()
        tok = self.current()

        if tok[0] == 'EOF':
            return None

        # ── use "file.minl"  →  module import (legacy, runs in current scope) ──
        if tok[0] == 'IDENT' and tok[1] == 'use':
            self.advance()
            path = self.parse_expr()
            return ('USE', path)

        # ── import "file.minl" as name  →  module with namespace  (v1.3) ─────
        if tok[0] == 'IDENT' and tok[1] == 'import':
            self.advance()
            path = self.parse_expr()
            self.expect('IDENT', 'as')
            alias = self.expect('IDENT')[1]
            return ('IMPORT', path, alias)

        # ── export name  →  mark variable as exported from module  (v1.3) ────
        if tok[0] == 'IDENT' and tok[1] == 'export':
            self.advance()
            name = self.expect('IDENT')[1]
            return ('EXPORT', name)

        # ── throw expr  →  raise a MinLang error  (v1.3) ─────────────────────
        if tok[0] == 'IDENT' and tok[1] == 'throw':
            self.advance()
            return ('THROW', self.parse_expr())

        # ── struct  →  OOP class definition ──────────────────────
        if tok[0] == 'IDENT' and tok[1] == 'struct':
            return self.parse_struct()

        # ── L  →  variable declaration (plain / destructuring) ───
        if tok[0] == 'IDENT' and tok[1] == 'L':
            self.advance()
            # List destructuring: L [a, b, *rest] = expr
            if self.current()[0] == 'LBRACKET':
                self.advance()
                names     = []
                rest_name = None
                while self.current()[0] != 'RBRACKET':
                    if self.current()[0] == 'OP' and self.current()[1] == '*':
                        self.advance()
                        rest_name = self.expect('IDENT')[1]
                    else:
                        names.append(self.expect('IDENT')[1])
                    if self.current()[0] == 'COMMA':
                        self.advance()
                self.expect('RBRACKET')
                self.expect('ASSIGN')
                val = self.parse_expr()
                return ('DESTRUCT_LIST', names, rest_name, val)
            # Dict destructuring: L {a, b} = expr
            elif self.current()[0] == 'LBRACE':
                self.advance()
                names = []
                while self.current()[0] != 'RBRACE':
                    names.append(self.expect('IDENT')[1])
                    if self.current()[0] == 'COMMA':
                        self.advance()
                self.expect('RBRACE')
                self.expect('ASSIGN')
                val = self.parse_expr()
                return ('DESTRUCT_DICT', names, val)
            # Regular: L x = expr
            else:
                name = self.expect('IDENT')[1]
                self.expect('ASSIGN')
                val = self.parse_expr()
                return ('LET', name, val)

        # ── pt / ptl ─────────────────────────────────────────────
        if tok[0] == 'IDENT' and tok[1] == 'pt':
            self.advance()
            return ('PRINT', self.parse_expr(), False)

        if tok[0] == 'IDENT' and tok[1] == 'ptl':
            self.advance()
            return ('PRINT', self.parse_expr(), True)

        # ── inp ───────────────────────────────────────────────────
        if tok[0] == 'IDENT' and tok[1] == 'inp':
            self.advance()
            prompt = None
            if self.current()[0] in ('STRING', 'FSTRING', 'MLSTRING'):
                prompt = self.parse_expr()
            name = self.expect('IDENT')[1]
            return ('INPUT', name, prompt)

        # ── Control flow keywords ─────────────────────────────────
        if tok[0] == 'IDENT' and tok[1] == 'if':
            return self.parse_if()

        if tok[0] == 'IDENT' and tok[1] == 'lp':
            return self.parse_loop()

        if tok[0] == 'IDENT' and tok[1] == 'wh':
            return self.parse_while()

        if tok[0] == 'IDENT' and tok[1] == 'fn':
            return self.parse_fn()

        if tok[0] == 'IDENT' and tok[1] == 'rt':
            self.advance()
            return ('RETURN', self.parse_expr())

        if tok[0] == 'IDENT' and tok[1] == 'brk':
            self.advance()
            return ('BREAK',)

        if tok[0] == 'IDENT' and tok[1] == 'cnt':
            self.advance()
            return ('CONTINUE',)

        if tok[0] == 'IDENT' and tok[1] == 'try':
            return self.parse_try()

        # ── Assignment / compound assignment / index+attr assign ──
        if tok[0] == 'IDENT':
            save = self.pos
            self.advance()

            compound_ops = {
                'PLUS_ASSIGN':  '+',
                'MINUS_ASSIGN': '-',
                'MUL_ASSIGN':   '*',
                'DIV_ASSIGN':   '/',
                'MOD_ASSIGN':   '%',
            }

            # Simple assignment:  x = expr
            if self.current()[0] == 'ASSIGN':
                self.advance()
                return ('ASSIGN', tok[1], self.parse_expr())

            # Compound assignment:  x += expr  etc.
            if self.current()[0] in compound_ops:
                op = compound_ops[self.current()[0]]
                self.advance()
                return ('COMPOUND_ASSIGN', tok[1], op, self.parse_expr())

            # Index assignment:  x[i] = val
            if self.current()[0] == 'LBRACKET':
                self.advance()
                idx = self.parse_expr()
                self.expect('RBRACKET')
                if self.current()[0] == 'ASSIGN':
                    self.advance()
                    return ('INDEX_ASSIGN', tok[1], idx, self.parse_expr())
                else:
                    self.pos = save   # not an assignment, rewind

            # Attribute assignment / compound attr assignment:
            #   x.attr = val   and   self.x += val  (inside methods)
            elif self.current()[0] == 'DOT':
                self.advance()            # consume dot
                if self.current()[0] == 'IDENT':
                    attr_name = self.advance()[1]
                    if self.current()[0] == 'ASSIGN':
                        self.advance()
                        return ('ATTR_ASSIGN', tok[1], attr_name, self.parse_expr())
                    if self.current()[0] in compound_ops:
                        op = compound_ops[self.current()[0]]
                        self.advance()
                        return ('ATTR_COMPOUND_ASSIGN', tok[1], attr_name, op, self.parse_expr())
                # Not a bare attr assignment — fall through to expression
                self.pos = save

            else:
                self.pos = save           # not any assignment, rewind

        # Fallthrough: expression used as statement
        return ('EXPR_STMT', self.parse_expr())

    # ── Control-flow parsers ──────────────────────────────────────

    def parse_if(self):
        self.advance()
        cond      = self.parse_expr()
        body      = self.parse_block()
        elifs     = []
        else_body = None
        while True:
            self.skip_newlines()
            if self.current()[0] == 'IDENT' and self.current()[1] == 'elif':
                self.advance()
                elifs.append((self.parse_expr(), self.parse_block()))
            elif self.current()[0] == 'IDENT' and self.current()[1] == 'el':
                self.advance()
                else_body = self.parse_block()
                break
            else:
                break
        return ('IF', cond, body, elifs, else_body)

    def parse_loop(self):
        self.advance()
        var      = self.expect('IDENT')[1]
        self.expect('IDENT', 'in')
        iterable = self.parse_expr()
        body     = self.parse_block()
        return ('FOR', var, iterable, body)

    def parse_while(self):
        self.advance()
        return ('WHILE', self.parse_expr(), self.parse_block())

    def parse_fn(self):
        self.advance()
        name     = self.expect('IDENT')[1]
        self.expect('LPAREN')
        params   = []
        variadic = None
        while self.current()[0] != 'RPAREN':
            if self.current()[0] == 'OP' and self.current()[1] == '*':
                self.advance()
                variadic = self.expect('IDENT')[1]
            else:
                params.append(self.expect('IDENT')[1])
            if self.current()[0] == 'COMMA':
                self.advance()
        self.expect('RPAREN')
        return ('FUNCDEF', name, params, self.parse_block(), variadic)

    def parse_try(self):
        self.advance()                  # consume 'try'
        body    = self.parse_block()
        self.skip_newlines()
        self.expect('IDENT', 'catch')
        err_var = self.expect('IDENT')[1]
        return ('TRY', body, err_var, self.parse_block())

    def parse_struct(self):
        """
        struct Name { fn init(...) { } fn method() { } }
        v1.3: struct Child extends Parent { ... }
        'self' is injected automatically — do NOT include it in param lists.
        'super' is available inside child methods to call parent methods.
        """
        self.advance()                  # consume 'struct'
        name = self.expect('IDENT')[1]

        # ── v1.3: optional inheritance ────────────────────────────
        parent_name = None
        self.skip_newlines()
        if self.current()[0] == 'IDENT' and self.current()[1] == 'extends':
            self.advance()              # consume 'extends'
            parent_name = self.expect('IDENT')[1]

        self.expect('LBRACE')
        methods = {}                    # method_name → (params, body, variadic)
        while True:
            self.skip_newlines()
            if self.current()[0] == 'RBRACE':
                self.advance()
                break
            if self.current()[0] == 'EOF':
                raise SyntaxError(
                    f"[line {self.current_line()}] Unclosed struct '{name}' — missing '}}'"
                )
            if not (self.current()[0] == 'IDENT' and self.current()[1] == 'fn'):
                raise SyntaxError(
                    f"[line {self.current_line()}] Expected method definition inside struct '{name}'"
                )
            fn_node = self.parse_fn()   # ('FUNCDEF', fname, params, body, variadic)
            _, fname, params, body, variadic = fn_node
            if fname in methods:
                raise SyntaxError(
                    f"Duplicate method '{fname}' in struct '{name}'"
                )
            methods[fname] = (params, body, variadic)
        return ('STRUCTDEF', name, parent_name, methods)

    # ── Expression parsing (recursive descent) ───────────────────
    #
    #  parse_expr
    #    └─ parse_ternary    (?:)
    #         └─ parse_or        (||)
    #              └─ parse_and      (&&)
    #                   └─ parse_bor      (|)         ← v1.3
    #                        └─ parse_bxor     (^)    ← v1.3
    #                             └─ parse_band     (&)  ← v1.3
    #                                  └─ parse_compare  (== != < > <= >=)
    #                                       └─ parse_shift   (<< >>)  ← v1.3
    #                                            └─ parse_additive (+-)
    #                                                 └─ parse_multiplicative (* / // %)
    #                                                      └─ parse_power (**,right-assoc)
    #                                                           └─ parse_unary (-/!/~)
    #                                                                └─ parse_postfix
    #                                                                     └─ parse_primary

    def parse_expr(self):
        return self.parse_ternary()

    def parse_ternary(self):
        cond = self.parse_or()
        if self.current()[0] == 'QMARK':
            self.advance()
            true_val  = self.parse_or()
            self.expect('COLON')
            false_val = self.parse_or()
            return ('TERNARY', cond, true_val, false_val)
        return cond

    def parse_or(self):
        left = self.parse_and()
        while self.current()[0] == 'OP_OR':
            self.advance()
            left = ('BINOP', '||', left, self.parse_and())
        return left

    def parse_and(self):
        left = self.parse_bor()
        while self.current()[0] == 'OP_AND':
            self.advance()
            left = ('BINOP', '&&', left, self.parse_bor())
        return left

    # ── v1.3: bitwise OR / XOR / AND ─────────────────────────────

    def parse_bor(self):
        left = self.parse_bxor()
        while self.current()[0] == 'OP_BOR':
            self.advance()
            left = ('BINOP', '|', left, self.parse_bxor())
        return left

    def parse_bxor(self):
        left = self.parse_band()
        while self.current()[0] == 'OP_BXOR':
            self.advance()
            left = ('BINOP', '^', left, self.parse_band())
        return left

    def parse_band(self):
        left = self.parse_compare()
        while self.current()[0] == 'OP_BAND':
            self.advance()
            left = ('BINOP', '&', left, self.parse_compare())
        return left

    # ── comparisons ───────────────────────────────────────────────

    def parse_compare(self):
        left = self.parse_shift()
        while self.current()[0] in ('OP_EQ', 'OP_NEQ', 'OP_LTE', 'OP_GTE', 'OP'):
            op = self.current()[1]
            if op in ('==', '!=', '<=', '>=', '<', '>'):
                self.advance()
                left = ('BINOP', op, left, self.parse_shift())
            else:
                break
        return left

    # ── v1.3: bit shifts ─────────────────────────────────────────

    def parse_shift(self):
        left = self.parse_additive()
        while self.current()[0] in ('OP_LSHIFT', 'OP_RSHIFT'):
            op = '<<' if self.current()[0] == 'OP_LSHIFT' else '>>'
            self.advance()
            left = ('BINOP', op, left, self.parse_additive())
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.current()[0] == 'OP' and self.current()[1] in ('+', '-'):
            left = ('BINOP', self.advance()[1], left, self.parse_multiplicative())
        return left

    def parse_multiplicative(self):
        left = self.parse_power()
        while True:
            tok = self.current()
            if tok[0] == 'OP' and tok[1] in ('*', '/', '%'):
                left = ('BINOP', self.advance()[1], left, self.parse_power())
            elif tok[0] == 'OP_IDIV':           # v1.3: //
                self.advance()
                left = ('BINOP', '//', left, self.parse_power())
            else:
                break
        return left

    def parse_power(self):
        """Right-associative:  2 ** 3 ** 2  ==  2 ** (3 ** 2)"""
        base = self.parse_unary()
        if self.current()[0] == 'OP_POW':
            self.advance()
            return ('BINOP', '**', base, self.parse_power())
        return base

    def parse_unary(self):
        if self.current()[0] == 'OP' and self.current()[1] == '-':
            self.advance()
            return ('UNOP', '-', self.parse_unary())
        if self.current()[0] == 'OP_NOT':
            self.advance()
            return ('UNOP', '!', self.parse_unary())
        if self.current()[0] == 'OP_BNOT':      # v1.3: ~
            self.advance()
            return ('UNOP', '~', self.parse_unary())
        return self.parse_postfix()

    def parse_postfix(self):
        """
        Left-associative postfix:
          call        expr(args)
          index       expr[i]
          slice       expr[a:b]  expr[:b]  expr[a:]  expr[:]
          method      expr.method(args)
          attr        expr.attr
          nil-safe    expr?.method()   expr?.attr
        """
        node = self.parse_primary()

        while True:
            # ── Function call ──────────────────────────────────
            if self.current()[0] == 'LPAREN':
                self.advance()
                args = []
                while self.current()[0] != 'RPAREN':
                    args.append(self.parse_expr())
                    if self.current()[0] == 'COMMA':
                        self.advance()
                self.expect('RPAREN')
                node = ('CALL', node, args)

            # ── Index or slice ─────────────────────────────────
            elif self.current()[0] == 'LBRACKET':
                self.advance()
                if self.current()[0] == 'COLON':
                    # [:stop] or [:]
                    self.advance()
                    stop = None if self.current()[0] == 'RBRACKET' else self.parse_expr()
                    self.expect('RBRACKET')
                    node = ('SLICE', node, None, stop)
                else:
                    first = self.parse_expr()
                    if self.current()[0] == 'COLON':
                        # [start:stop] or [start:]
                        self.advance()
                        stop = None if self.current()[0] == 'RBRACKET' else self.parse_expr()
                        self.expect('RBRACKET')
                        node = ('SLICE', node, first, stop)
                    else:
                        self.expect('RBRACKET')
                        node = ('INDEX', node, first)

            # ── Regular dot ────────────────────────────────────
            elif self.current()[0] == 'DOT':
                self.advance()
                attr = self.expect('IDENT')[1]
                if self.current()[0] == 'LPAREN':
                    self.advance()
                    args = []
                    while self.current()[0] != 'RPAREN':
                        args.append(self.parse_expr())
                        if self.current()[0] == 'COMMA':
                            self.advance()
                    self.expect('RPAREN')
                    node = ('METHOD', node, attr, args)
                else:
                    node = ('ATTR', node, attr)

            # ── Nil-safe dot ───────────────────────────────────
            elif self.current()[0] == 'SAFE_DOT':
                self.advance()
                attr = self.expect('IDENT')[1]
                if self.current()[0] == 'LPAREN':
                    self.advance()
                    args = []
                    while self.current()[0] != 'RPAREN':
                        args.append(self.parse_expr())
                        if self.current()[0] == 'COMMA':
                            self.advance()
                    self.expect('RPAREN')
                    node = ('SAFE_METHOD', node, attr, args)
                else:
                    node = ('SAFE_ATTR', node, attr)

            else:
                break

        return node

    def parse_primary(self):
        tok = self.current()

        if tok[0] == 'INT':
            self.advance()
            return ('INT', int(tok[1]))

        if tok[0] == 'FLOAT':
            self.advance()
            return ('FLOAT', float(tok[1]))

        if tok[0] == 'BOOL':
            self.advance()
            return ('BOOL', tok[1] == 'T')

        if tok[0] == 'STRING':
            self.advance()
            val = tok[1][1:-1].replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"')
            return ('STRING', val)

        if tok[0] == 'MLSTRING':
            self.advance()
            val = tok[1][3:-3].replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"')
            return ('STRING', val)

        if tok[0] == 'FSTRING':
            self.advance()
            return ('FSTRING', tok[1][2:-1])

        if tok[0] == 'IDENT':
            if tok[1] == 'nil':
                self.advance()
                return ('NIL',)
            # Anonymous function: fn(params) { body }
            if tok[1] == 'fn':
                self.advance()
                self.expect('LPAREN')
                params   = []
                variadic = None
                while self.current()[0] != 'RPAREN':
                    if self.current()[0] == 'OP' and self.current()[1] == '*':
                        self.advance()
                        variadic = self.expect('IDENT')[1]
                    else:
                        params.append(self.expect('IDENT')[1])
                    if self.current()[0] == 'COMMA':
                        self.advance()
                self.expect('RPAREN')
                body = self.parse_block()
                return ('LAMBDA', params, body, variadic)
            self.advance()
            return ('VAR', tok[1])

        if tok[0] == 'LPAREN':
            self.advance()
            expr = self.parse_expr()
            self.expect('RPAREN')
            return expr

        if tok[0] == 'LBRACKET':
            self.advance()
            items = []
            while self.current()[0] != 'RBRACKET':
                items.append(self.parse_expr())
                if self.current()[0] == 'COMMA':
                    self.advance()
            self.expect('RBRACKET')
            return ('LIST', items)

        if tok[0] == 'LBRACE':
            self.advance()
            pairs = []
            while self.current()[0] != 'RBRACE':
                key = self.parse_expr()
                self.expect('COLON')
                val = self.parse_expr()
                pairs.append((key, val))
                if self.current()[0] == 'COMMA':
                    self.advance()
            self.expect('RBRACE')
            return ('DICT', pairs)

        raise SyntaxError(f"[line {tok[2]}] Unexpected token: '{tok[1]}'")


# ═══════════════════════════════════════════════════════════════
#  STAGE 3 — INTERPRETER
#  Walks the AST and executes each node.
#
#  Environment  — lexical scope chain (parent lookup for closures)
#  exec_stmt    — runs a statement node (side effects, no value)
#  eval         — evaluates an expression node (returns a value)
#
#  Control flow (rt / brk / cnt / throw) is implemented via Python
#  exceptions so they bubble through arbitrarily nested calls.
#
#  v1.3 additions:
#    MinLangClass.parent     — single-parent inheritance chain
#    MinLangSuper            — proxy bound to `super` inside methods
#    MinLangModule           — namespace produced by `import … as`
#    MinLangThrow            — user-raised errors (throw expr)
#    _find_method            — walks inheritance chain for method lookup
#    _call_method            — now accepts dispatching_class, injects super
#    instanceof              — now walks the full inheritance chain
#    STRUCTDEF node          — now carries parent_name field
#    IMPORT / EXPORT / THROW — new statement kinds
# ═══════════════════════════════════════════════════════════════

class ReturnException(Exception):
    def __init__(self, val): self.val = val

class BreakException(Exception):    pass
class ContinueException(Exception): pass

class MinLangThrow(Exception):
    """Raised by the MinLang `throw` statement. Carries the thrown value."""
    def __init__(self, val):
        self.val = val
        super().__init__(str(val))


class Environment:
    def __init__(self, parent=None):
        self.vars   = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Variable '{name}' is not defined")

    def set(self, name, val):
        """Declare in THIS scope."""
        self.vars[name] = val

    def assign(self, name, val):
        """Update existing variable, searching parent scopes."""
        if name in self.vars:
            self.vars[name] = val
        elif self.parent:
            self.parent.assign(name, val)
        else:
            self.vars[name] = val   # create at global level if not found


class Function:
    """A first-class MinLang function value (closure)."""
    def __init__(self, name, params, body, env, variadic=None):
        self.name     = name
        self.params   = params    # list of regular param names
        self.body     = body      # BLOCK AST node
        self.env      = env       # closure: scope at definition time
        self.variadic = variadic  # name of *args param, or None

    def __repr__(self):
        return f"<fn {self.name}>"


class MinLangClass:
    """
    Runtime representation of a struct definition.
    v1.3: carries an optional parent (MinLangClass) for inheritance.
    """
    def __init__(self, name, methods, parent=None):
        self.name    = name
        self.methods = methods   # dict[str, Function] — own methods only
        self.parent  = parent    # MinLangClass | None

    def __repr__(self):
        if self.parent:
            return f"<class {self.name} extends {self.parent.name}>"
        return f"<class {self.name}>"


class MinLangInstance:
    """
    Runtime representation of a struct instance.
    Attributes are stored in a plain dict; methods are looked up
    on the class (and its parents) and called with 'self' injected.
    """
    def __init__(self, klass):
        self.klass = klass
        self.attrs = {}         # instance attributes set by init / methods

    def __repr__(self):
        return f"<{self.klass.name} instance>"


class MinLangSuper:
    """
    Proxy bound to the name `super` inside a child method.
    Calls on it resolve to methods of the parent class but keep `self`
    bound to the current instance, just like Python's super().
    """
    def __init__(self, parent_class, instance):
        self.parent_class = parent_class
        self.instance     = instance

    def __repr__(self):
        return f"<super of {self.parent_class.name}>"


class MinLangModule:
    """
    Namespace produced by `import "file.minl" as name`.
    Exposes the module's exported variables as attributes.
    Access: mod.func()  or  mod.var
    """
    def __init__(self, path, exports):
        self.path    = path     # source path (used in error messages)
        self.exports = exports  # dict[str, value]

    def __repr__(self):
        return f"<module '{self.path}'>"


class Interpreter:

    def __init__(self):
        self.global_env    = Environment()
        self._current_line = None   # updated by SOURCELOC; shown in runtime errors
        self._setup_builtins()

    # ── Built-in functions ────────────────────────────────────────

    def _setup_builtins(self):
        e = self.global_env

        # Math
        e.set('sqrt',  lambda a: math.sqrt(a[0]))
        e.set('abs',   lambda a: abs(a[0]))
        e.set('pow',   lambda a: a[0] ** a[1])
        e.set('floor', lambda a: math.floor(a[0]))
        e.set('ceil',  lambda a: math.ceil(a[0]))
        e.set('rnd',   lambda a: round(a[0], int(a[1]) if len(a) > 1 else 0))
        e.set('max',   lambda a: max(a[0]) if len(a) == 1 and isinstance(a[0], list) else max(a))
        e.set('min',   lambda a: min(a[0]) if len(a) == 1 and isinstance(a[0], list) else min(a))
        e.set('log',   lambda a: math.log(a[0], a[1]) if len(a) > 1 else math.log(a[0]))
        e.set('sin',   lambda a: math.sin(a[0]))
        e.set('cos',   lambda a: math.cos(a[0]))
        e.set('tan',   lambda a: math.tan(a[0]))

        # Type conversion
        e.set('int',   lambda a: int(a[0]))
        e.set('flt',   lambda a: float(a[0]))
        e.set('str',   lambda a: self.to_str(a[0]))
        e.set('bool',  lambda a: bool(a[0]))

        def safe_int(a):
            try:    return int(a[0])
            except: return None
        def safe_flt(a):
            try:    return float(a[0])
            except: return None
        def can_int(a):
            try:    int(str(a[0]).strip()); return True
            except: return False
        def can_flt(a):
            try:    float(str(a[0]).strip()); return True
            except: return False

        e.set('toInt',  safe_int)
        e.set('toFlt',  safe_flt)
        e.set('canInt', can_int)
        e.set('canFlt', can_flt)

        # Type checking
        e.set('isInt',  lambda a: isinstance(a[0], int)   and not isinstance(a[0], bool))
        e.set('isFlt',  lambda a: isinstance(a[0], float))
        e.set('isStr',  lambda a: isinstance(a[0], str))
        e.set('isLst',  lambda a: isinstance(a[0], list))
        e.set('isDct',  lambda a: isinstance(a[0], dict))
        e.set('isBool', lambda a: isinstance(a[0], bool))
        e.set('isNil',  lambda a: a[0] is None)
        e.set('isObj',  lambda a: isinstance(a[0], MinLangInstance))
        e.set('type',   lambda a: type(a[0]).__name__)

        # OOP helpers — instanceof now walks the full inheritance chain (v1.3)
        e.set('instanceof', lambda a: self._instanceof(a[0], a[1]))
        e.set('className',  lambda a: (
            a[0].klass.name if isinstance(a[0], MinLangInstance)
            else type(a[0]).__name__
        ))

        # String functions
        e.set('len',        lambda a: len(a[0]))
        e.set('up',         lambda a: a[0].upper())
        e.set('lo',         lambda a: a[0].lower())
        e.set('trim',       lambda a: a[0].strip())
        e.set('split',      lambda a: a[0].split(a[1] if len(a) > 1 else ' '))
        e.set('join',       lambda a: a[1].join(self.to_str(x) for x in a[0]))
        e.set('find',       lambda a: a[0].find(a[1]))
        e.set('sub',        lambda a: a[0][int(a[1]):int(a[2]) if len(a) > 2 else None])
        e.set('rep',        lambda a: a[0] * a[1])
        e.set('replace',    lambda a: a[0].replace(a[1], a[2]))
        e.set('contains',   lambda a: a[1] in a[0])
        e.set('startsWith', lambda a: a[0].startswith(a[1]))
        e.set('endsWith',   lambda a: a[0].endswith(a[1]))
        e.set('fmt',        lambda a: format(a[0], a[1] if len(a) > 1 else ''))

        # List functions
        e.set('rng',     lambda a: list(range(int(a[0]))) if len(a) == 1
                                    else list(range(int(a[0]), int(a[1]),
                                            int(a[2]) if len(a) > 2 else 1)))
        e.set('push',    lambda a: a[0].append(a[1]) or a[0])
        e.set('pop',     lambda a: a[0].pop())
        e.set('sort',    lambda a: sorted(a[0]))
        e.set('rev',     lambda a: list(reversed(a[0])))
        e.set('flat',    lambda a: [x for sub in a[0] for x in sub])
        e.set('sum',     lambda a: sum(a[0]))
        e.set('count',   lambda a: a[0].count(a[1]))
        e.set('idx',     lambda a: a[0].index(a[1]) if a[1] in a[0] else -1)
        e.set('zip2',    lambda a: [list(p) for p in zip(a[0], a[1])])
        e.set('uniq',    lambda a: list(dict.fromkeys(a[0])))
        e.set('map',     lambda a: [self._call_fn(a[1], [x]) for x in a[0]])
        e.set('flt2',    lambda a: [x for x in a[0] if self._call_fn(a[1], [x])])
        e.set('red',     lambda a: self._reduce(a[0], a[1], a[2] if len(a) > 2 else a[0][0]))
        e.set('slice',   lambda a: a[0][int(a[1]):int(a[2]) if len(a) > 2 else None])

        # Dict functions
        e.set('keys',    lambda a: list(a[0].keys()))
        e.set('values',  lambda a: list(a[0].values()))
        e.set('items',   lambda a: [[k, v] for k, v in a[0].items()])
        e.set('hasKey',  lambda a: a[1] in a[0])
        e.set('delKey',  lambda a: a[0].pop(a[1], None) or a[0])
        e.set('merge',   lambda a: {**a[0], **a[1]})

        # Time
        import time as _time
        e.set('now',    lambda a: _time.time())
        e.set('sleep',  lambda a: (_time.sleep(a[0]), None)[1])
        e.set('clock',  lambda a: _time.strftime(a[0] if a else "%H:%M:%S"))
        e.set('date',   lambda a: _time.strftime(a[0] if a else "%Y-%m-%d"))

        # Random
        import random as _rnd
        e.set('rand',    lambda a: _rnd.random())
        e.set('randInt', lambda a: _rnd.randint(int(a[0]), int(a[1])))
        e.set('shuffle', lambda a: (_rnd.shuffle(a[0]), a[0])[1])
        e.set('pick',    lambda a: _rnd.choice(a[0]))

        # I/O
        e.set('read',    lambda a: open(a[0], encoding='utf-8').read())
        e.set('write',   lambda a: open(a[0], 'w',  encoding='utf-8').write(a[1]) or None)
        e.set('append',  lambda a: open(a[0], 'a',  encoding='utf-8').write(a[1]) or None)
        e.set('exists',  lambda a: os.path.exists(a[0]))
        e.set('exit',    lambda a: sys.exit(int(a[0]) if a else 0))

        # System
        e.set('sysArgs', lambda _: sys.argv[2:])
        e.set('sysEnv',  lambda a: os.environ.get(a[0], None))

        # Constants
        e.vars['pi']  = math.pi
        e.vars['inf'] = float('inf')
        e.vars['nan'] = float('nan')

    # ── v1.3: instanceof walks the full inheritance chain ─────────

    def _instanceof(self, obj, klass):
        if not isinstance(obj, MinLangInstance) or not isinstance(klass, MinLangClass):
            return False
        current = obj.klass
        while current is not None:
            if current.name == klass.name:
                return True
            current = current.parent
        return False

    # ── v1.3: method lookup walks the inheritance chain ───────────

    def _find_method(self, klass, name):
        """
        Walk the inheritance chain to find method `name`.
        Returns (Function, MinLangClass) — the function and the class it lives on.
        Returns (None, None) if not found anywhere in the chain.
        """
        current = klass
        while current is not None:
            if name in current.methods:
                return current.methods[name], current
            current = current.parent
        return None, None

    # ── Function / constructor calling ────────────────────────────

    def _call_fn(self, fn, args):
        if callable(fn):
            return fn(args)

        elif isinstance(fn, Function):
            env = Environment(fn.env)
            for param, arg in zip(fn.params, args):
                env.set(param, arg)
            if fn.variadic is not None:
                env.set(fn.variadic, list(args[len(fn.params):]))
            try:
                self.exec_block(fn.body, env)
            except ReturnException as r:
                return r.val
            return None

        elif isinstance(fn, MinLangClass):
            # v1.3: use _find_method so inherited init works
            instance = MinLangInstance(fn)
            init, init_class = self._find_method(fn, 'init')
            if init:
                self._call_method(instance, init, args, init_class)
            return instance

        raise TypeError(f"Cannot call: {fn!r}")

    def _call_method(self, instance, method_fn, args, dispatching_class=None):
        """
        Execute a struct method with 'self' bound to the instance.
        v1.3: also injects 'super' pointing to the parent of dispatching_class,
              so that child methods can call super.method(args).
        """
        env = Environment(method_fn.env)
        env.set('self', instance)

        # ── Inject `super` ────────────────────────────────────────
        # dispatching_class is the class that owns method_fn.
        # super should point to its parent, not necessarily instance.klass.parent,
        # so that multi-level chains work correctly.
        if dispatching_class is not None and dispatching_class.parent is not None:
            env.set('super', MinLangSuper(dispatching_class.parent, instance))
        else:
            env.set('super', None)

        for param, arg in zip(method_fn.params, args):
            env.set(param, arg)
        if method_fn.variadic is not None:
            env.set(method_fn.variadic, list(args[len(method_fn.params):]))
        try:
            self.exec_block(method_fn.body, env)
        except ReturnException as r:
            return r.val
        return None

    def _reduce(self, lst, fn, acc):
        for item in lst:
            acc = self._call_fn(fn, [acc, item])
        return acc

    # ── v1.3: run a file as an isolated module ────────────────────

    def _run_module(self, source, path):
        """
        Execute source in a fresh child scope (sees builtins).
        Returns a MinLangModule whose exports dict contains:
          - all names listed by `export` statements, OR
          - every non-dunder top-level name if no exports were declared.
        """
        tokens = tokenize(source)
        ast    = Parser(tokens).parse()

        module_env = Environment(self.global_env)
        # __exports__ is a list; export statements append to it.
        module_env.set('__exports__', [])

        self.exec_block(ast, module_env)

        declared = module_env.vars.get('__exports__', [])
        if declared:
            exports = {
                name: module_env.vars[name]
                for name in declared
                if name in module_env.vars
            }
        else:
            # No explicit exports → expose everything (except internal marker)
            exports = {
                k: v for k, v in module_env.vars.items()
                if not k.startswith('__')
            }
        return MinLangModule(path, exports)

    # ── Entry point ───────────────────────────────────────────────

    def run(self, ast, env=None):
        if env is None:
            env = self.global_env
        return self.exec_block(ast, env)

    def exec_block(self, node, env):
        _, stmts = node
        result = None
        for stmt in stmts:
            # SOURCELOC wrapper: update line tracker, then execute inner node
            if stmt[0] == 'SOURCELOC':
                self._current_line = stmt[1]
                result = self.exec_stmt(stmt[2], env)
            else:
                result = self.exec_stmt(stmt, env)
        return result

    # ── Statement executor ────────────────────────────────────────

    def exec_stmt(self, node, env):
        kind = node[0]

        if kind == 'LET':
            _, name, val_node = node
            env.set(name, self.eval(val_node, env))

        elif kind == 'ASSIGN':
            _, name, val_node = node
            env.assign(name, self.eval(val_node, env))

        elif kind == 'COMPOUND_ASSIGN':
            _, name, op, val_node = node
            current = env.get(name)
            delta   = self.eval(val_node, env)
            ops = {'+': lambda a, b: a + b, '-': lambda a, b: a - b,
                   '*': lambda a, b: a * b, '/': lambda a, b: a / b,
                    '%': lambda a, b: a % b}
            env.assign(name, ops[op](current, delta))

        elif kind == 'INDEX_ASSIGN':
            _, name, idx_node, val_node = node
            env.get(name)[self.eval(idx_node, env)] = self.eval(val_node, env)

        elif kind == 'ATTR_ASSIGN':
            # obj.attr = val
            _, obj_name, attr, val_node = node
            obj = env.get(obj_name)
            if isinstance(obj, MinLangInstance):
                obj.attrs[attr] = self.eval(val_node, env)
            else:
                raise RuntimeError(
                    f"Cannot set attribute '{attr}' on non-struct value '{obj_name}'"
                )

        elif kind == 'ATTR_COMPOUND_ASSIGN':
            # obj.attr += val  (and -=  *=  /=  %=)
            _, obj_name, attr, op, val_node = node
            obj = env.get(obj_name)
            if not isinstance(obj, MinLangInstance):
                raise RuntimeError(
                    f"Cannot set attribute '{attr}' on non-struct value '{obj_name}'"
                )
            current = obj.attrs.get(attr)
            if current is None:
                raise RuntimeError(
                    f"Attribute '{attr}' not set on '{obj.klass.name}' — cannot compound-assign"
                )
            delta = self.eval(val_node, env)
            ops = {'+': lambda a, b: a + b, '-': lambda a, b: a - b,
                   '*': lambda a, b: a * b, '/': lambda a, b: a / b,
                    '%': lambda a, b: a % b}
            obj.attrs[attr] = ops[op](current, delta)

        elif kind == 'PRINT':
            _, val_node, newline = node
            print(self.to_str(self.eval(val_node, env)), end='\n' if newline else '')

        elif kind == 'INPUT':
            _, name, prompt_node = node
            prompt = self.to_str(self.eval(prompt_node, env)) if prompt_node else ''
            env.assign(name, input(prompt))

        elif kind == 'IF':
            _, cond, body, elifs, else_body = node
            if self.eval(cond, env):
                self.exec_block(body, Environment(env))
            else:
                done = False
                for elif_cond, elif_body in elifs:
                    if self.eval(elif_cond, env):
                        self.exec_block(elif_body, Environment(env))
                        done = True
                        break
                if not done and else_body:
                    self.exec_block(else_body, Environment(env))

        elif kind == 'FOR':
            _, var, iter_node, body = node
            for item in self.eval(iter_node, env):
                loop_env = Environment(env)
                loop_env.set(var, item)
                try:
                    self.exec_block(body, loop_env)
                except BreakException:
                    break
                except ContinueException:
                    continue

        elif kind == 'WHILE':
            _, cond, body = node
            while self.eval(cond, env):
                loop_env = Environment(env)
                try:
                    self.exec_block(body, loop_env)
                except BreakException:
                    break
                except ContinueException:
                    continue

        elif kind == 'FUNCDEF':
            _, name, params, body, variadic = node
            env.set(name, Function(name, params, body, env, variadic))

        elif kind == 'STRUCTDEF':
            # v1.3: node is now ('STRUCTDEF', name, parent_name, method_defs)
            _, name, parent_name, method_defs = node
            parent = None
            if parent_name is not None:
                parent = env.get(parent_name)
                if not isinstance(parent, MinLangClass):
                    raise TypeError(
                        f"'{parent_name}' is not a struct — cannot use as parent"
                    )
            methods = {
                mname: Function(mname, params, body, env, variadic)
                for mname, (params, body, variadic) in method_defs.items()
            }
            env.set(name, MinLangClass(name, methods, parent))

        elif kind == 'RETURN':
            raise ReturnException(self.eval(node[1], env))

        elif kind == 'BREAK':
            raise BreakException()

        elif kind == 'CONTINUE':
            raise ContinueException()

        elif kind == 'THROW':
            # v1.3: throw any value — string, instance, etc.
            _, val_node = node
            raise MinLangThrow(self.eval(val_node, env))

        elif kind == 'TRY':
            _, body, err_var, handler = node
            try:
                self.exec_block(body, Environment(env))
            except (ReturnException, BreakException, ContinueException):
                raise
            except MinLangThrow as e:
                # v1.3: user-thrown value exposed as-is (not stringified)
                handler_env = Environment(env)
                handler_env.set(err_var, e.val)
                self.exec_block(handler, handler_env)
            except Exception as exc:
                handler_env = Environment(env)
                handler_env.set(err_var, str(exc))
                self.exec_block(handler, handler_env)

        elif kind == 'USE':
            # Legacy: run file in current scope (no namespace isolation)
            _, path_node = node
            path = self.eval(path_node, env)
            try:
                src = open(path, encoding='utf-8').read()
            except FileNotFoundError:
                raise RuntimeError(f"Module not found: '{path}'")
            ast = Parser(tokenize(src)).parse()
            self.exec_block(ast, env)

        elif kind == 'IMPORT':
            # v1.3: import "file.minl" as name  →  isolated namespace
            _, path_node, alias = node
            path = self.eval(path_node, env)
            try:
                src = open(path, encoding='utf-8').read()
            except FileNotFoundError:
                raise RuntimeError(f"Module not found: '{path}'")
            module = self._run_module(src, path)
            env.set(alias, module)

        elif kind == 'EXPORT':
            # v1.3: register a name in the module's export list
            _, name = node
            try:
                export_list = env.get('__exports__')
            except NameError:
                raise RuntimeError("'export' can only be used inside a module file")
            if not isinstance(export_list, list):
                raise RuntimeError("'export' can only be used inside a module file")
            if name not in export_list:
                export_list.append(name)

        elif kind == 'DESTRUCT_LIST':
            _, names, rest_name, val_node = node
            lst = self.eval(val_node, env)
            for i, name in enumerate(names):
                env.set(name, lst[i] if i < len(lst) else None)
            if rest_name is not None:
                env.set(rest_name, list(lst[len(names):]))

        elif kind == 'DESTRUCT_DICT':
            _, names, val_node = node
            dct = self.eval(val_node, env)
            for name in names:
                env.set(name, dct.get(name))

        elif kind == 'EXPR_STMT':
            return self.eval(node[1], env)

        elif kind == 'BLOCK':
            return self.exec_block(node, env)

    # ── Expression evaluator ──────────────────────────────────────

    def eval(self, node, env):
        kind = node[0]

        # ── Literals ──────────────────────────────────────────────
        if kind == 'INT':    return node[1]
        if kind == 'FLOAT':  return node[1]
        if kind == 'BOOL':   return node[1]
        if kind == 'STRING': return node[1]
        if kind == 'NIL':    return None

        if kind == 'FSTRING':
            def replace_expr(m):
                val = self.eval(Parser(tokenize(m.group(1))).parse_expr(), env)
                return self.to_str(val)
            return re.sub(r'\{([^}]+)\}', replace_expr, node[1])

        if kind == 'VAR':
            return env.get(node[1])

        if kind == 'LAMBDA':
            _, params, body, variadic = node
            return Function('<lambda>', params, body, env, variadic)

        if kind == 'LIST':
            return [self.eval(item, env) for item in node[1]]

        if kind == 'DICT':
            return {self.eval(k, env): self.eval(v, env) for k, v in node[1]}

        # ── Ternary: cond ? a : b ─────────────────────────────────
        if kind == 'TERNARY':
            _, cond, true_val, false_val = node
            return self.eval(true_val, env) if self.eval(cond, env) else self.eval(false_val, env)

        # ── Binary operations ─────────────────────────────────────
        if kind == 'BINOP':
            _, op, l, r = node
            lv = self.eval(l, env)
            rv = self.eval(r, env)
            if op == '+':   return lv + rv
            if op == '-':   return lv - rv
            if op == '*':   return lv * rv
            if op == '/':   return lv / rv
            if op == '%':   return lv % rv
            if op == '**':  return lv ** rv
            if op == '//':  return lv // rv          # v1.3: integer division
            if op == '<':   return lv <  rv
            if op == '>':   return lv >  rv
            if op == '<=':  return lv <= rv
            if op == '>=':  return lv >= rv
            if op == '==':  return lv == rv
            if op == '!=':  return lv != rv
            if op == '&&':  return lv and rv
            if op == '||':  return lv or  rv
            if op == '&':   return int(lv) &  int(rv)   # v1.3: bitwise
            if op == '|':   return int(lv) |  int(rv)
            if op == '^':   return int(lv) ^  int(rv)
            if op == '<<':  return int(lv) << int(rv)
            if op == '>>':  return int(lv) >> int(rv)

        # ── Unary operations ──────────────────────────────────────
        if kind == 'UNOP':
            _, op, val = node
            v = self.eval(val, env)
            if op == '-': return -v
            if op == '!': return not v
            if op == '~': return ~int(v)              # v1.3: bitwise NOT

        # ── Function / constructor call ───────────────────────────
        if kind == 'CALL':
            _, fn_node, arg_nodes = node
            fn   = self.eval(fn_node, env)
            args = [self.eval(a, env) for a in arg_nodes]
            return self._call_fn(fn, args)

        # ── Index access ──────────────────────────────────────────
        if kind == 'INDEX':
            _, obj_node, idx_node = node
            return self.eval(obj_node, env)[self.eval(idx_node, env)]

        # ── Slice: obj[start:stop] ────────────────────────────────
        if kind == 'SLICE':
            _, obj_node, start_node, stop_node = node
            obj   = self.eval(obj_node, env)
            start = self.eval(start_node, env) if start_node is not None else None
            stop  = self.eval(stop_node,  env) if stop_node  is not None else None
            return obj[start:stop]

        # ── Method call ───────────────────────────────────────────
        if kind == 'METHOD':
            _, obj_node, method, arg_nodes = node
            obj  = self.eval(obj_node, env)
            args = [self.eval(a, env) for a in arg_nodes]
            return self._dispatch_method(obj, method, args)

        # ── Nil-safe method call: returns nil if obj is nil ───────
        if kind == 'SAFE_METHOD':
            _, obj_node, method, arg_nodes = node
            obj = self.eval(obj_node, env)
            if obj is None:
                return None
            args = [self.eval(a, env) for a in arg_nodes]
            return self._dispatch_method(obj, method, args)

        # ── Attribute read ────────────────────────────────────────
        if kind == 'ATTR':
            _, obj_node, attr = node
            obj = self.eval(obj_node, env)

            if isinstance(obj, MinLangInstance):
                if attr in obj.attrs:
                    return obj.attrs[attr]
                # Allow reading methods as first-class values
                m, _ = self._find_method(obj.klass, attr)
                if m is not None:
                    return m
                raise AttributeError(
                    f"'{obj.klass.name}' instance has no attribute '{attr}'"
                )

            # v1.3: module attribute access
            if isinstance(obj, MinLangModule):
                if attr in obj.exports:
                    return obj.exports[attr]
                raise AttributeError(
                    f"Module '{obj.path}' has no export '{attr}'"
                )

            if attr == 'len': return len(obj)
            return getattr(obj, attr)

        # ── Nil-safe attribute read ───────────────────────────────
        if kind == 'SAFE_ATTR':
            _, obj_node, attr = node
            obj = self.eval(obj_node, env)
            if obj is None:
                return None
            if isinstance(obj, MinLangInstance):
                return obj.attrs.get(attr)
            if isinstance(obj, MinLangModule):
                return obj.exports.get(attr)
            if attr == 'len': return len(obj)
            return getattr(obj, attr)

        raise RuntimeError(f"Unknown AST node: {node}")

    def _dispatch_method(self, obj, method, args):
        """Central method dispatch — shared by METHOD and SAFE_METHOD."""

        # ── v1.3: struct instance methods (with inheritance) ─────
        if isinstance(obj, MinLangInstance):
            m, found_class = self._find_method(obj.klass, method)
            if m is None:
                raise AttributeError(
                    f"'{obj.klass.name}' has no method '{method}'"
                )
            return self._call_method(obj, m, args, found_class)

        # ── v1.3: super proxy — calls parent's method ────────────
        if isinstance(obj, MinLangSuper):
            m, found_class = self._find_method(obj.parent_class, method)
            if m is None:
                raise AttributeError(
                    f"Parent class '{obj.parent_class.name}' has no method '{method}'"
                )
            return self._call_method(obj.instance, m, args, found_class)

        # ── v1.3: module method call ──────────────────────────────
        if isinstance(obj, MinLangModule):
            fn = obj.exports.get(method)
            if fn is None:
                raise AttributeError(
                    f"Module '{obj.path}' has no export '{method}'"
                )
            return self._call_fn(fn, args)

        # ── String methods ──────────────────────────────────────
        if method == 'up':         return obj.upper()
        if method == 'lo':         return obj.lower()
        if method == 'trim':       return obj.strip()
        if method == 'split':      return obj.split(args[0] if args else ' ')
        if method == 'find':       return obj.find(args[0])
        if method == 'rep':        return obj * args[0]
        if method == 'sub':        return obj[args[0]:args[1] if len(args) > 1 else None]
        if method == 'replace':    return obj.replace(args[0], args[1])
        if method == 'has':        return args[0] in obj
        if method == 'startsWith': return obj.startswith(args[0])
        if method == 'endsWith':   return obj.endswith(args[0])

        # ── List methods ────────────────────────────────────────
        if method == 'push':   obj.append(args[0]); return obj
        if method == 'pop':    return obj.pop()
        if method == 'sort':   return sorted(obj)
        if method == 'rev':    return list(reversed(obj))
        if method == 'len':    return len(obj)
        if method == 'count':  return obj.count(args[0])
        if method == 'idx':    return obj.index(args[0]) if args[0] in obj else -1
        if method == 'flat':   return [x for sub in obj for x in sub]
        if method == 'uniq':   return list(dict.fromkeys(obj))
        if method == 'slice':  return obj[args[0]:args[1] if len(args) > 1 else None]
        if method == 'join':   return (args[0] if args else '').join(self.to_str(x) for x in obj)
        if method == 'map':    return [self._call_fn(args[0], [x]) for x in obj]
        if method == 'filter': return [x for x in obj if self._call_fn(args[0], [x])]
        if method == 'sum':    return sum(obj)

        # ── Dict methods ────────────────────────────────────────
        if method == 'keys':   return list(obj.keys())
        if method == 'values': return list(obj.values())
        if method == 'items':  return [[k, v] for k, v in obj.items()]
        if method == 'get':    return obj.get(args[0], args[1] if len(args) > 1 else None)
        if method == 'del':    obj.pop(args[0], None); return obj
        if method == 'merge':  return {**obj, **args[0]}

        raise AttributeError(f"Unknown method: '{method}'")

    # ── Value → string conversion ─────────────────────────────────

    def to_str(self, val):
        if val is None:  return "nil"
        if val is True:  return "T"
        if val is False: return "F"
        if isinstance(val, MinLangClass):
            return repr(val)
        if isinstance(val, MinLangInstance):
            # Call 'str' method if defined, otherwise format attrs
            m, mc = self._find_method(val.klass, 'str')
            if m:
                result = self._call_method(val, m, [], mc)
                return self.to_str(result)
            attrs = ', '.join(
                f"{k}: {self.to_str(v)}" for k, v in val.attrs.items()
            )
            return f"{val.klass.name}({{{attrs}}})"
        if isinstance(val, MinLangModule):
            return repr(val)
        if isinstance(val, MinLangSuper):
            return repr(val)
        if isinstance(val, float):
            if math.isnan(val):  return "nan"
            if math.isinf(val):  return "inf" if val > 0 else "-inf"
            if val == int(val) and abs(val) < 1e15:
                return str(int(val))
            s = repr(val)
            if "." in s and "e" not in s and "E" not in s:
                s = s.rstrip("0").rstrip(".")
            return s
        if isinstance(val, list):
            return "[" + ", ".join(self.to_str(v) for v in val) + "]"
        if isinstance(val, dict):
            pairs = ", ".join(f"{self.to_str(k)}: {self.to_str(v)}" for k, v in val.items())
            return "{" + pairs + "}"
        return str(val)


# ═══════════════════════════════════════════════════════════════
#  REPL + FILE RUNNER
# ═══════════════════════════════════════════════════════════════

def run_code(source, interp=None):
    """
    Compile and execute a MinLang source string.
    Both syntax errors (from the parser) and runtime errors
    (from the interpreter) now include a source line number.
    """
    if interp is None:
        interp = Interpreter()
    try:
        tokens = tokenize(source)
        ast    = Parser(tokens).parse()
        interp.run(ast)
    except (SyntaxError, NameError, TypeError, AttributeError,
            RuntimeError, KeyError, IndexError, ZeroDivisionError) as e:
        msg = str(e)
        if not msg.startswith('[line'):
            line   = interp._current_line
            prefix = f"[line {line}] " if line is not None else ""
            msg    = prefix + msg
        print(f"[Error] {msg}", file=sys.stderr)
    return interp


def repl():
    """Interactive REPL with multi-line block support."""
    print("MinLang REPL v1.3  |  'q' to quit  |  'help' for reference")
    print("─" * 56)
    interp = Interpreter()
    buf    = []

    while True:
        try:
            prompt = "... " if buf else ">>> "
            line   = input(prompt)

            if line.strip() == 'q':
                print("Goodbye!")
                break
            if line.strip() == 'help':
                print_help()
                continue
            if line.strip() == 'cls':
                os.system('cls' if os.name == 'nt' else 'clear')
                continue

            buf.append(line)
            src = '\n'.join(buf)

            if src.count('{') > src.count('}'):
                continue

            run_code(src, interp)
            buf = []

        except KeyboardInterrupt:
            buf = []
            print()
        except EOFError:
            print("\nGoodbye!")
            break


def print_help():
    print("""
╔══════════════════════════════════════════════════════════╗
║              MinLang v1.3  —  Quick Reference            ║
╠══════════════════════════════════════════════════════════╣
║  VARIABLES                                               ║
║   L x = 5              declare                           ║
║   x = 10               reassign                          ║
║   x += 1               compound  (+=  -=  *=  /=  %=)    ║
║   L [a,b,*r] = lst     list destructure  (*r = rest)     ║
║   L {x,y} = dct        dict destructure                  ║
║                                                          ║
║  OUTPUT / INPUT                                          ║
║   pt  "text"           print without newline             ║
║   ptl "text"           print with newline                ║
║   pt  f"{x}+{y}"       f-string interpolation            ║
║   inp "Prompt: " x     read with prompt                  ║
║                                                          ║
║  STRINGS                                                 ║
║   \"""...\"""           multiline string                 ║
║   s[1:4]               slice  (also s[:4]  s[2:])        ║
║   s.up()  s.lo()  s.trim()  s.split(",")                 ║
║   s.replace(a,b)  s.find(x)  s.has(x)                    ║
║   s.startsWith(x)  s.endsWith(x)                         ║
║                                                          ║
║  CONDITIONS                                              ║
║   if x > 5 { }  elif x == 5 { }  el { }                  ║
║   cond ? a : b         ternary expression                ║
║                                                          ║
║  LOOPS                                                   ║
║   lp i in rng(10) { }  for loop                          ║
║   wh x < 10 { }        while loop                        ║
║   brk / cnt            break / continue                  ║
║                                                          ║
║  FUNCTIONS                                               ║
║   fn add(a, b) { rt a + b }                              ║
║   fn greet(*names) { lp n in names { ptl n } }           ║
║                                                          ║
║  STRUCTS  (OOP)                                          ║
║   struct Animal {                                        ║
║     fn init(name) { self.name = name }                   ║
║     fn speak() { ptl "..." }                             ║
║   }                                                      ║
║   struct Dog extends Animal {        ## v1.3             ║
║     fn init(name, breed) {                               ║
║       super.init(name)               ## v1.3             ║
║       self.breed = breed                                 ║
║     }                                                    ║
║     fn speak() { ptl f"Woof! I'm {self.name}" }          ║
║     fn str() { rt f"Dog({self.name})" }                  ║
║   }                                                      ║
║   L d = Dog("Rex", "Lab")  ## construct                  ║
║   d.speak()                ## method call                ║
║   ptl d.name               ## read attribute             ║
║   d.name = "Max"           ## write attribute            ║
║   instanceof(d, Dog)       ## T                          ║
║   instanceof(d, Animal)    ## T  (chain)  v1.3           ║
║   className(d)             ## "Dog"                      ║
║   isObj(d)                 ## T                          ║
║                                                          ║
║  ERROR HANDLING                                          ║
║   try { risky() } catch e { ptl e }                      ║
║   throw "something went wrong"       ## v1.3             ║
║   throw MyError("typed error")       ## v1.3             ║
║                                                          ║
║  MODULES  (v1.3)                                         ║
║   ## In utils.minl:                                      ║
║   fn helper() { rt 42 }                                  ║
║   export helper          ## explicit export              ║
║                                                          ║
║   ## In main.minl:                                       ║
║   import "utils.minl" as utils                           ║
║   ptl utils.helper()                                     ║
║   use "legacy.minl"      ## old: runs in current scope   ║
║                                                          ║
║  NIL-SAFE ACCESS                                         ║
║   obj?.method()        nil if obj is nil                 ║
║   obj?.attr            nil if obj is nil                 ║
║                                                          ║
║  OPERATORS                                               ║
║   2 ** 10              power (right-associative)         ║
║   17 // 5              integer division → 3    v1.3      ║
║   == != < > <= >=  &&  ||  !                             ║
║   & | ^ ~ << >>        bitwise             v1.3          ║
║                                                          ║
║  DICT METHODS                                            ║
║   d.keys()  d.values()  d.items()                        ║
║   d.get("k", default)  d.has("k")  d.del("k")            ║
║   d.merge(other)                                         ║
║                                                          ║
║  BUILT-INS                                               ║
║   len sqrt abs pow rnd max min sum log sin cos tan       ║
║   rng push pop sort rev map flt2 red flat uniq zip2      ║
║   up lo trim split join find replace fmt                 ║
║   int flt str canInt canFlt toInt toFlt                  ║
║   now clock date sleep rand randInt pick shuffle         ║
║   keys values items hasKey delKey merge                  ║
║   read write append exists exit                          ║
║   instanceof className isObj                             ║
╚══════════════════════════════════════════════════════════╝
""")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = sys.argv[1]
        try:
            src = open(path, encoding='utf-8').read()
        except FileNotFoundError:
            print(f"[Error] File not found: {path}", file=sys.stderr)
            sys.exit(1)
        run_code(src)
    else:
        repl()
