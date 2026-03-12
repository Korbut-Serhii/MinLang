"""
MinLang Interpreter — v0.5
Major milestone: loops and user-defined functions.
Introduced lexical scoping via Environment chain.
Control flow now uses exceptions (ReturnException, BreakException).
New keywords: lp  wh  fn  rt  brk  cnt  elif  inp
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
    ('COMMA',    r','),
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


# ─── CONTROL FLOW EXCEPTIONS ─────────────────────────────────────

class ReturnException(Exception):
    def __init__(self, val): self.val = val

class BreakException(Exception):    pass
class ContinueException(Exception): pass


# ─── ENVIRONMENT (scoped) ─────────────────────────────────────────

class Environment:
    def __init__(self, parent=None):
        self.vars   = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:   return self.vars[name]
        if self.parent:         return self.parent.get(name)
        raise NameError(f"Variable '{name}' is not defined")

    def set(self, name, val):
        self.vars[name] = val

    def assign(self, name, val):
        if name in self.vars:
            self.vars[name] = val
        elif self.parent:
            self.parent.assign(name, val)
        else:
            self.vars[name] = val


# ─── FUNCTION OBJECT ─────────────────────────────────────────────

class Function:
    def __init__(self, name, params, body, env):
        self.name   = name
        self.params = params
        self.body   = body
        self.env    = env   # closure

    def __repr__(self): return f"<fn {self.name}>"


# ─── PARSER ──────────────────────────────────────────────────────

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ('EOF', '')

    def advance(self):
        tok = self.current(); self.pos += 1; return tok

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
            if self.current()[0] == 'EOF': break
            stmt = self.parse_statement()
            if stmt: stmts.append(stmt)
        return ('BLOCK', stmts)

    def parse_block(self):
        self.expect('LBRACE')
        stmts = []
        while True:
            self.skip_newlines()
            if self.current()[0] == 'RBRACE':
                self.advance(); break
            if self.current()[0] == 'EOF':
                raise SyntaxError("Unclosed block")
            stmt = self.parse_statement()
            if stmt: stmts.append(stmt)
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
            self.advance(); return ('PRINT', self.parse_expr(), False)

        if tok[0] == 'IDENT' and tok[1] == 'ptl':
            self.advance(); return ('PRINT', self.parse_expr(), True)

        if tok[0] == 'IDENT' and tok[1] == 'inp':
            self.advance()
            prompt = None
            if self.current()[0] == 'STRING':
                prompt = self.parse_expr()
            name = self.expect('IDENT')[1]
            return ('INPUT', name, prompt)

        if tok[0] == 'IDENT' and tok[1] == 'if':
            return self.parse_if()

        if tok[0] == 'IDENT' and tok[1] == 'lp':
            return self.parse_loop()

        if tok[0] == 'IDENT' and tok[1] == 'wh':
            return self.parse_while()

        if tok[0] == 'IDENT' and tok[1] == 'fn':
            return self.parse_fn()

        if tok[0] == 'IDENT' and tok[1] == 'rt':
            self.advance(); return ('RETURN', self.parse_expr())

        if tok[0] == 'IDENT' and tok[1] == 'brk':
            self.advance(); return ('BREAK',)

        if tok[0] == 'IDENT' and tok[1] == 'cnt':
            self.advance(); return ('CONTINUE',)

        if tok[0] == 'IDENT':
            save = self.pos
            self.advance()
            if self.current()[0] == 'ASSIGN':
                self.advance()
                return ('ASSIGN', tok[1], self.parse_expr())
            self.pos = save

        return ('EXPR_STMT', self.parse_expr())

    def parse_if(self):
        self.advance()
        cond = self.parse_expr()
        body = self.parse_block()
        elifs = []
        else_body = None
        while True:
            self.skip_newlines()
            if self.current()[0] == 'IDENT' and self.current()[1] == 'elif':
                self.advance()
                ec = self.parse_expr()
                eb = self.parse_block()
                elifs.append((ec, eb))
            elif self.current()[0] == 'IDENT' and self.current()[1] == 'el':
                self.advance()
                else_body = self.parse_block()
                break
            else:
                break
        return ('IF', cond, body, elifs, else_body)

    def parse_loop(self):
        self.advance()
        var = self.expect('IDENT')[1]
        self.expect('IDENT', 'in')
        iterable = self.parse_expr()
        body = self.parse_block()
        return ('FOR', var, iterable, body)

    def parse_while(self):
        self.advance()
        cond = self.parse_expr()
        body = self.parse_block()
        return ('WHILE', cond, body)

    def parse_fn(self):
        self.advance()
        name = self.expect('IDENT')[1]
        self.expect('LPAREN')
        params = []
        while self.current()[0] != 'RPAREN':
            params.append(self.expect('IDENT')[1])
            if self.current()[0] == 'COMMA': self.advance()
        self.expect('RPAREN')
        body = self.parse_block()
        return ('FUNCDEF', name, params, body)

    # ── Expressions ──────────────────────────────────────────────

    def parse_expr(self):   return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.current()[0] == 'OP_OR':
            self.advance(); left = ('BINOP', '||', left, self.parse_and())
        return left

    def parse_and(self):
        left = self.parse_compare()
        while self.current()[0] == 'OP_AND':
            self.advance(); left = ('BINOP', '&&', left, self.parse_compare())
        return left

    def parse_compare(self):
        left = self.parse_additive()
        while self.current()[0] in ('OP_EQ', 'OP_NEQ', 'OP_LTE', 'OP_GTE', 'OP'):
            op = self.current()[1]
            if op in ('==', '!=', '<=', '>=', '<', '>'):
                self.advance(); left = ('BINOP', op, left, self.parse_additive())
            else: break
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.current()[0] == 'OP' and self.current()[1] in ('+', '-'):
            op = self.advance()[1]; left = ('BINOP', op, left, self.parse_multiplicative())
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.current()[0] == 'OP' and self.current()[1] in ('*', '/', '%'):
            op = self.advance()[1]; left = ('BINOP', op, left, self.parse_unary())
        return left

    def parse_unary(self):
        if self.current()[0] == 'OP' and self.current()[1] == '-':
            self.advance(); return ('UNOP', '-', self.parse_unary())
        if self.current()[0] == 'OP_NOT':
            self.advance(); return ('UNOP', '!', self.parse_unary())
        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_primary()
        while True:
            if self.current()[0] == 'LPAREN':
                self.advance()
                args = []
                while self.current()[0] != 'RPAREN':
                    args.append(self.parse_expr())
                    if self.current()[0] == 'COMMA': self.advance()
                self.expect('RPAREN')
                node = ('CALL', node, args)
            else:
                break
        return node

    def parse_primary(self):
        tok = self.current()
        if tok[0] == 'INT':    self.advance(); return ('INT', int(tok[1]))
        if tok[0] == 'FLOAT':  self.advance(); return ('FLOAT', float(tok[1]))
        if tok[0] == 'BOOL':   self.advance(); return ('BOOL', tok[1] == 'T')
        if tok[0] == 'STRING':
            self.advance()
            val = tok[1][1:-1].replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"')
            return ('STRING', val)
        if tok[0] == 'IDENT':
            if tok[1] == 'nil': self.advance(); return ('NIL',)
            self.advance(); return ('VAR', tok[1])
        if tok[0] == 'LPAREN':
            self.advance(); expr = self.parse_expr(); self.expect('RPAREN'); return expr
        raise SyntaxError(f"Unexpected token: {tok}")


# ─── INTERPRETER ─────────────────────────────────────────────────

class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self._setup_builtins()

    def _setup_builtins(self):
        import math
        e = self.global_env
        e.set('len',    lambda args: len(args[0]))
        e.set('sqrt',   lambda args: math.sqrt(args[0]))
        e.set('abs',    lambda args: abs(args[0]))
        e.set('pow',    lambda args: args[0] ** args[1])
        e.set('max',    lambda args: max(args))
        e.set('min',    lambda args: min(args))
        e.set('rng',    lambda args: list(range(int(args[0]))) if len(args) == 1
                                     else list(range(int(args[0]), int(args[1]))))
        e.set('int',    lambda args: int(args[0]))
        e.set('flt',    lambda args: float(args[0]))
        e.set('str',    lambda args: str(args[0]))
        e.set('push',   lambda args: args[0].append(args[1]) or args[0])
        e.set('pop',    lambda args: args[0].pop())
        e.set('sort',   lambda args: sorted(args[0]))

    def run(self, ast, env=None):
        if env is None: env = self.global_env
        return self.exec_block(ast, env)

    def exec_block(self, node, env):
        _, stmts = node
        result = None
        for stmt in stmts:
            result = self.exec_stmt(stmt, env)
        return result

    def exec_stmt(self, node, env):
        kind = node[0]

        if kind == 'LET':
            _, name, val_node = node
            env.set(name, self.eval(val_node, env))

        elif kind == 'ASSIGN':
            _, name, val_node = node
            env.assign(name, self.eval(val_node, env))

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
                for ec, eb in elifs:
                    if self.eval(ec, env):
                        self.exec_block(eb, Environment(env)); done = True; break
                if not done and else_body:
                    self.exec_block(else_body, Environment(env))

        elif kind == 'FOR':
            _, var, iter_node, body = node
            for item in self.eval(iter_node, env):
                loop_env = Environment(env)
                loop_env.set(var, item)
                try:
                    self.exec_block(body, loop_env)
                except BreakException:    break
                except ContinueException: continue

        elif kind == 'WHILE':
            _, cond, body = node
            while self.eval(cond, env):
                try:
                    self.exec_block(body, Environment(env))
                except BreakException:    break
                except ContinueException: continue

        elif kind == 'FUNCDEF':
            _, name, params, body = node
            env.set(name, Function(name, params, body, env))

        elif kind == 'RETURN':
            raise ReturnException(self.eval(node[1], env))

        elif kind == 'BREAK':    raise BreakException()
        elif kind == 'CONTINUE': raise ContinueException()

        elif kind == 'EXPR_STMT':
            return self.eval(node[1], env)

    def _call_fn(self, fn, args):
        if callable(fn):
            return fn(args)
        elif isinstance(fn, Function):
            env = Environment(fn.env)
            for p, a in zip(fn.params, args):
                env.set(p, a)
            try:
                self.exec_block(fn.body, env)
            except ReturnException as r:
                return r.val
            return None
        raise TypeError(f"Cannot call: {fn}")

    def eval(self, node, env):
        kind = node[0]
        if kind == 'INT':    return node[1]
        if kind == 'FLOAT':  return node[1]
        if kind == 'BOOL':   return node[1]
        if kind == 'STRING': return node[1]
        if kind == 'NIL':    return None
        if kind == 'VAR':    return env.get(node[1])

        if kind == 'BINOP':
            _, op, l, r = node
            lv, rv = self.eval(l, env), self.eval(r, env)
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
            v = self.eval(val, env)
            if op == '-': return -v
            if op == '!': return not v

        if kind == 'CALL':
            _, fn_node, arg_nodes = node
            fn   = self.eval(fn_node, env)
            args = [self.eval(a, env) for a in arg_nodes]
            return self._call_fn(fn, args)

        raise RuntimeError(f"Unknown AST node: {node}")

    def to_str(self, val):
        if val is None:  return "nil"
        if val is True:  return "T"
        if val is False: return "F"
        return str(val)


# ─── RUNNER / REPL ───────────────────────────────────────────────

def run_code(source, interp=None):
    if interp is None: interp = Interpreter()
    try:
        tokens = tokenize(source)
        ast    = Parser(tokens).parse()
        interp.run(ast)
    except (SyntaxError, NameError, TypeError, RuntimeError,
            KeyError, IndexError, ZeroDivisionError) as e:
        print(f"[Error] {e}", file=sys.stderr)
    return interp

def repl():
    print("MinLang REPL v0.5  |  'q' to quit")
    interp = Interpreter()
    buf = []
    while True:
        try:
            line = input("... " if buf else ">>> ")
            if line.strip() == 'q': print("Goodbye!"); break
            buf.append(line)
            src = '\n'.join(buf)
            if src.count('{') > src.count('}'):
                continue
            run_code(src, interp)
            buf = []
        except KeyboardInterrupt:
            buf = []; print()
        except EOFError:
            print("\nGoodbye!"); break

if __name__ == '__main__':
    if len(sys.argv) > 1:
        try: src = open(sys.argv[1], encoding='utf-8').read()
        except FileNotFoundError:
            print(f"[Error] File not found: {sys.argv[1]}", file=sys.stderr); sys.exit(1)
        run_code(src)
    else:
        repl()
