"""
MinLang - минималистичный язык программирования
Максимум возможностей, минимум символов

Примерная версия: v0.9, в относительности патча v1.0

"""

import sys
import re
import math
import os

# ─────────────────────────────────────────────
#  ТОКЕНИЗАТОР
# ─────────────────────────────────────────────

TOKEN_PATTERNS = [
    ('COMMENT',   r'##.*'),
    ('STRING',    r'"(?:[^"\\]|\\.)*"'),
    ('FSTRING',   r'f"(?:[^"\\]|\\.)*"'),
    ('FLOAT',     r'\d+\.\d+'),
    ('INT',       r'\d+'),
    ('BOOL',      r'\b(T|F)\b'),
    ('OP_EQ',     r'=='),
    ('OP_NEQ',    r'!='),
    ('OP_LTE',    r'<='),
    ('OP_GTE',    r'>='),
    ('OP_AND',    r'&&'),
    ('OP_OR',     r'\|\|'),
    ('OP_NOT',    r'!(?!=)'),
    ('ARROW',     r'->'),
    ('ASSIGN',    r'='),
    ('OP',        r'[+\-*/%<>]'),
    ('LPAREN',    r'\('),
    ('RPAREN',    r'\)'),
    ('LBRACE',    r'\{'),
    ('RBRACE',    r'\}'),
    ('LBRACKET',  r'\['),
    ('RBRACKET',  r'\]'),
    ('COMMA',     r','),
    ('COLON',     r':'),
    ('DOT',       r'\.'),
    ('NEWLINE',   r'\n'),
    ('INDENT',    r'[ \t]+'),
    ('IDENT',     r'[A-Za-z_][A-Za-z0-9_]*'),
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
                if ttype == 'COMMENT':
                    pass  # skip
                elif ttype == 'INDENT':
                    pass  # skip whitespace
                else:
                    tokens.append((ttype, val))
                pos += len(val)
                matched = True
                break
        if not matched:
            raise SyntaxError(f"Неизвестный символ: '{code[pos]}' на позиции {pos}")
    return tokens

# ─────────────────────────────────────────────
#  ПАРСЕР → AST
# ─────────────────────────────────────────────

class Parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t[0] != 'NEWLINE' or True]
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        i = self.pos + offset
        while i < len(self.tokens) and self.tokens[i][0] == 'NEWLINE':
            i += 1
        if i < len(self.tokens):
            return self.tokens[i]
        return ('EOF', '')

    def skip_newlines(self):
        while self.pos < len(self.tokens) and self.tokens[self.pos][0] == 'NEWLINE':
            self.pos += 1

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ('EOF', '')

    def advance(self):
        tok = self.current()
        self.pos += 1
        return tok

    def expect(self, ttype, val=None):
        self.skip_newlines()
        tok = self.advance()
        if tok[0] != ttype:
            raise SyntaxError(f"Ожидался {ttype}, получен {tok}")
        if val and tok[1] != val:
            raise SyntaxError(f"Ожидалось '{val}', получено '{tok[1]}'")
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
                raise SyntaxError("Незакрытый блок {")
            stmt = self.parse_statement()
            if stmt:
                stmts.append(stmt)
        return ('BLOCK', stmts)

    def parse_statement(self):
        self.skip_newlines()
        tok = self.current()

        if tok[0] == 'EOF':
            return None

        # L x = expr  →  let
        if tok[0] == 'IDENT' and tok[1] == 'L':
            self.advance()
            name = self.expect('IDENT')[1]
            self.expect('ASSIGN')
            val = self.parse_expr()
            return ('LET', name, val)

        # pt expr  →  print
        if tok[0] == 'IDENT' and tok[1] == 'pt':
            self.advance()
            # pt"str" or pt(expr)
            val = self.parse_expr()
            return ('PRINT', val, False)

        # ptl expr  →  println (print + newline, по умолчанию)
        if tok[0] == 'IDENT' and tok[1] == 'ptl':
            self.advance()
            val = self.parse_expr()
            return ('PRINT', val, True)

        # inp x  →  input
        if tok[0] == 'IDENT' and tok[1] == 'inp':
            self.advance()
            prompt = None
            if self.current()[0] in ('STRING', 'FSTRING'):
                prompt = self.parse_expr()
            name = self.expect('IDENT')[1]
            return ('INPUT', name, prompt)

        # if cond { } elif { } el { }
        if tok[0] == 'IDENT' and tok[1] == 'if':
            return self.parse_if()

        # lp var in expr { }  →  for loop
        if tok[0] == 'IDENT' and tok[1] == 'lp':
            return self.parse_loop()

        # wh cond { }  →  while
        if tok[0] == 'IDENT' and tok[1] == 'wh':
            return self.parse_while()

        # fn name(args) { }  →  function def
        if tok[0] == 'IDENT' and tok[1] == 'fn':
            return self.parse_fn()

        # rt expr  →  return
        if tok[0] == 'IDENT' and tok[1] == 'rt':
            self.advance()
            val = self.parse_expr()
            return ('RETURN', val)

        # brk  →  break
        if tok[0] == 'IDENT' and tok[1] == 'brk':
            self.advance()
            return ('BREAK',)

        # cnt  →  continue
        if tok[0] == 'IDENT' and tok[1] == 'cnt':
            self.advance()
            return ('CONTINUE',)

        # im "module"  →  import
        if tok[0] == 'IDENT' and tok[1] == 'im':
            self.advance()
            name = self.expect('IDENT')[1]
            return ('IMPORT', name)

        # x = expr  →  assignment (must be IDENT followed by =)
        if tok[0] == 'IDENT':
            # look ahead: could be assignment or call expression
            save = self.pos
            self.advance()
            # check for = (not ==)
            if self.current()[0] == 'ASSIGN':
                self.advance()
                val = self.parse_expr()
                return ('ASSIGN', tok[1], val)
            # could be index assign: x[i] = val
            elif self.current()[0] == 'LBRACKET':
                self.advance()
                idx = self.parse_expr()
                self.expect('RBRACKET')
                if self.current()[0] == 'ASSIGN':
                    self.advance()
                    val = self.parse_expr()
                    return ('INDEX_ASSIGN', tok[1], idx, val)
                else:
                    self.pos = save
            else:
                self.pos = save

        # expression statement (function call etc.)
        expr = self.parse_expr()
        return ('EXPR_STMT', expr)

    def parse_if(self):
        self.advance()  # consume 'if'
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
        self.advance()  # consume 'lp'
        var = self.expect('IDENT')[1]
        self.expect('IDENT', 'in')
        iterable = self.parse_expr()
        body = self.parse_block()
        return ('FOR', var, iterable, body)

    def parse_while(self):
        self.advance()  # consume 'wh'
        cond = self.parse_expr()
        body = self.parse_block()
        return ('WHILE', cond, body)

    def parse_fn(self):
        self.advance()  # consume 'fn'
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
        while self.current()[0] in ('OP_EQ','OP_NEQ','OP_LTE','OP_GTE','OP'):
            op = self.current()[1]
            if op in ('==','!=','<=','>=','<','>'):
                self.advance()
                right = self.parse_additive()
                left = ('BINOP', op, left, right)
            else:
                break
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.current()[0] == 'OP' and self.current()[1] in ('+','-'):
            op = self.advance()[1]
            right = self.parse_multiplicative()
            left = ('BINOP', op, left, right)
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.current()[0] == 'OP' and self.current()[1] in ('*','/','%'):
            op = self.advance()[1]
            right = self.parse_unary()
            left = ('BINOP', op, left, right)
        return left

    def parse_unary(self):
        if self.current()[0] == 'OP_NOT':
            self.advance()
            val = self.parse_unary()
            return ('UNOP', '!', val)
        if self.current()[0] == 'OP' and self.current()[1] == '-':
            self.advance()
            val = self.parse_unary()
            return ('UNOP', '-', val)
        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_primary()
        while True:
            if self.current()[0] == 'LPAREN':
                # function call
                self.advance()
                args = []
                while self.current()[0] != 'RPAREN':
                    args.append(self.parse_expr())
                    if self.current()[0] == 'COMMA':
                        self.advance()
                self.expect('RPAREN')
                node = ('CALL', node, args)
            elif self.current()[0] == 'LBRACKET':
                self.advance()
                idx = self.parse_expr()
                self.expect('RBRACKET')
                node = ('INDEX', node, idx)
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
            val = tok[1][1:-1].replace('\\n','\n').replace('\\t','\t').replace('\\"','"')
            return ('STRING', val)

        if tok[0] == 'FSTRING':
            self.advance()
            return ('FSTRING', tok[1][2:-1])

        if tok[0] == 'IDENT':
            # nil keyword
            if tok[1] == 'nil':
                self.advance()
                return ('NIL',)
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

        raise SyntaxError(f"Неожиданный токен: {tok}")


# ─────────────────────────────────────────────
#  ИНТЕРПРЕТАТОР
# ─────────────────────────────────────────────

class ReturnException(Exception):
    def __init__(self, val): self.val = val

class BreakException(Exception): pass
class ContinueException(Exception): pass

class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Переменная '{name}' не определена")

    def set(self, name, val):
        self.vars[name] = val

    def assign(self, name, val):
        if name in self.vars:
            self.vars[name] = val
        elif self.parent:
            self.parent.assign(name, val)
        else:
            self.vars[name] = val


class Function:
    def __init__(self, name, params, body, env):
        self.name = name
        self.params = params
        self.body = body
        self.env = env
    def __repr__(self):
        return f"<fn {self.name}>"


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self._setup_builtins()

    def _setup_builtins(self):
        e = self.global_env
        # Math
        e.set('sqrt', lambda args: math.sqrt(args[0]))
        e.set('abs',  lambda args: abs(args[0]))
        e.set('pow',  lambda args: args[0] ** args[1])
        e.set('floor',lambda args: math.floor(args[0]))
        e.set('ceil', lambda args: math.ceil(args[0]))
        e.set('rnd',  lambda args: round(args[0], int(args[1]) if len(args)>1 else 0))
        e.set('max',  lambda args: max(args[0]) if len(args)==1 and isinstance(args[0],list) else max(args))
        e.set('min',  lambda args: min(args[0]) if len(args)==1 and isinstance(args[0],list) else min(args))
        # Type conversion
        e.set('int',  lambda args: int(args[0]))
        e.set('flt',  lambda args: float(args[0]))
        e.set('str',  lambda args: str(args[0]))
        e.set('bool', lambda args: bool(args[0]))
        # String
        e.set('len',  lambda args: len(args[0]))
        e.set('up',   lambda args: args[0].upper())
        e.set('lo',   lambda args: args[0].lower())
        e.set('trim', lambda args: args[0].strip())
        e.set('split',lambda args: args[0].split(args[1] if len(args)>1 else ' '))
        e.set('join', lambda args: args[1].join(args[0]))
        e.set('rep',  lambda args: args[0] * args[1])
        e.set('find', lambda args: args[0].find(args[1]))
        e.set('sub',  lambda args: args[0][int(args[1]):int(args[2]) if len(args)>2 else None])
        # List
        e.set('rng',  lambda args: list(range(int(args[0]))) if len(args)==1 else list(range(int(args[0]),int(args[1]),int(args[2]) if len(args)>2 else 1)))
        e.set('push', lambda args: args[0].append(args[1]) or args[0])
        e.set('pop',  lambda args: args[0].pop())
        e.set('sort', lambda args: sorted(args[0]))
        e.set('rev',  lambda args: list(reversed(args[0])))
        e.set('flat', lambda args: [x for sub in args[0] for x in sub])
        e.set('map',  lambda args: list(map(lambda x: self._call_fn(args[1],[x]), args[0])))
        e.set('flt2', lambda args: list(filter(lambda x: self._call_fn(args[1],[x]), args[0])))
        e.set('red',  lambda args: self._reduce(args[0], args[1], args[2] if len(args)>2 else args[0][0]))
        # I/O
        e.set('read', lambda args: open(args[0]).read())
        e.set('write',lambda args: open(args[0],'w').write(args[1]) or None)
        e.set('exit', lambda args: sys.exit(int(args[0]) if args else 0))
        # Type check
        e.set('isInt', lambda args: isinstance(args[0], int) and not isinstance(args[0], bool))
        e.set('isFlt', lambda args: isinstance(args[0], float))
        e.set('isStr', lambda args: isinstance(args[0], str))
        e.set('isLst', lambda args: isinstance(args[0], list))
        e.set('isDct', lambda args: isinstance(args[0], dict))
        e.set('isBool',lambda args: isinstance(args[0], bool))
        e.set('isNil', lambda args: args[0] is None)
        e.set('type',  lambda args: type(args[0]).__name__)
        # Safe conversion (returns nil on failure)
        def safe_int(args):
            try: return int(args[0])
            except: return None
        def safe_flt(args):
            try: return float(args[0])
            except: return None
        e.set('toInt', safe_int)
        e.set('toFlt', safe_flt)
        # Can convert check
        def can_int(args):
            try: int(str(args[0]).strip()); return True
            except: return False
        def can_flt(args):
            try: float(str(args[0]).strip()); return True
            except: return False
        e.set('canInt', can_int)
        e.set('canFlt', can_flt)
        # Time
        import time as _time
        e.set('now',   lambda args: _time.time())
        e.set('sleep', lambda args: (_time.sleep(args[0]), None)[1])
        e.set('clock', lambda args: _time.strftime(args[0] if args else "%H:%M:%S"))
        e.set('date',  lambda args: _time.strftime(args[0] if args else "%Y-%m-%d"))
        # Random
        import random as _random
        e.set('rand',    lambda args: _random.random())
        e.set('randInt', lambda args: _random.randint(int(args[0]), int(args[1])))
        e.set('shuffle', lambda args: (_random.shuffle(args[0]), args[0])[1])
        e.set('pick',    lambda args: _random.choice(args[0]))
        # String extras
        e.set('startsWith', lambda args: args[0].startswith(args[1]))
        e.set('endsWith',   lambda args: args[0].endswith(args[1]))
        e.set('replace',    lambda args: args[0].replace(args[1], args[2]))
        e.set('contains',   lambda args: args[1] in args[0])
        # List extras
        e.set('sum',    lambda args: sum(args[0]))
        e.set('count',  lambda args: args[0].count(args[1]))
        e.set('idx',    lambda args: args[0].index(args[1]) if args[1] in args[0] else -1)
        e.set('zip2',   lambda args: [list(pair) for pair in zip(args[0], args[1])])
        e.set('uniq',   lambda args: list(dict.fromkeys(args[0])))
        # System
        e.set('sysArgs', lambda _: sys.argv[2:])
        e.set('sysEnv',  lambda args: os.environ.get(args[0], None))
        # Constants (set as plain values)
        self.global_env.vars['pi']  = math.pi
        self.global_env.vars['inf'] = float('inf')

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
        raise TypeError(f"Не является функцией: {fn}")

    def _reduce(self, lst, fn, acc):
        for item in lst:
            acc = self._call_fn(fn, [acc, item])
        return acc

    def run(self, ast, env=None):
        if env is None:
            env = self.global_env
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

        elif kind == 'INDEX_ASSIGN':
            _, name, idx_node, val_node = node
            lst = env.get(name)
            idx = self.eval(idx_node, env)
            lst[idx] = self.eval(val_node, env)

        elif kind == 'PRINT':
            _, val_node, newline = node
            val = self.eval(val_node, env)
            end = '\n' if newline else ''
            print(self.to_str(val), end=end)

        elif kind == 'INPUT':
            _, name, prompt_node = node
            prompt = self.to_str(self.eval(prompt_node, env)) if prompt_node else ''
            val = input(prompt)
            env.assign(name, val)

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
            iterable = self.eval(iter_node, env)
            for item in iterable:
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
            _, name, params, body = node
            fn = Function(name, params, body, env)
            env.set(name, fn)

        elif kind == 'RETURN':
            _, val_node = node
            raise ReturnException(self.eval(val_node, env))

        elif kind == 'BREAK':
            raise BreakException()

        elif kind == 'CONTINUE':
            raise ContinueException()

        elif kind == 'IMPORT':
            pass  # placeholder

        elif kind == 'EXPR_STMT':
            return self.eval(node[1], env)

        elif kind == 'BLOCK':
            return self.exec_block(node, env)

    def eval(self, node, env):
        kind = node[0]

        if kind == 'INT':    return node[1]
        if kind == 'FLOAT':  return node[1]
        if kind == 'BOOL':   return node[1]
        if kind == 'STRING': return node[1]
        if kind == 'NIL':    return None

        if kind == 'FSTRING':
            template = node[1]
            def replace_expr(m):
                expr_src = m.group(1)
                tokens = tokenize(expr_src)
                parser = Parser(tokens)
                expr_ast = parser.parse_expr()
                val = self.eval(expr_ast, env)
                return self.to_str(val)
            return re.sub(r'\{([^}]+)\}', replace_expr, template)

        if kind == 'VAR':
            return env.get(node[1])

        if kind == 'LIST':
            return [self.eval(item, env) for item in node[1]]

        if kind == 'DICT':
            return {self.eval(k,env): self.eval(v,env) for k,v in node[1]}

        if kind == 'BINOP':
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
            if op == '&&': return lv and rv
            if op == '||': return lv or rv

        if kind == 'UNOP':
            _, op, val = node
            v = self.eval(val, env)
            if op == '-': return -v
            if op == '!': return not v

        if kind == 'CALL':
            _, fn_node, arg_nodes = node
            fn = self.eval(fn_node, env)
            args = [self.eval(a, env) for a in arg_nodes]
            return self._call_fn(fn, args)

        if kind == 'INDEX':
            _, obj_node, idx_node = node
            obj = self.eval(obj_node, env)
            idx = self.eval(idx_node, env)
            return obj[idx]

        if kind == 'METHOD':
            _, obj_node, method, arg_nodes = node
            obj = self.eval(obj_node, env)
            args = [self.eval(a, env) for a in arg_nodes]
            # string methods
            if method == 'up':    return obj.upper()
            if method == 'lo':    return obj.lower()
            if method == 'trim':  return obj.strip()
            if method == 'split': return obj.split(args[0] if args else ' ')
            if method == 'find':  return obj.find(args[0])
            if method == 'rep':   return obj * args[0]
            if method == 'sub':   return obj[args[0]:args[1] if len(args)>1 else None]
            if method == 'has':   return args[0] in obj
            # list methods
            if method == 'push':  obj.append(args[0]); return obj
            if method == 'pop':   return obj.pop()
            if method == 'sort':  return sorted(obj)
            if method == 'rev':   return list(reversed(obj))
            if method == 'len':   return len(obj)
            if method == 'has':   return args[0] in obj
            raise AttributeError(f"Метод '{method}' не найден")

        if kind == 'ATTR':
            _, obj_node, attr = node
            obj = self.eval(obj_node, env)
            if attr == 'len': return len(obj)
            return getattr(obj, attr)

        raise RuntimeError(f"Неизвестный узел AST: {node}")

    def to_str(self, val):
        if val is None:   return "nil"
        if val is True:   return "T"
        if val is False:  return "F"
        if isinstance(val, list):
            return "[" + ", ".join(self.to_str(v) for v in val) + "]"
        if isinstance(val, dict):
            pairs = ", ".join(f"{self.to_str(k)}: {self.to_str(v)}" for k,v in val.items())
            return "{" + pairs + "}"
        return str(val)


# ─────────────────────────────────────────────
#  REPL + FILE RUNNER
# ─────────────────────────────────────────────

def run_code(source, interp=None):
    if interp is None:
        interp = Interpreter()
    try:
        tokens = tokenize(source)
        parser = Parser(tokens)
        ast = parser.parse()
        interp.run(ast)
    except (SyntaxError, NameError, TypeError, RuntimeError, KeyError, IndexError, ZeroDivisionError) as e:
        print(f"[Ошибка] {e}", file=sys.stderr)
    return interp

def repl():
    print("MinLang REPL v1.0  |  'q' для выхода  |  'help' для справки")
    print("─" * 55)
    interp = Interpreter()
    buf = []
    while True:
        try:
            prompt = "... " if buf else ">>> "
            line = input(prompt)
            if line.strip() == 'q':
                print("До свидания!")
                break
            if line.strip() == 'help':
                print_help()
                continue
            if line.strip() == 'cls':
                os.system('clear')
                continue
            buf.append(line)
            # try to run
            src = '\n'.join(buf)
            open_braces = src.count('{') - src.count('}')
            if open_braces > 0:
                continue  # wait for block to close
            run_code(src, interp)
            buf = []
        except KeyboardInterrupt:
            buf = []
            print()
        except EOFError:
            print("\nДо свидания!")
            break

def print_help():
    help_text = """
╔══════════════════════════════════════════╗
║         MinLang — справка                ║
╠══════════════════════════════════════════╣
║ ПЕРЕМЕННЫЕ                               ║
║  L x = 5         → let x = 5            ║
║  x = 10          → переприсвоение        ║
║                                          ║
║ ВЫВОД                                    ║
║  pt "Hello"      → print (без \n)        ║
║  ptl "Hello"     → println (с \n)        ║
║  pt f"{x}+{y}"   → f-строка             ║
║                                          ║
║ ВВОД                                     ║
║  inp x           → читать в x            ║
║  inp "Имя: " x   → с подсказкой          ║
║                                          ║
║ УСЛОВИЯ                                  ║
║  if x > 5 { }                            ║
║  elif x == 5 { }                         ║
║  el { }                                  ║
║                                          ║
║ ЦИКЛЫ                                    ║
║  lp i in rng(10) { }    → for            ║
║  wh x < 10 { }          → while          ║
║  brk                    → break          ║
║  cnt                    → continue       ║
║                                          ║
║ ФУНКЦИИ                                  ║
║  fn add(a, b) { rt a+b }                 ║
║  add(2, 3)                               ║
║                                          ║
║ ТИПЫ                                     ║
║  T / F           → true / false          ║
║  nil             → null                  ║
║  [1,2,3]         → список                ║
║  {"k": "v"}      → словарь               ║
║                                          ║
║ ВСТРОЕННЫЕ ФУНКЦИИ                       ║
║  len, sqrt, abs, int, str, flt           ║
║  rng, push, pop, sort, rev               ║
║  up, lo, trim, split, join, find         ║
╚══════════════════════════════════════════╝
"""
    print(help_text)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        path = sys.argv[1]
        try:
            src = open(path, encoding='utf-8').read()
        except FileNotFoundError:
            print(f"[Ошибка] Файл не найден: {path}", file=sys.stderr)
            sys.exit(1)
        run_code(src)
    else:
        repl()
