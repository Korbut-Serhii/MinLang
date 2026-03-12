# MinLang

MinLang is a minimalist programming language with a `.ll` file extension.
Maximum expressive power, minimum keystrokes.

This repository tracks the full development history of the interpreter —
from a bare-bones "variables and print" concept all the way to
a complete implementation with collections, closures, higher-order functions,
and a standard library.

---

## Architecture

Every version of the interpreter follows the same three-stage pipeline:

```
Source code (.ll)
      │
      ▼
  Tokenizer  ── splits raw text into a flat list of tokens
      │
      ▼
  Parser     ── builds an Abstract Syntax Tree (AST) from tokens
      │
      ▼
  Interpreter── walks the AST and executes each node
```

---

## Version history

### v0.1 — Proof of concept

**File:** `v0.1_minlang.py`

The first working interpreter. The only goal was to verify that the
tokenizer → parser → interpreter pipeline holds together at all.

**What works:**
- Variable declaration: `L x = 42`
- Print a value: `pt x`
- Types: integers (`INT`) and strings (`STRING`)
- Comments: `## this is a comment`

**Not yet supported:** arithmetic, conditions, loops, functions.

```
L name = "world"
L n = 99
pt name
pt n
```

---

### v0.2 — Arithmetic and expressions

**File:** `v0.2_minlang.py`

Variables can now store computed values, not just literals.

**What's new:**
- Arithmetic operators `+ - * / %` with correct precedence
- Unary minus: `-x`
- Floating-point numbers (`FLOAT`)
- Grouping with parentheses: `(a + b) * c`
- `ptl` — print with a trailing newline (vs `pt` which doesn't)
- Variable reassignment: `x = x + 1`

**Design note:** operator precedence is encoded structurally via recursive
descent — `parse_additive` calls `parse_multiplicative` calls `parse_unary`
calls `parse_primary`. No precedence tables needed; the call hierarchy
is the precedence hierarchy.

```
L a = 10
L b = 3
ptl a + b
ptl a * b - 1
ptl (a + b) * 2
```

---

### v0.3 — Conditionals and boolean logic

**File:** `v0.3_minlang.py`

The language gains branching. Boolean values and the full set of
comparison operators are introduced.

**What's new:**
- Boolean literals `T` and `F`
- Comparison operators: `== != < > <= >=`
- Logical operators: `&&` `||` `!`
- Conditionals: `if expr { }` and `el { }`
- Curly-brace blocks `{ }`

**Design note:** two new precedence levels are inserted above comparisons —
`parse_or` and `parse_and`. `parse_block` is split out from `parse_statement`
so that `if` bodies can contain any statement, including nested `if`s.

```
L x = 15
if x > 10 {
    ptl "big"
} el {
    ptl "small"
}
```

---

### v0.5 — Loops, functions, and scoped environments

**File:** `v0.5_minlang.py`

The biggest milestone. The language becomes Turing-complete.

**What's new:**
- `elif` — additional conditional branches
- `lp var in iterable { }` — for loop
- `wh cond { }` — while loop
- `brk` / `cnt` — break and continue
- `fn name(a, b) { rt a + b }` — function definitions
- `rt expr` — return a value
- `inp` / `inp "prompt" x` — read user input
- Basic built-ins: `len sqrt abs pow max min rng int flt str push pop sort`

**Design note:** the flat `self.env` dict is replaced by an `Environment`
class with a parent-chain for lexical scoping. Closures are captured in the
`Function` object at definition time. Control flow (`rt`, `brk`, `cnt`) is
implemented via Python exceptions — a standard tree-walking interpreter
technique that avoids threading return/break flags through every method manually.

```
fn factorial(n) {
    if n <= 1 { rt 1 }
    rt n * factorial(n - 1)
}
ptl factorial(10)

lp i in rng(5) {
    if i == 3 { cnt }
    ptl i
}
```

---

### v0.8 — Collections, method calls, and f-strings

**File:** `v0.8_minlang.py`

The language gets data structures and string interpolation.

**What's new:**
- Lists: `[1, 2, 3]`, index access `x[0]`, index assignment `x[0] = 99`
- Dicts: `{"key": "val"}`, access `d["key"]`, assignment `d["k"] = v`
- F-strings: `f"hello {name}, sum = {a + b}"`
- Method call syntax: `"hello".up()`, `lst.push(4)`
- Attribute shorthand: `lst.len` instead of `len(lst)`
- Extended stdlib: `map`, `flt2`, `red`, `rev`, `sum`, `join`, `split`,
  `find`, `replace`, `rand`, `randInt`, `pick`

**Design note:** `parse_postfix` is extended with three chained cases —
function call `()`, index `[]`, and dot access `.`. Because each case loops
back to check for another postfix operator, chains like `a[0].split(",")[1]`
parse correctly without extra rules. F-strings are compiled lazily: the
`{expr}` segments are re-tokenized and re-parsed at evaluation time rather
than at parse time, which keeps the main parser simple.

```
L nums = [3, 1, 4, 1, 5, 9]
ptl nums.sort()

fn double(x) { rt x * 2 }
ptl map(nums, double)

L person = {"name": "Alice", "age": 30}
ptl f"Name: {person["name"]}, age: {person["age"]}"
```

---

### v1.0 — Standard library and REPL polish

**File:** `v1.0_minlang.py`

Final version of the first generation. The core language is frozen;
this release fills out the standard library and makes the interactive
REPL usable as a daily tool.

**What's new since v0.8:**
- Type inspection: `isInt isFlt isStr isLst isDct isBool isNil type`
- Safe type coercion: `toInt toFlt canInt canFlt`
- Time functions: `now clock date sleep`
- Extended random: `shuffle`
- String functions: `contains startsWith endsWith sub rep`
- List functions: `flat zip2 uniq count idx`
- File I/O: `read write`
- System functions: `sysArgs sysEnv exit`
- Constants: `pi` `inf`
- REPL commands `help` and `cls`
- Full quick-reference printed by `print_help()`

```
## FizzBuzz in MinLang
lp i in rng(1, 31) {
    if i % 15 == 0 { ptl "FizzBuzz" }
    elif i % 3 == 0 { ptl "Fizz" }
    elif i % 5 == 0 { ptl "Buzz" }
    el { ptl i }
}
```

---

### v1.1 — Syntax sugar, safety, and modules

**File:** `v1.1_minlang.py`

A focused quality-of-life release. No new data types or execution model
changes — every addition makes existing patterns shorter or safer to write.

**What's new:**

#### Compound assignment operators
`+=  -=  *=  /=  %=` — the five most common "update a variable" patterns
are now single tokens instead of verbose `x = x + 1` rewrites.

```
L score = 0
score += 10
score *= 2     ## score is now 20
```

#### Power operator `**`
Right-associative exponentiation, slotted between `*/%` and unary in the
precedence chain. `pow(a, b)` still works; `**` is just shorter.

```
ptl 2 ** 10       ## 1024
ptl 2 ** 3 ** 2   ## 512  (right-associative: 2 ** (3**2))
```

#### Ternary expression `cond ? a : b`
Single-line conditional value. Added as the lowest precedence expression
level, sitting above `||` in the parse chain.

```
L label = score >= 60 ? "pass" : "fail"
```

#### Slices `lst[a:b]`
Python-style half-open slices for both lists and strings. Either bound
can be omitted: `lst[:3]` means "first three", `lst[2:]` means "from index 2
to end". The parser extends the `LBRACKET` postfix case to detect `:`.

```
L nums = [0, 1, 2, 3, 4, 5]
ptl nums[1:4]   ## [1, 2, 3]
ptl nums[:3]    ## [0, 1, 2]

L s = "MinLang"
ptl s[3:]       ## "Lang"
```

#### List destructuring `L [a, b, *rest] = lst`
Unpack a list directly into named variables. The optional `*name` suffix
collects all remaining elements into a sub-list, similar to Python's
starred assignment.

```
L [head, *tail] = [10, 20, 30, 40]
## head = 10,  tail = [20, 30, 40]
```

#### Dict destructuring `L {a, b} = dct`
Extract dictionary values into variables using the key names. Equivalent to
writing `L a = dct["a"]  L b = dct["b"]` but in one line.

```
L user = {"name": "Alice", "score": 99}
L {name, score} = user
ptl f"{name} scored {score}"
```

#### Variadic functions `fn f(*args)`
A `*name` parameter in a function definition collects all extra positional
arguments into a list. Regular parameters can still precede it.

```
fn total(*nums) {
    L s = 0
    lp n in nums { s += n }
    rt s
}
ptl total(1, 2, 3, 4, 5)   ## 15
```

#### Anonymous functions (lambdas) `fn(x) { rt expr }`
`fn` can now appear inside an expression, not just as a statement. The
resulting `Function` object can be stored, passed, or called immediately.
This makes `map`, `flt2`, and `red` genuinely convenient without requiring
a named helper function for every one-liner.

```
L doubled = map([1, 2, 3], fn(x) { rt x * 2 })
L evens   = flt2([1,2,3,4,5,6], fn(x) { rt x % 2 == 0 })
L total   = red([1,2,3,4,5], fn(a, b) { rt a + b }, 0)
```

#### Error handling `try { } catch e { }`
Wraps a block in a Python `try/except`. If any runtime error occurs,
execution jumps to the `catch` block with the error message bound to the
given variable. Control-flow exceptions (`rt`, `brk`, `cnt`) pass through
unaffected.

```
try {
    L n = int("oops")
} catch e {
    ptl f"Caught: {e}"
}
```

#### Multiline strings `"""..."""`
Triple-quoted string literals that preserve embedded newlines verbatim.
The tokenizer matches them before single-quoted strings so they take
priority. Escape sequences (`\n`, `\t`, `\"`) still work inside them.

```
L msg = """Dear Alice,

Thank you for your message.

Regards"""
ptl msg
```

#### Dict methods
`.keys()`, `.values()`, `.items()`, `.get(key, default)`, `.has(key)`,
`.del(key)`, `.merge(other)` — the standard operations that make
dictionaries fully iterable and navigable without reaching for the
standalone built-in functions every time.

```
L d = {"a": 1, "b": 2, "c": 3}
lp pair in d.items() {
    ptl f"{pair[0]} → {pair[1]}"
}
ptl d.get("z", 0)   ## 0 (default — key not present)
```

#### Nil-safe access `?.`
`obj?.method()` and `obj?.attr` return `nil` immediately if `obj` is `nil`,
instead of crashing with a runtime error. Particularly useful when working
with optional values or results of safe conversions.

```
L result = toInt("abc")   ## nil
ptl result?.len()          ## nil — no crash
```

#### Module system `use "file.ll"`
Executes another `.ll` file in the **current scope**, making all its
functions and variables available to the caller. This is intentionally
simple: no namespacing, no import aliases — just a clean way to split
a large program into files.

```
## utils.ll
fn clamp(x, lo, hi) { rt x < lo ? lo : (x > hi ? hi : x) }

## main.ll
use "utils.ll"
ptl clamp(150, 0, 100)   ## 100
```

#### Improved float output
Whole-number floats now display without the trailing `.0` (so `3.0`
prints as `3` and `1000000.0` prints as `1000000`). Decimal values
strip unnecessary trailing zeros. The `fmt` built-in gives full control
for cases that need precise formatting.

```
ptl 3.0          ## 3
ptl 3.14         ## 3.14
ptl fmt(pi, ".4f")   ## 3.1416
```

**Design note:** compound assignment and slices required the most tokenizer
work — `+=` etc. needed to precede `+` in `TOKEN_PATTERNS`, and the slice
`[a:b]` case needed a COLON-detection branch inside the existing `LBRACKET`
postfix handler. Lambdas were the subtlest parser change: `fn` is now valid
in both statement position (named function definition) and expression
position (`parse_primary` checks for `fn` before falling through to `VAR`).
Everything else was additive — new AST node types, new `exec_stmt`/`eval`
branches, new built-in lambdas registered in `_setup_builtins`.

```
## All v1.1 features in one snippet
L [a, *rest] = [1, 2, 3, 4, 5]
a += 10
ptl a                                     ## 11
ptl 2 ** len(rest)                        ## 16  (2**4)
ptl len(rest) > 3 ? "long" : "short"      ## short

try {
    ptl int("bad")
} catch e {
    ptl f"error: {e}"
}

L d = {"x": 10, "y": 20}
L {x, y} = d
ptl map([x, y], fn(v) { rt v * 2 })      ## [20, 40]
```

---

## File index

```
v0.1_minlang.py   — variables and print
v0.2_minlang.py   — arithmetic expressions
v0.3_minlang.py   — conditionals and boolean logic
v0.5_minlang.py   — loops, functions, lexical scoping
v0.8_minlang.py   — lists, dicts, method calls, f-strings
v1.0_minlang.py   — standard library and REPL polish
v1.1_minlang.py   — syntax sugar, safety, and modules  ← current
```

## Usage

```bash
# Run a source file
python minlang.py program.ll

# Interactive REPL (v0.5 and later)
python minlang.py
```