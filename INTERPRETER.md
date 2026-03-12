# MinLang — How the Interpreter Works

This document explains what happens inside `minlang.py` from the moment
you type `python minlang.py program.ll` to the moment output appears on screen.

---

## The Big Picture

Every interpreter (and compiler) does the same three jobs, in order:

```
Source text  (.ll file)
     │
     ▼  Stage 1 — TOKENIZER
     │
  Token list  [('IDENT','L'), ('IDENT','x'), ('ASSIGN','='), ('INT','5'), …]
     │
     ▼  Stage 2 — PARSER
     │
  AST (Abstract Syntax Tree)   ('LET', 'x', ('INT', 5))
     │
     ▼  Stage 3 — INTERPRETER
     │
  Output / side effects
```

Each stage has one job and knows nothing about the others.
You can think of them as an assembly line.

---

## Stage 1 — The Tokenizer

**File location:** `tokenize()` function, top of `minlang.py`

**Input:** a raw string of source code, e.g. `'L x = 5 + 3\n'`  
**Output:** a flat list of `(type, value)` pairs called **tokens**

### What is a token?

A token is the smallest meaningful unit in the language.
Just like a sentence is made of words, source code is made of tokens.

```
L x = 5 + 3
```

becomes:

```python
[
  ('IDENT',  'L'),
  ('IDENT',  'x'),
  ('ASSIGN', '='),
  ('INT',    '5'),
  ('OP',     '+'),
  ('INT',    '3'),
  ('NEWLINE','\n'),
]
```

### How it works

The tokenizer keeps a **position cursor** that starts at character 0.
At each step it tries every regex pattern in `TOKEN_PATTERNS` (in order)
against the text starting at the cursor position.
The first pattern that matches wins; the cursor jumps forward by the
length of the match, and the token is recorded.

Two token types are silently **discarded**:
- `COMMENT` — everything after `##`
- `INDENT` — spaces and tabs (MinLang doesn't care about indentation)

### Why the order of patterns matters

Patterns are tried **first-to-last**, so more specific patterns must
come before general ones:

- `==` must be matched before `=`, otherwise `==` would be seen as two `=` tokens
- `FLOAT` must come before `INT`, otherwise `3.14` would be tokenized as `3` then `.14`
- `BOOL` (`\b(T|F)\b`) uses word boundaries so it only matches the standalone
  letters T and F, not the T inside "True" or a variable called "Tax"

### Error handling

If the cursor reaches a character that no pattern can match, a
`SyntaxError` is raised immediately with the position in the source.

---

## Stage 2 — The Parser

**File location:** `Parser` class in `minlang.py`

**Input:** the token list from Stage 1  
**Output:** an **Abstract Syntax Tree (AST)**

### What is an AST?

An AST is a tree of nested Python tuples.
Each tuple represents one piece of code:

| Source | AST node |
|---|---|
| `42` | `('INT', 42)` |
| `x` | `('VAR', 'x')` |
| `a + b` | `('BINOP', '+', ('VAR','a'), ('VAR','b'))` |
| `L x = 5` | `('LET', 'x', ('INT', 5))` |
| `if cond { }` | `('IF', cond_node, body_node, [], None)` |
| `fn f(x) { rt x }` | `('FUNCDEF', 'f', ['x'], body_node)` |

The tree structure naturally captures **nesting** and **priority**:
`2 + 3 * 4` becomes a tree where `*` is deeper (higher priority) than `+`:

```
  BINOP +
  ├── INT 2
  └── BINOP *
      ├── INT 3
      └── INT 4
```

### Recursive Descent

The parser is a **recursive descent** parser.
There is one method per grammar rule; each method may call others.
The call depth mirrors the nesting of the source code.

The methods are ordered by **operator precedence** (lowest first):

```
parse_expr
  └─ parse_or          (||)
       └─ parse_and        (&&)
            └─ parse_compare   (== != < > <= >=)
                 └─ parse_additive    (+ -)
                      └─ parse_multiplicative  (* / %)
                           └─ parse_unary  (- !)
                                └─ parse_postfix  (calls, index, methods)
                                     └─ parse_primary  (literals, (expr), [list], {dict})
```

When `parse_additive` calls `parse_multiplicative`, it means `*` and `/`
bind tighter than `+` and `-` — which is exactly what we want.

### Navigation helpers

The parser keeps a `pos` cursor into the token list and uses three helpers:

- `current()` — return the token at `pos` without moving
- `advance()` — return the token at `pos` **and** move forward
- `expect(type)` — assert the current token has the right type, then advance;
  raises `SyntaxError` if it doesn't

### Lookahead for ambiguity

Sometimes the parser needs to look ahead to decide what it's reading.
For example, `x = 5` (assignment) vs `x == 5` (comparison) both start
with an identifier.  The parser saves its position, peeks at the next
token, and rewinds if it was wrong:

```python
save = self.pos
self.advance()           # consume the identifier
if self.current()[0] == 'ASSIGN':
    ...                  # it's an assignment
else:
    self.pos = save      # rewind — it's something else
```

---

## Stage 3 — The Interpreter

**File location:** `Interpreter` class in `minlang.py`

**Input:** the AST from Stage 2  
**Output:** the actual execution of the program

### Environment (scopes)

The interpreter stores variables in an **Environment** object —
essentially a dictionary of `name → value`.

Every block creates a **child environment** that holds a reference to
its **parent**:

```
global env  { pi: 3.14, fact: <fn> }
    │
    └─ function call env  { n: 5 }
           │
           └─ if-branch env  { }
```

When a variable is looked up, the interpreter first checks the current
environment; if not found, it walks up to the parent, then the grandparent,
until it reaches the global environment.  This is **lexical scoping**.

`L x = 5` always creates in the **current** scope (`env.set`).  
`x = 5` (reassignment) searches up the chain and updates wherever it
was first declared (`env.assign`).

### exec_stmt vs eval

The interpreter has two kinds of methods:

- **`exec_stmt(node, env)`** — executes a statement; produces **side effects**
  (printing, writing to a variable, looping) but does not return a value
  the caller needs.

- **`eval(node, env)`** — evaluates an expression; always **returns a value**
  (a number, string, list, function object, etc.)

The top-level program is one big `BLOCK` containing statements.
Each statement may contain expressions (e.g. the right-hand side of
an assignment, the condition of an `if`), which are handled by `eval`.

### Built-in functions

Built-ins are stored as Python **lambda functions** directly in the
global environment.  They follow a uniform calling convention:
they receive a single Python list `args` of already-evaluated values
and return a Python value.

```python
e.set('sqrt', lambda args: math.sqrt(args[0]))
e.set('len',  lambda args: len(args[0]))
```

When the interpreter sees a `CALL` node it:
1. Evaluates the function expression (looks up the name)
2. Evaluates each argument expression
3. Calls `_call_fn(fn, args)` which works for both lambdas and user functions

### User-defined functions and closures

A `fn` definition creates a `Function` object that stores:
- the parameter names
- the body AST node
- a **reference to the current environment** (the closure)

When the function is called later, a new child environment is created
**from the closure environment**, not from wherever the call happens.
This is what makes closures work:

```
fn makeAdder(n) {
    fn add(x) { rt x + n }    ## 'n' is captured here
    rt add
}
L add5 = makeAdder(5)
ptl add5(10)    ## still knows n=5 even though makeAdder has returned
```

### Control flow via exceptions

`return`, `break`, and `continue` are implemented using Python exceptions:

| MinLang | Python exception |
|---|---|
| `rt expr` | `raise ReturnException(value)` |
| `brk` | `raise BreakException()` |
| `cnt` | `raise ContinueException()` |

This is a standard interpreter technique.
When `rt` is hit inside a function, `ReturnException` unwinds the call
stack automatically until it is caught in `_call_fn`.
`BreakException` unwinds until it is caught in the `FOR` or `WHILE`
handler in `exec_stmt`.

No flags need to be threaded through every function — Python's exception
mechanism handles the unwinding for free.

### F-string evaluation

F-strings like `f"x = {x+1}"` are evaluated lazily at runtime.
The interpreter uses a regex to find every `{...}` inside the template,
re-tokenizes and re-parses the expression inside the braces, evaluates
it in the current environment, and substitutes the result.

---

## The REPL

The REPL (Read-Eval-Print Loop) is the interactive mode you get when
you run `python minlang.py` with no file argument.

It works by buffering lines until the number of `{` equals the number
of `}` (meaning all open blocks are closed), then running the buffer
through the same `tokenize → parse → run` pipeline as a file.

The key difference is that **the interpreter object is reused** between
inputs, so variables declared in one line are still visible in the next.

---

## Error Handling

Errors are caught at the top of the pipeline in `run_code()`:

```python
try:
    tokens = tokenize(source)    # SyntaxError if unknown character
    ast    = parser.parse()      # SyntaxError if unexpected token
    interp.run(ast)              # NameError, TypeError, ZeroDivisionError, etc.
except (...) as e:
    print(f"[Error] {e}")
```

The interpreter does **not** crash on errors — it prints the message and
continues (especially useful in the REPL).

---

## Summary

```
minlang.py program.ll
    │
    ├─ open file, read source text
    │
    ├─ tokenize(source)
    │    regex scan → list of (type, value) tokens
    │
    ├─ Parser(tokens).parse()
    │    recursive descent → nested tuple AST
    │
    ├─ Interpreter().run(ast)
    │    walk AST, exec_stmt / eval
    │    Environment chain for scoping
    │    _call_fn for both lambdas and user functions
    │    exceptions for return / break / continue
    │
    └─ output appears on screen
```

The entire interpreter is ~600 lines of Python.
No external libraries are used — just `re`, `math`, `sys`, `os`,
`time`, and `random` from the standard library.
