"""
MinLang Interpreter — v1.0
A minimalist programming language. Maximum power, minimum keystrokes.
Source files use the .ll extension.

Architecture:
    Source code (.ll file)
        │
        ▼
    Tokenizer  ── turns raw text into a flat list of tokens
        │
        ▼
    Parser     ── turns tokens into an Abstract Syntax Tree (AST)
        │
        ▼
    Interpreter── walks the AST and executes each node
"""

import sys
import re
import math
import os


# ═══════════════════════════════════════════════════════════════
#  STAGE 1 — TOKENIZER
#  Reads raw source text character by character and groups
#  characters into named tokens, e.g. "42" → ('INT', '42').
#  Each entry in TOKEN_PATTERNS is tried left-to-right; the
#  first regex that matches at the current position wins.
# ═══════════════════════════════════════════════════════════════

TOKEN_PATTERNS = [
    # Comments: everything after ## until end of line is discarded
    ('COMMENT',   r'##.*'),

    # String literals: "hello" — supports \" \n \t escape sequences
    ('STRING',    r'"(?:[^"\\]|\\.)*"'),

    # F-strings: f"hello {name}" — interpolated strings
    ('FSTRING',   r'f"(?:[^"\\]|\\.)*"'),

    # Numbers: floats must be checked BEFORE ints so 3.14 isn't split into 3 and .14
    ('FLOAT',     r'\d+\.\d+'),
    ('INT',       r'\d+'),

    # Boolean literals: T = true, F = false  (word boundary \b so "True" doesn't match)
    ('BOOL',      r'\b(T|F)\b'),

    # Two-character operators must come BEFORE single-character ones
    ('OP_EQ',     r'=='),
    ('OP_NEQ',    r'!='),
    ('OP_LTE',    r'<='),
    ('OP_GTE',    r'>='),
    ('OP_AND',    r'&&'),
    ('OP_OR',     r'\|\|'),

    # Logical NOT: ! but NOT != (negative lookahead (?!=))
    ('OP_NOT',    r'!(?!=)'),

    # Arrow (reserved for future use)
    ('ARROW',     r'->'),

    # Single = is assignment; == was already matched above
    ('ASSIGN',    r'='),

    # Arithmetic and comparison operators
    ('OP',        r'[+\-*/%<>]'),

    # Brackets and punctuation
    ('LPAREN',    r'\('),
    ('RPAREN',    r'\)'),
    ('LBRACE',    r'\{'),
    ('RBRACE',    r'\}'),
    ('LBRACKET',  r'\['),
    ('RBRACKET',  r'\]'),
    ('COMMA',     r','),
    ('COLON',     r':'),
    ('DOT',       r'\.'),

    # Newlines are kept as tokens so the parser can handle line endings
    ('NEWLINE',   r'\n'),

    # Whitespace (spaces and tabs) is silently discarded
    ('INDENT',    r'[ \t]+'),

    # Identifiers: variable names, keywords, built-in names
    # Must come LAST so keywords like "if" are caught as IDENT, not something else
    ('IDENT',     r'[A-Za-z_][A-Za-z0-9_]*'),
]


def tokenize(code):
    """
    Convert a source string into a list of (type, value) token pairs.

    Example:
        tokenize('L x = 5')
        → [('IDENT','L'), ('IDENT','x'), ('ASSIGN','='), ('INT','5')]

    Raises SyntaxError if an unrecognised character is encountered.
    """
    tokens = []
    pos = 0
    while pos < len(code):
        matched = False
        for ttype, pattern in TOKEN_PATTERNS:
            m = re.match(pattern, code[pos:])
            if m:
                val = m.group(0)
                if ttype == 'COMMENT':
                    pass             # drop comments entirely
                elif ttype == 'INDENT':
                    pass             # drop whitespace
                else:
                    tokens.append((ttype, val))
                pos += len(val)
                matched = True
                break
        if not matched:
            raise SyntaxError(f"Unknown character: '{code[pos]}' at position {pos}")
    return tokens


# ═══════════════════════════════════════════════════════════════
#  STAGE 2 — PARSER
#  Takes the flat token list and builds a tree of nested tuples
#  called an Abstract Syntax Tree (AST).
#
#  Every node in the AST is a tuple whose first element is a
#  string tag, e.g.:
#    ('LET',    'x',  ('INT', 5))
#    ('BINOP',  '+',  ('VAR','x'), ('INT', 3))
#    ('IF',     cond, body, elifs, else_body)
#
#  The grammar is recursive descent: each "parse_X" method
#  handles one level of the grammar and may call lower-level
#  methods for sub-expressions.
#
#  Operator precedence (lowest → highest):
#    || (or)  →  && (and)  →  comparisons  →  +/-  →  */% →  unary  →  postfix
# ═══════════════════════════════════════════════════════════════

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0   # index of the token we are currently looking at

    # ── Navigation helpers ──────────────────────────────────────

    def skip_newlines(self):
        """Advance past any NEWLINE tokens."""
        while self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'NEWLINE':
            self.pos += 1

    def current(self):
        """Return the current token without consuming it."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ('EOF', '')

    def advance(self):
        """Return the current token and move the cursor forward."""
        tok = self.current()
        self.pos += 1
        return tok

    def expect(self, ttype, val=None):
        """
        Assert the current token has the given type (and optionally value),
        consume it, and return it.  Raises SyntaxError on mismatch.
        """
        self.skip_newlines()
        tok = self.advance()
        if tok[0] != ttype:
            raise SyntaxError(f"Expected {ttype} but got {tok}")
        if val and tok[1] != val:
            raise SyntaxError(f"Expected '{val}' but got '{tok[1]}'")
        return tok

    # ── Top-level entry point ────────────────────────────────────

    def parse(self):
        """Parse the entire token stream into a BLOCK node."""
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
        """Parse a { ... } block and return a BLOCK node."""
        self.expect('LBRACE')
        stmts = []
        while True:
            self.skip_newlines()
            if self.current()[0] == 'RBRACE':
                self.advance()
                break
            if self.current()[0] == 'EOF':
                raise SyntaxError("Unclosed block — missing '}'")
            stmt = self.parse_statement()
            if stmt:
                stmts.append(stmt)
        return ('BLOCK', stmts)

    # ── Statement dispatcher ─────────────────────────────────────

    def parse_statement(self):
        """
        Look at the current token and dispatch to the appropriate
        statement parser.  Falls through to expression statement
        (e.g. a bare function call) if no keyword matches.
        """
        self.skip_newlines()
        tok = self.current()

        if tok[0] == 'EOF':
            return None

        # ── L x = expr   →  variable declaration ────────────────
        if tok[0] == 'IDENT' and tok[1] == 'L':
            self.advance()
            name = self.expect('IDENT')[1]
            self.expect('ASSIGN')
            val = self.parse_expr()
            return ('LET', name, val)

        # ── pt expr   →  print without newline ──────────────────
        if tok[0] == 'IDENT' and tok[1] == 'pt':
            self.advance()
            val = self.parse_expr()
            return ('PRINT', val, False)   # False = no trailing newline

        # ── ptl expr  →  print with newline ─────────────────────
        if tok[0] == 'IDENT' and tok[1] == 'ptl':
            self.advance()
            val = self.parse_expr()
            return ('PRINT', val, True)    # True = append newline

        # ── inp [prompt] varname  →  read user input ─────────────
        if tok[0] == 'IDENT' and tok[1] == 'inp':
            self.advance()
            prompt = None
            # optional prompt string immediately after inp
            if self.current()[0] in ('STRING', 'FSTRING'):
                prompt = self.parse_expr()
            name = self.expect('IDENT')[1]
            return ('INPUT', name, prompt)

        # ── if / elif / el ───────────────────────────────────────
        if tok[0] == 'IDENT' and tok[1] == 'if':
            return self.parse_if()

        # ── lp var in iterable { }   →  for loop ─────────────────
        if tok[0] == 'IDENT' and tok[1] == 'lp':
            return self.parse_loop()

        # ── wh cond { }   →  while loop ──────────────────────────
        if tok[0] == 'IDENT' and tok[1] == 'wh':
            return self.parse_while()

        # ── fn name(params) { }   →  function definition ─────────
        if tok[0] == 'IDENT' and tok[1] == 'fn':
            return self.parse_fn()

        # ── rt expr   →  return ──────────────────────────────────
        if tok[0] == 'IDENT' and tok[1] == 'rt':
            self.advance()
            val = self.parse_expr()
            return ('RETURN', val)

        # ── brk   →  break ───────────────────────────────────────
        if tok[0] == 'IDENT' and tok[1] == 'brk':
            self.advance()
            return ('BREAK',)

        # ── cnt   →  continue ────────────────────────────────────
        if tok[0] == 'IDENT' and tok[1] == 'cnt':
            self.advance()
            return ('CONTINUE',)

        # ── x = expr   →  reassignment  (IDENT followed by plain =) ──
        # We need lookahead to distinguish   x = 5   from   x == 5
        if tok[0] == 'IDENT':
            save = self.pos
            self.advance()

            if self.current()[0] == 'ASSIGN':
                # simple assignment: x = expr
                self.advance()
                val = self.parse_expr()
                return ('ASSIGN', tok[1], val)

            elif self.current()[0] == 'LBRACKET':
                # possible index assignment: x[i] = val
                self.advance()
                idx = self.parse_expr()
                self.expect('RBRACKET')
                if self.current()[0] == 'ASSIGN':
                    self.advance()
                    val = self.parse_expr()
                    return ('INDEX_ASSIGN', tok[1], idx, val)
                else:
                    # not an assignment — rewind and fall through
                    self.pos = save
            else:
                # not an assignment — rewind and fall through
                self.pos = save

        # ── Fallthrough: expression used as a statement (e.g. fn call) ──
        expr = self.parse_expr()
        return ('EXPR_STMT', expr)

    # ── Control flow parsers ─────────────────────────────────────

    def parse_if(self):
        self.advance()               # consume 'if'
        cond = self.parse_expr()
        body = self.parse_block()
        elifs = []
        else_body = None
        while True:
            self.skip_newlines()
            if self.current()[0] == 'IDENT' and self.current()[1] == 'elif':
                self.advance()
                elif_cond = self.parse_expr()
                elif_body = self.parse_block()
                elifs.append((elif_cond, elif_body))
            elif self.current()[0] == 'IDENT' and self.current()[1] == 'el':
                self.advance()
                else_body = self.parse_block()
                break
            else:
                break
        return ('IF', cond, body, elifs, else_body)

    def parse_loop(self):
        self.advance()               # consume 'lp'
        var = self.expect('IDENT')[1]
        self.expect('IDENT', 'in')   # keyword 'in' is required
        iterable = self.parse_expr()
        body = self.parse_block()
        return ('FOR', var, iterable, body)

    def parse_while(self):
        self.advance()               # consume 'wh'
        cond = self.parse_expr()
        body = self.parse_block()
        return ('WHILE', cond, body)

    def parse_fn(self):
        self.advance()               # consume 'fn'
        name = self.expect('IDENT')[1]
        self.expect('LPAREN')
        params = []
        while self.current()[0] != 'RPAREN':
            params.append(self.expect('IDENT')[1])
            if self.current()[0] == 'COMMA':
                self.advance()
        self.expect('RPAREN')
        body = self.parse_block()
        return ('FUNCDEF', name, params, body)

    # ── Expression parsing (recursive descent by precedence) ─────
    #
    #  Each level calls the level above it, so lower precedence
    #  operators are only reached after higher ones are handled.
    #
    #  parse_expr
    #    └─ parse_or       (||)
    #         └─ parse_and     (&&)
    #              └─ parse_compare  (== != < > <= >=)
    #                   └─ parse_additive   (+ -)
    #                        └─ parse_multiplicative  (* / %)
    #                             └─ parse_unary  (- !)
    #                                  └─ parse_postfix  (calls, indexing, methods)
    #                                       └─ parse_primary  (literals, vars, parens)

    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.current()[0] == 'OP_OR':
            self.advance()
            right = self.parse_and()
            left = ('BINOP', '||', left, right)
        return left

    def parse_and(self):
        left = self.parse_compare()
        while self.current()[0] == 'OP_AND':
            self.advance()
            right = self.parse_compare()
            left = ('BINOP', '&&', left, right)
        return left

    def parse_compare(self):
        left = self.parse_additive()
        # Comparison operators are non-associative (no a < b < c)
        while self.current()[0] in ('OP_EQ', 'OP_NEQ', 'OP_LTE', 'OP_GTE', 'OP'):
            op = self.current()[1]
            if op in ('==', '!=', '<=', '>=', '<', '>'):
                self.advance()
                right = self.parse_additive()
                left = ('BINOP', op, left, right)
            else:
                break
        return left

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
        # Unary minus:  -x
        if self.current()[0] == 'OP' and self.current()[1] == '-':
            self.advance()
            val = self.parse_unary()
            return ('UNOP', '-', val)
        # Logical not:  !cond
        if self.current()[0] == 'OP_NOT':
            self.advance()
            val = self.parse_unary()
            return ('UNOP', '!', val)
        return self.parse_postfix()

    def parse_postfix(self):
        """
        Handle operations that come after an expression:
            - function call:   expr(args)
            - index access:    expr[i]
            - method call:     expr.method(args)
            - attribute read:  expr.attr
        Left-associative, so  a[0].len()  works correctly.
        """
        node = self.parse_primary()
        while True:
            if self.current()[0] == 'LPAREN':
                # Function call
                self.advance()
                args = []
                while self.current()[0] != 'RPAREN':
                    args.append(self.parse_expr())
                    if self.current()[0] == 'COMMA':
                        self.advance()
                self.expect('RPAREN')
                node = ('CALL', node, args)

            elif self.current()[0] == 'LBRACKET':
                # Index access: list[i] or dict["key"]
                self.advance()
                idx = self.parse_expr()
                self.expect('RBRACKET')
                node = ('INDEX', node, idx)

            elif self.current()[0] == 'DOT':
                # Method or attribute access
                self.advance()
                attr = self.expect('IDENT')[1]
                if self.current()[0] == 'LPAREN':
                    # Method call: obj.method(args)
                    self.advance()
                    args = []
                    while self.current()[0] != 'RPAREN':
                        args.append(self.parse_expr())
                        if self.current()[0] == 'COMMA':
                            self.advance()
                    self.expect('RPAREN')
                    node = ('METHOD', node, attr, args)
                else:
                    # Attribute read: obj.attr
                    node = ('ATTR', node, attr)
            else:
                break
        return node

    def parse_primary(self):
        """
        Parse the smallest indivisible units:
        literals, variable names, parenthesised expressions,
        list literals, and dict literals.
        """
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
            # Process escape sequences
            val = tok[1][1:-1].replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"')
            return ('STRING', val)

        if tok[0] == 'FSTRING':
            self.advance()
            # Strip the leading f" and trailing "
            return ('FSTRING', tok[1][2:-1])

        if tok[0] == 'IDENT':
            if tok[1] == 'nil':
                self.advance()
                return ('NIL',)
            self.advance()
            return ('VAR', tok[1])

        if tok[0] == 'LPAREN':
            # Parenthesised expression for grouping: (a + b) * c
            self.advance()
            expr = self.parse_expr()
            self.expect('RPAREN')
            return expr

        if tok[0] == 'LBRACKET':
            # List literal: [1, 2, 3]
            self.advance()
            items = []
            while self.current()[0] != 'RBRACKET':
                items.append(self.parse_expr())
                if self.current()[0] == 'COMMA':
                    self.advance()
            self.expect('RBRACKET')
            return ('LIST', items)

        if tok[0] == 'LBRACE':
            # Dict literal: {"key": value}
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

        raise SyntaxError(f"Unexpected token: {tok}")


# ═══════════════════════════════════════════════════════════════
#  STAGE 3 — INTERPRETER
#  Walks the AST produced by the parser and evaluates each node.
#
#  Key concepts:
#
#  Environment — a dictionary of name → value mappings.
#    Each block (function body, loop, if-branch) creates a child
#    Environment that inherits from its parent.  Variable lookup
#    walks up the chain: local first, then outer scopes.
#
#  exec_stmt  — executes a statement node (no return value).
#  eval       — evaluates an expression node (always returns a value).
#
#  Control flow (return / break / continue) is implemented via
#  Python exceptions: ReturnException, BreakException, ContinueException.
#  This is a standard technique — it avoids threading control flags
#  through every function manually.
# ═══════════════════════════════════════════════════════════════

class ReturnException(Exception):
    """Raised by 'rt' to bubble a return value up to the call site."""
    def __init__(self, val):
        self.val = val

class BreakException(Exception):
    """Raised by 'brk' to exit the nearest enclosing loop."""
    pass

class ContinueException(Exception):
    """Raised by 'cnt' to skip to the next loop iteration."""
    pass


class Environment:
    """
    A single scope frame.  Behaves like a dictionary but with
    parent-chain lookup for lexical scoping.
    """

    def __init__(self, parent=None):
        self.vars = {}          # variables defined in THIS scope
        self.parent = parent    # enclosing scope (None for global)

    def get(self, name):
        """Look up a name — walk up parent chain if not found here."""
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Variable '{name}' is not defined")

    def set(self, name, val):
        """Declare a new variable in THIS scope (used by L x = ...)."""
        self.vars[name] = val

    def assign(self, name, val):
        """
        Reassign an existing variable.
        Searches up the parent chain so inner scopes can update
        outer variables.  If not found anywhere, creates it here.
        """
        if name in self.vars:
            self.vars[name] = val
        elif self.parent:
            self.parent.assign(name, val)
        else:
            # Variable wasn't declared — create it in global scope
            self.vars[name] = val


class Function:
    """
    A first-class function value.
    Stores the parameter list, the body AST node, and the
    environment at the time of definition (closure).
    """

    def __init__(self, name, params, body, env):
        self.name   = name    # function name (for error messages)
        self.params = params  # list of parameter name strings
        self.body   = body    # BLOCK AST node
        self.env    = env     # closure: the scope where fn was defined

    def __repr__(self):
        return f"<fn {self.name}>"


class Interpreter:

    def __init__(self):
        self.global_env = Environment()
        self._setup_builtins()

    # ── Built-in functions ────────────────────────────────────────
    # Each built-in is stored as a Python lambda in the global
    # environment.  When the interpreter sees a CALL node it looks
    # up the name, finds the lambda, and calls it with a list of
    # already-evaluated argument values.

    def _setup_builtins(self):
        e = self.global_env

        # ── Math ────────────────────────────────────────────────
        e.set('sqrt',  lambda args: math.sqrt(args[0]))           # square root
        e.set('abs',   lambda args: abs(args[0]))                  # absolute value
        e.set('pow',   lambda args: args[0] ** args[1])            # power: pow(2,10) = 1024
        e.set('floor', lambda args: math.floor(args[0]))           # round down
        e.set('ceil',  lambda args: math.ceil(args[0]))            # round up
        e.set('rnd',   lambda args: round(args[0], int(args[1]) if len(args) > 1 else 0))
        e.set('max',   lambda args: max(args[0]) if len(args) == 1 and isinstance(args[0], list) else max(args))
        e.set('min',   lambda args: min(args[0]) if len(args) == 1 and isinstance(args[0], list) else min(args))

        # ── Type conversion ──────────────────────────────────────
        e.set('int',   lambda args: int(args[0]))                  # "42" → 42  (crashes if invalid)
        e.set('flt',   lambda args: float(args[0]))                # "3.14" → 3.14
        e.set('str',   lambda args: str(args[0]))                  # 42 → "42"
        e.set('bool',  lambda args: bool(args[0]))                 # 0 → F, 1 → T

        # Safe conversion — returns nil instead of crashing
        def safe_int(args):
            try:    return int(args[0])
            except: return None
        def safe_flt(args):
            try:    return float(args[0])
            except: return None
        e.set('toInt', safe_int)   # toInt("abc") → nil, toInt("5") → 5
        e.set('toFlt', safe_flt)   # toFlt("x")   → nil, toFlt("3.1") → 3.1

        # Check if conversion is possible — returns T or F
        def can_int(args):
            try:    int(str(args[0]).strip()); return True
            except: return False
        def can_flt(args):
            try:    float(str(args[0]).strip()); return True
            except: return False
        e.set('canInt', can_int)   # canInt("42") → T,  canInt("hi") → F
        e.set('canFlt', can_flt)   # canFlt("3.14") → T

        # ── Type checking ────────────────────────────────────────
        e.set('isInt',  lambda args: isinstance(args[0], int) and not isinstance(args[0], bool))
        e.set('isFlt',  lambda args: isinstance(args[0], float))
        e.set('isStr',  lambda args: isinstance(args[0], str))
        e.set('isLst',  lambda args: isinstance(args[0], list))
        e.set('isDct',  lambda args: isinstance(args[0], dict))
        e.set('isBool', lambda args: isinstance(args[0], bool))
        e.set('isNil',  lambda args: args[0] is None)
        e.set('type',   lambda args: type(args[0]).__name__)       # type(42) → "int"

        # ── String functions ─────────────────────────────────────
        e.set('len',         lambda args: len(args[0]))                         # length of string or list
        e.set('up',          lambda args: args[0].upper())                      # "hello" → "HELLO"
        e.set('lo',          lambda args: args[0].lower())                      # "HELLO" → "hello"
        e.set('trim',        lambda args: args[0].strip())                      # "  hi  " → "hi"
        e.set('split',       lambda args: args[0].split(args[1] if len(args) > 1 else ' '))
        e.set('join',        lambda args: args[1].join(str(x) for x in args[0]))  # join(["a","b"], "-") → "a-b"
        e.set('find',        lambda args: args[0].find(args[1]))                # find("hello","ll") → 2, -1 if not found
        e.set('sub',         lambda args: args[0][int(args[1]):int(args[2]) if len(args) > 2 else None])
        e.set('rep',         lambda args: args[0] * args[1])                   # rep("ab",3) → "ababab"
        e.set('replace',     lambda args: args[0].replace(args[1], args[2]))   # replace("hi world","world","MinLang")
        e.set('contains',    lambda args: args[1] in args[0])                  # contains("hello","ell") → T
        e.set('startsWith',  lambda args: args[0].startswith(args[1]))
        e.set('endsWith',    lambda args: args[0].endswith(args[1]))

        # ── List functions ───────────────────────────────────────
        e.set('rng',     lambda args: list(range(int(args[0]))) if len(args) == 1
                                    else list(range(int(args[0]), int(args[1]),
                                                int(args[2]) if len(args) > 2 else 1)))
        e.set('push',    lambda args: args[0].append(args[1]) or args[0])      # add to end, return list
        e.set('pop',     lambda args: args[0].pop())                            # remove+return last element
        e.set('sort',    lambda args: sorted(args[0]))                          # return sorted copy
        e.set('rev',     lambda args: list(reversed(args[0])))                  # return reversed copy
        e.set('flat',    lambda args: [x for sub in args[0] for x in sub])     # flatten one level
        e.set('sum',     lambda args: sum(args[0]))                             # sum all numbers in list
        e.set('count',   lambda args: args[0].count(args[1]))                  # count occurrences
        e.set('idx',     lambda args: args[0].index(args[1]) if args[1] in args[0] else -1)
        e.set('zip2',    lambda args: [list(p) for p in zip(args[0], args[1])])
        e.set('uniq',    lambda args: list(dict.fromkeys(args[0])))             # remove duplicates, preserve order
        e.set('map',     lambda args: list(map(lambda x: self._call_fn(args[1], [x]), args[0])))
        e.set('flt2',    lambda args: list(filter(lambda x: self._call_fn(args[1], [x]), args[0])))
        e.set('red',     lambda args: self._reduce(args[0], args[1], args[2] if len(args) > 2 else args[0][0]))

        # ── Time ─────────────────────────────────────────────────
        import time as _time
        e.set('now',     lambda args: _time.time())                             # unix timestamp as float
        e.set('sleep',   lambda args: (_time.sleep(args[0]), None)[1])          # pause execution N seconds
        e.set('clock',   lambda args: _time.strftime(args[0] if args else "%H:%M:%S"))  # "14:32:05"
        e.set('date',    lambda args: _time.strftime(args[0] if args else "%Y-%m-%d"))  # "2026-03-11"

        # ── Random ───────────────────────────────────────────────
        import random as _random
        e.set('rand',    lambda args: _random.random())                         # 0.0 – 1.0
        e.set('randInt', lambda args: _random.randint(int(args[0]), int(args[1])))  # inclusive both ends
        e.set('shuffle', lambda args: (_random.shuffle(args[0]), args[0])[1])   # shuffle in-place, return list
        e.set('pick',    lambda args: _random.choice(args[0]))                  # random element from list

        # ── I/O ──────────────────────────────────────────────────
        e.set('read',    lambda args: open(args[0], encoding='utf-8').read())
        e.set('write',   lambda args: open(args[0], 'w', encoding='utf-8').write(args[1]) or None)
        e.set('exit',    lambda args: sys.exit(int(args[0]) if args else 0))

        # ── System ───────────────────────────────────────────────
        e.set('sysArgs', lambda _: sys.argv[2:])                   # command-line arguments after filename
        e.set('sysEnv',  lambda args: os.environ.get(args[0], None))

        # ── Constants (stored as plain values, not functions) ────
        self.global_env.vars['pi']  = math.pi    # 3.14159...
        self.global_env.vars['inf'] = float('inf')

    # ── Function calling ─────────────────────────────────────────

    def _call_fn(self, fn, args):
        """
        Call either a Python built-in (lambda) or a MinLang Function object.
        Returns the function's return value, or nil if there's no return statement.
        """
        if callable(fn):
            # Built-in: just call the lambda with the argument list
            return fn(args)
        elif isinstance(fn, Function):
            # User-defined: create a new scope, bind parameters, run the body
            env = Environment(fn.env)            # child of the closure scope
            for param, arg in zip(fn.params, args):
                env.set(param, arg)
            try:
                self.exec_block(fn.body, env)
            except ReturnException as r:
                return r.val                     # rt expr was hit
            return None                          # fell off end of function
        raise TypeError(f"Cannot call: {fn}")

    def _reduce(self, lst, fn, acc):
        """Fold a list left using fn(accumulator, item)."""
        for item in lst:
            acc = self._call_fn(fn, [acc, item])
        return acc

    # ── Entry point ──────────────────────────────────────────────

    def run(self, ast, env=None):
        if env is None:
            env = self.global_env
        return self.exec_block(ast, env)

    def exec_block(self, node, env):
        """Execute all statements inside a BLOCK node in order."""
        _, stmts = node
        result = None
        for stmt in stmts:
            result = self.exec_stmt(stmt, env)
        return result

    # ── Statement executor ────────────────────────────────────────

    def exec_stmt(self, node, env):
        """
        Execute one statement.  Statements produce side effects
        (printing, assigning, looping) but do not return values
        to the caller — except EXPR_STMT which passes the value through.
        """
        kind = node[0]

        if kind == 'LET':
            # L x = expr  — declare new variable in current scope
            _, name, val_node = node
            env.set(name, self.eval(val_node, env))

        elif kind == 'ASSIGN':
            # x = expr  — reassign existing variable (searches parent scopes)
            _, name, val_node = node
            env.assign(name, self.eval(val_node, env))

        elif kind == 'INDEX_ASSIGN':
            # x[i] = val  — mutate an element of a list or dict
            _, name, idx_node, val_node = node
            obj = env.get(name)
            idx = self.eval(idx_node, env)
            obj[idx] = self.eval(val_node, env)

        elif kind == 'PRINT':
            # pt / ptl  — print expression, optional newline
            _, val_node, newline = node
            val = self.eval(val_node, env)
            end = '\n' if newline else ''
            print(self.to_str(val), end=end)

        elif kind == 'INPUT':
            # inp [prompt] varname  — read a line from stdin
            _, name, prompt_node = node
            prompt = self.to_str(self.eval(prompt_node, env)) if prompt_node else ''
            val = input(prompt)
            env.assign(name, val)     # always stored as string

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
            # lp var in iterable { body }
            _, var, iter_node, body = node
            iterable = self.eval(iter_node, env)
            for item in iterable:
                loop_env = Environment(env)
                loop_env.set(var, item)
                try:
                    self.exec_block(body, loop_env)
                except BreakException:
                    break
                except ContinueException:
                    continue          # Python's continue restarts the for loop

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
            # fn name(params) { body }  — store Function object in current scope
            _, name, params, body = node
            fn = Function(name, params, body, env)   # capture current env as closure
            env.set(name, fn)

        elif kind == 'RETURN':
            _, val_node = node
            raise ReturnException(self.eval(val_node, env))   # unwinds to _call_fn

        elif kind == 'BREAK':
            raise BreakException()

        elif kind == 'CONTINUE':
            raise ContinueException()

        elif kind == 'EXPR_STMT':
            # A bare expression used as a statement (e.g. a function call for its side effect)
            return self.eval(node[1], env)

        elif kind == 'BLOCK':
            return self.exec_block(node, env)

    # ── Expression evaluator ──────────────────────────────────────

    def eval(self, node, env):
        """
        Evaluate an expression node and return its value.
        Every node type returns a Python value:
            INT/FLOAT → number, STRING → str, BOOL → bool, NIL → None,
            LIST → list, DICT → dict, BINOP → computed value, etc.
        """
        kind = node[0]

        # Literal values — just unwrap them
        if kind == 'INT':    return node[1]
        if kind == 'FLOAT':  return node[1]
        if kind == 'BOOL':   return node[1]
        if kind == 'STRING': return node[1]
        if kind == 'NIL':    return None

        if kind == 'FSTRING':
            # f"Hello {name}!"
            # Find every {expr} inside the template and replace it
            # with the evaluated value of expr.
            template = node[1]
            def replace_expr(m):
                expr_src = m.group(1)
                tokens   = tokenize(expr_src)
                parser   = Parser(tokens)
                expr_ast = parser.parse_expr()
                val      = self.eval(expr_ast, env)
                return self.to_str(val)
            return re.sub(r'\{([^}]+)\}', replace_expr, template)

        if kind == 'VAR':
            # Variable lookup — walks up the environment chain
            return env.get(node[1])

        if kind == 'LIST':
            # [expr, expr, ...]  — evaluate each element
            return [self.eval(item, env) for item in node[1]]

        if kind == 'DICT':
            # {key: val, ...}  — evaluate every key and value
            return {self.eval(k, env): self.eval(v, env) for k, v in node[1]}

        if kind == 'BINOP':
            # Binary operation: evaluate both sides, apply operator
            _, op, l, r = node
            lv = self.eval(l, env)
            rv = self.eval(r, env)
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
            if op == '&&': return lv and rv   # short-circuits in Python
            if op == '||': return lv or rv

        if kind == 'UNOP':
            # Unary operation: -x or !cond
            _, op, val = node
            v = self.eval(val, env)
            if op == '-': return -v
            if op == '!': return not v

        if kind == 'CALL':
            # Function call: evaluate the function expression, evaluate arguments,
            # then dispatch to _call_fn
            _, fn_node, arg_nodes = node
            fn   = self.eval(fn_node, env)
            args = [self.eval(a, env) for a in arg_nodes]
            return self._call_fn(fn, args)

        if kind == 'INDEX':
            # list[i] or dict["key"]
            _, obj_node, idx_node = node
            obj = self.eval(obj_node, env)
            idx = self.eval(idx_node, env)
            return obj[idx]

        if kind == 'METHOD':
            # obj.method(args)  — hard-coded method dispatch
            _, obj_node, method, arg_nodes = node
            obj  = self.eval(obj_node, env)
            args = [self.eval(a, env) for a in arg_nodes]
            # String methods
            if method == 'up':    return obj.upper()
            if method == 'lo':    return obj.lower()
            if method == 'trim':  return obj.strip()
            if method == 'split': return obj.split(args[0] if args else ' ')
            if method == 'find':  return obj.find(args[0])
            if method == 'rep':   return obj * args[0]
            if method == 'sub':   return obj[args[0]:args[1] if len(args) > 1 else None]
            if method == 'has':   return args[0] in obj
            if method == 'replace': return obj.replace(args[0], args[1])
            # List methods
            if method == 'push':  obj.append(args[0]); return obj
            if method == 'pop':   return obj.pop()
            if method == 'sort':  return sorted(obj)
            if method == 'rev':   return list(reversed(obj))
            if method == 'len':   return len(obj)
            if method == 'count': return obj.count(args[0])
            if method == 'idx':   return obj.index(args[0]) if args[0] in obj else -1
            raise AttributeError(f"Unknown method: '{method}'")

        if kind == 'ATTR':
            # obj.attr  — read-only attribute shorthand
            _, obj_node, attr = node
            obj = self.eval(obj_node, env)
            if attr == 'len': return len(obj)
            return getattr(obj, attr)

        raise RuntimeError(f"Unknown AST node: {node}")

    # ── Value → string conversion ─────────────────────────────────

    def to_str(self, val):
        """
        Convert any MinLang value to its string representation for output.
        Python's True/False become MinLang's T/F, None becomes nil.
        """
        if val is None:   return "nil"
        if val is True:   return "T"
        if val is False:  return "F"
        if isinstance(val, list):
            return "[" + ", ".join(self.to_str(v) for v in val) + "]"
        if isinstance(val, dict):
            pairs = ", ".join(f"{self.to_str(k)}: {self.to_str(v)}" for k, v in val.items())
            return "{" + pairs + "}"
        return str(val)


# ═══════════════════════════════════════════════════════════════
#  REPL + FILE RUNNER
#  The entry point that ties everything together.
# ═══════════════════════════════════════════════════════════════

def run_code(source, interp=None):
    """
    Compile and execute a MinLang source string.
    Accepts an optional existing Interpreter so state can persist
    across multiple calls (used by the REPL).
    """
    if interp is None:
        interp = Interpreter()
    try:
        tokens = tokenize(source)         # Stage 1
        parser = Parser(tokens)
        ast    = parser.parse()           # Stage 2
        interp.run(ast)                   # Stage 3
    except (SyntaxError, NameError, TypeError,
            RuntimeError, KeyError, IndexError, ZeroDivisionError) as e:
        print(f"[Error] {e}", file=sys.stderr)
    return interp


def repl():
    """
    Interactive Read-Eval-Print Loop.
    Supports multi-line input by counting braces — if there are
    unclosed '{' we keep buffering lines until they are closed.
    """
    print("MinLang REPL v1.0  |  'q' to quit  |  'help' for reference")
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
            src         = '\n'.join(buf)
            open_braces = src.count('{') - src.count('}')

            if open_braces > 0:
                continue           # block not closed yet — keep reading

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
╔══════════════════════════════════════════════╗
║           MinLang  —  Quick Reference        ║
╠══════════════════════════════════════════════╣
║  VARIABLES                                   ║
║   L x = 5          declare variable          ║
║   x = 10           reassign                  ║
║                                              ║
║  OUTPUT                                      ║
║   pt  "text"       print without newline     ║
║   ptl "text"       print with newline        ║
║   pt  f"{x}+{y}"  f-string interpolation     ║
║                                              ║
║  INPUT                                       ║
║   inp x            read into x               ║
║   inp "Name: " x   read with prompt          ║
║                                              ║
║  CONDITIONS                                  ║
║   if x > 5 { }                               ║
║   elif x == 5 { }                            ║
║   el { }                                     ║
║                                              ║
║  LOOPS                                       ║
║   lp i in rng(10) { }   for loop             ║
║   wh x < 10 { }         while loop           ║
║   brk                   break                ║
║   cnt                   continue             ║
║                                              ║
║  FUNCTIONS                                   ║
║   fn add(a,b) { rt a+b }                     ║
║                                              ║
║  TYPES                                       ║
║   T / F / nil      true / false / null       ║
║   [1,2,3]          list                      ║
║   {"k":"v"}        dict                      ║
║                                              ║
║  BUILT-INS                                   ║
║   len sqrt abs pow rnd max min sum           ║
║   rng push pop sort rev map flt2 red         ║
║   up lo trim split join find replace         ║
║   int flt str canInt canFlt toInt toFlt      ║
║   now clock date sleep rand randInt pick     ║
╚══════════════════════════════════════════════╝
""")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = sys.argv[1]
        # Accept both .ll and .minlang extensions
        try:
            src = open(path, encoding='utf-8').read()
        except FileNotFoundError:
            print(f"[Error] File not found: {path}", file=sys.stderr)
            sys.exit(1)
        run_code(src)
    else:
        repl()
