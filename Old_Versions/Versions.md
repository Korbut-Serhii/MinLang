# MinLang

MinLang is a minimalist programming language with a `.minl` file extension.
Maximum expressive power, minimum keystrokes.

This repository tracks the full development history of the interpreter —
from a bare-bones "variables and print" concept all the way to
a complete implementation with collections, closures, higher-order functions,
structs, and a standard library.

---

## Architecture

Every version of the interpreter follows the same three-stage pipeline:

```
Source code (.minl)
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

#### Module system `use "file.minl"`
Executes another `.minl` file in the **current scope**, making all its
functions and variables available to the caller. This is intentionally
simple: no namespacing, no import aliases — just a clean way to split
a large program into files.

```
## utils.minl
fn clamp(x, lo, hi) { rt x < lo ? lo : (x > hi ? hi : x) }

## main.minl
use "utils.minl"
ptl clamp(150, 0, 100)   ## 100
```

#### Improved float output
Whole-number floats now display without the trailing `.0` (so `3.0`
prints as `3` and `1000000.0` prints as `1000000`). Decimal values
strip unnecessary trailing zeros. The `fmt` built-in gives full control
for cases that need precise formatting.

```
ptl 3.0              ## 3
ptl 3.14             ## 3.14
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

---

### v1.2 — Structs (OOP) and line numbers in errors

**File:** `v1.2_minlang.py`

The language gains its first object-oriented feature: user-defined types
with methods. Error messages now report the exact source line where a
problem occurred, making debugging significantly faster.

**What's new:**

#### Structs — user-defined types `struct Name { }`
A struct bundles data and the functions that operate on it into a single
named type. Each instance of a struct carries its own copy of the attributes
set inside methods.

```
struct Dog {
    fn init(name, age) {
        self.name = name
        self.age  = age
    }
    fn bark() {
        ptl f"Woof! I am {self.name}."
    }
}

L d = Dog("Rex", 3)
d.bark()
```

#### `self` — the instance inside a method
Inside any struct method, `self` refers to the specific instance the method
was called on. `self` is injected automatically — it does not appear in the
parameter list. Attributes are created and read via `self.name`.

#### Constructor `init`
The method named `init` runs automatically whenever an instance is created.
It receives any arguments passed to the struct call and is the right place
to set up initial attribute values.

#### Attribute assignment — outside and inside methods
Attributes can be written from outside the struct as well as from within:

```
d.name = "Max"       ## from outside
## self.age += 1      ## from inside a method (compound assign works too)
```

Compound assignment (`+=`, `-=`, `*=`, `/=`, `%=`) is fully supported on
`self` attributes inside methods.

#### Custom `str` method
Defining a method called `str` controls how an instance is displayed when
converted to text — including inside f-strings and when `str(obj)` is called:

```
struct Point {
    fn init(x, y) { self.x = x   self.y = y }
    fn str()      { rt f"Point({self.x}, {self.y})" }
}
L p = Point(3, 4)
ptl str(p)    ## Point(3, 4)
```

#### OOP built-in functions
Three new built-ins support runtime type inspection of struct instances:

| Function | Returns |
|---|---|
| `isObj(v)` | `T` if `v` is any struct instance |
| `className(v)` | The struct name as a string, e.g. `"Dog"` |
| `instanceof(v, Cls)` | `T` if `v` is an instance of `Cls` specifically |

#### Nil-safe access on instances
The existing `?.` operator works on struct instances: `obj?.attr` and
`obj?.method()` return `nil` without crashing if `obj` is `nil`.

#### Line numbers in all error messages
The tokenizer now tracks the current line number and attaches it to every
token. The parser includes `[line N]` in every `SyntaxError`. The
interpreter wraps every statement in a `SOURCELOC` node that keeps
`_current_line` up to date, so runtime errors also show the correct line:

```
[Error] [line 7] Variable 'scroe' is not defined
[Error] [line 3] Unknown character: '@'
[Error] [line 12] division by zero
```

This applies to errors inside struct methods too — the reported line is the
line inside the method body where the failure occurred, not the line of the
method call.

**Design notes:**

*Structs in the parser:* `parse_struct` reads a `struct Name { }` block and
collects method definitions using the existing `parse_fn` helper. The result
is a `STRUCTDEF` AST node containing a dict of `(params, body, variadic)`
triples.

*Runtime representation:* `MinLangClass` holds the struct name and its
method `Function` objects. `MinLangInstance` holds a reference to its class
and a plain dict of instance attributes. Calling a `MinLangClass` like a
function constructs a `MinLangInstance` and calls `init` if defined.
`_call_method` injects `self` into the method's local scope before executing.

*Attribute assignment (`ATTR_ASSIGN`):* the parser detects `ident.attr =`
patterns in statement position. The interpreter checks that the target is a
`MinLangInstance` and writes directly to `instance.attrs`.

*Compound attribute assignment (`ATTR_COMPOUND_ASSIGN`):* detected as
`ident.attr op=` in statement position, resolves to a read-modify-write
on `instance.attrs`.

*`_dispatch_method` routing:* when `obj` is a `MinLangInstance`, method
dispatch goes through `_call_method` with `self` bound, before any
string/list/dict method checks.

*Line tracking:* each token in the tokenizer is now a `(type, value, line)`
triple. Line counts are bumped inside the tokenizer for every `\n` in any
matched span, which handles multiline strings correctly. The parser's
`parse`/`parse_block` wrap each statement in `('SOURCELOC', line, stmt)`.
`exec_block` unwraps these to update `self._current_line` before executing.
`run_code` prepends `[line N]` to any runtime error that doesn't already
carry a line prefix.

```
## All v1.2 features in one snippet

struct Vector2 {
    fn init(x, y) { self.x = x   self.y = y }
    fn add(other)  { rt Vector2(self.x + other.x, self.y + other.y) }
    fn len()       { rt sqrt(self.x ** 2 + self.y ** 2) }
    fn str()       { rt f"Vec({self.x}, {self.y})" }
}

L v1 = Vector2(3, 4)
L v2 = Vector2(1, 2)
L v3 = v1.add(v2)

ptl str(v1)               ## Vec(3, 4)
ptl v1.len()              ## 5
ptl instanceof(v1, Vector2)  ## T
ptl className(v1)         ## Vector2
```

---

### v1.3 — Inheritance, typed errors, namespaced modules, and bitwise operators

**File:** `v1.3_minlang.py`

The language takes a significant step toward production readiness. Four
independent subsystems are added — each one self-contained, none breaking
any existing code.

**What's new:**

#### Struct inheritance `extends` and `super`
A struct can extend another struct. The child inherits all parent methods and
can override them. `super.method(args)` calls the parent's version from within
a child method, making it possible to extend behaviour without duplicating code.
Inheritance chains can be arbitrarily deep.

```
struct Animal {
    fn init(name) { self.name = name }
    fn speak()    { rt f"{self.name} ..." }
}

struct Dog extends Animal {
    fn init(name, breed) {
        super.init(name)
        self.breed = breed
    }
    fn speak() { rt f"{self.name} Woof!" }
}

L d = Dog("Rex", "Lab")
ptl d.speak()       ## Rex Woof!
ptl d.name          ## Rex  (inherited attribute)
```

#### `instanceof` walks the inheritance chain
`instanceof(obj, Cls)` now returns `T` for any class in the ancestry, not just
the direct class of the instance. `className` still returns the concrete class.

```
struct GuideDog extends Dog {
    fn init(name) { super.init(name, "Golden") }
}

L g = GuideDog("Buddy")
ptl instanceof(g, GuideDog)   ## T
ptl instanceof(g, Dog)        ## T  ← new in v1.3
ptl instanceof(g, Animal)     ## T  ← new in v1.3
ptl className(g)              ## "GuideDog"
```

#### `throw` — user-defined errors
Any value can be thrown with `throw expr`. The `catch` block receives the
thrown value directly — not a stringified message — so struct instances can
be thrown as typed errors and `instanceof`-checked in the handler.

```
struct ValueError {
    fn init(msg) { self.msg = msg }
    fn str()     { rt f"ValueError: {self.msg}" }
}

fn divide(a, b) {
    if b == 0 { throw ValueError("division by zero") }
    rt a / b
}

try {
    divide(5, 0)
} catch e {
    ptl instanceof(e, ValueError)   ## T
    ptl e.msg                       ## "division by zero"
}
```

`throw` can also be used with plain values: `throw "something went wrong"`,
`throw 404`. Strings thrown this way are caught as-is, not wrapped in an object.

#### Namespaced modules `import "file" as name`
`import "file.minl" as alias` runs the file in an **isolated scope** and
binds the result to `alias`. All access goes through the alias — names from
the module do not leak into the calling scope.

Inside a module, `export name` marks specific names for export. If no
`export` statements are present, every top-level name is exported.

```
## math_utils.minl
fn square(x) { rt x * x }
fn cube(x)   { rt x * x * x }
L VERSION = "1.0"

export square
export cube
export VERSION

## main.minl
import "math_utils.minl" as math

ptl math.square(5)   ## 25
ptl math.cube(3)     ## 27
ptl math.VERSION     ## "1.0"
```

The older `use "file.minl"` (runs in current scope, no isolation) still works.

#### Integer division `//`
`a // b` performs integer (floor) division, always returning a whole number.
Inserted between `*/% ` and `**` in the precedence chain.

```
ptl 17 // 5    ## 3   (not 3.4)
ptl -7 // 2    ## -4  (floor toward negative infinity, same as Python)
```

#### Bitwise operators `& | ^ ~ << >>`
All six C-style bitwise operators are added, sitting between `&&/||` and the
comparison operators in the precedence hierarchy.

| Operator | Meaning | Example |
|---|---|---|
| `a & b` | Bitwise AND | `12 & 10` → `8` |
| `a \| b` | Bitwise OR | `8 \| 4` → `12` |
| `a ^ b` | Bitwise XOR | `15 ^ 9` → `6` |
| `~a` | Bitwise NOT (unary) | `~5` → `-6` |
| `a << n` | Left shift | `1 << 4` → `16` |
| `a >> n` | Right shift | `256 >> 3` → `32` |

```
ptl 8 & 12     ## 8
ptl 8 | 4      ## 12
ptl 1 << 4     ## 16
ptl ~5         ## -6
```

#### Deep recursion
Python's internal recursion limit is raised to 50 000 frames at interpreter
startup. This gives MinLang programs approximately 5 000–6 000 levels of
usable recursion depth, up from Python's default ~1 000.

**Design notes:**

*Inheritance:* `MinLangClass` gains a `parent` field. `_find_method` walks
the chain until it finds the method or exhausts the ancestors. `_call_method`
now receives the `dispatching_class` so it can inject the correct `super`
proxy — a `MinLangSuper(parent_class, instance)` object that dispatches
through the parent's method table while keeping `self` bound to the original
instance. This ensures multi-level `super` chains work correctly.

*`throw`:* a new `MinLangThrow(Exception)` Python exception class wraps the
thrown MinLang value. `TRY` handling is split: `MinLangThrow` is caught first
and the `.val` is exposed to the handler unchanged; Python exceptions are
caught second and stringified as before. Control-flow exceptions (`rt`, `brk`,
`cnt`) still pass through unaffected.

*`import as`:* `_run_module` creates a fresh child `Environment`, sets
`__exports__` to an empty list, executes the AST, then builds a
`MinLangModule(path, exports)` dict from the declared exports (or all names if
none were declared). `export name` in statement position appends to
`__exports__`. When a file is run directly (not via `import`), `__exports__`
is created silently — no error — so module files can be linted or tested
standalone.

*Bitwise:* six new token types (`OP_IDIV`, `OP_LSHIFT`, `OP_RSHIFT`,
`OP_BAND`, `OP_BOR`, `OP_BXOR`, `OP_BNOT`) are added to `TOKEN_PATTERNS`
after `&&` and `||` to avoid ambiguity. Three new parse levels (`parse_bor`,
`parse_bxor`, `parse_band`) sit between `parse_and` and `parse_compare`.
`parse_shift` sits between `parse_compare` and `parse_additive`.
`parse_multiplicative` gains a branch for `OP_IDIV`. `parse_unary` gains a
branch for `OP_BNOT`. The interpreter evaluates all six operators with Python's
native bitwise operations (casting operands to `int` first).

```
## All v1.3 features in one snippet

struct Shape {
    fn init(color) { self.color = color }
    fn area()      { rt 0 }
}

struct Circle extends Shape {
    fn init(color, r) {
        super.init(color)
        self.r = r
    }
    fn area() { rt pi * self.r ** 2 }
    fn str()  { rt f"Circle(r={self.r}, color={self.color})" }
}

L c = Circle("red", 5)
ptl c.area()                  ## 78.53...
ptl instanceof(c, Shape)      ## T
ptl str(c)                    ## Circle(r=5, color=red)

try {
    if c.r > 4 { throw "too big" }
} catch e {
    ptl f"Caught: {e}"        ## Caught: too big
}

ptl 100 // 7    ## 14
ptl 0xFF & 0x0F ## 15
ptl 1 << 8      ## 256
```

---

### v1.4 — Syntax completion: control flow, safety, and spread

**File:** `minlang.py`

A broad quality-of-life release that fills in the remaining gaps in the language's
control flow, function model, operator set, and standard library.
No breaking changes — all existing v1.3 code runs unchanged.

**What's new:**

#### `x++` / `x--` — increment and decrement
Statement-level shorthand for `x += 1` and `x -= 1`. Works on any numeric variable.

```
L n = 0
n++      ## n = 1
n++      ## n = 2
n--      ## n = 1
```

#### `??` nil-coalescing operator
`a ?? b` returns `a` if it is not `nil`, otherwise returns `b`.
Chains are right-associative: `a ?? b ?? c` tries `a`, then `b`, then `c`.

```
L name = nil
ptl name ?? "Guest"    ## Guest
ptl 0 ?? 99            ## 0  (0 is not nil)
```

#### `in` operator
`x in collection` returns `T` if `x` is found in a list, dict key set, or string.
Composes naturally with `if` and `wh`.

```
ptl 3 in [1, 2, 3]     ## T
ptl "name" in person   ## T  (dict key check)
ptl "ell" in "hello"   ## T
```

#### `do { } wh cond` — do-while loop
Runs the body first, then checks the condition. Guarantees at least one execution.

```
L i = 0
do { i++ } wh i < 5    ## i = 5
```

#### `sw` / `cs` / `df` — switch statement
Multi-way branching on a single value. Each `cs` can match one or more values.
`df` is the optional default branch. No fallthrough between cases.

```
sw day {
    cs 1, 7 { ptl "weekend" }
    cs 2, 3, 4, 5, 6 { ptl "weekday" }
    df { ptl "unknown" }
}
```

#### Default function parameters
Parameters can be given a default value with `=`. The default is used when
the caller omits that argument. Works for named functions and lambdas.

```
fn greet(name="World") {
    ptl f"Hello, {name}!"
}
greet()          ## Hello, World!
greet("Alice")   ## Hello, Alice!
```

#### `finally` block in `try / catch`
Code in `finally { }` runs whether or not an error occurred — even when `catch`
is triggered. Ideal for cleanup operations such as closing files or resetting state.

```
try {
    riskyOperation()
} catch e {
    ptl f"Error: {e}"
} finally {
    ptl "always runs"
}
```

#### `assert expr [, msg]`
Asserts that an expression is true. If it is false, throws an `AssertionError`.
An optional message string is appended to the error.

```
assert x > 0, "x must be positive"
```

#### `from "file" import { a, b }` — selective import
Imports specific names from a module file directly into the current scope,
without needing to use an alias. The names behave exactly as if defined locally.

```
from "math_utils.minl" import { square, cube }
ptl square(5)   ## 25  — no alias prefix needed
```

#### Spread operator `...`
`...expr` inside a list literal expands the list in-place.
Inside a dict literal it merges all key-value pairs.

```
L a = [1, 2, 3]
L b = [...a, 4, 5]      ## [1, 2, 3, 4, 5]

L d1 = {"x": 1}
L d2 = {"y": 2}
L m  = {...d1, ...d2}   ## {x: 1, y: 2}
```

#### New math built-ins
`trunc(x)` · `sign(x)` · `gcd(a,b)` · `lcm(a,b)` · `hypot(a,b)`
`asin(x)` · `acos(x)` · `atan(x)` · `atan2(y,x)`

#### New string methods
`s.padL(n)` · `s.padL(n, ch)` · `s.padR(n)` · `s.padR(n, ch)`
`s.repeat(n)` · `s.chars()` · `s.lstrip()` · `s.rstrip()`
`s.isNum()` · `s.isAlpha()`

**Design notes:**

*Tokenizer:* four new token types added to `TOKEN_PATTERNS` in order-sensitive
positions — `INC` (`++`) and `DEC` (`--`) before `PLUS_ASSIGN`/`MINUS_ASSIGN`;
`OP_NULLCO` (`??`) before `QMARK`; `SPREAD` (`...`) before `DOT`.

*`parse_fn`:* updated to return a six-element tuple
`('FUNCDEF', name, params, defaults, body, variadic)`. `parse_primary`'s lambda
branch receives the same treatment. `parse_struct` unpacks the new format.

*`parse_statement`:* dispatch added for `do`, `sw`, `assert`, and `from`
keywords; `INC`/`DEC` checks added to the IDENT branch.

*`parse_compare`:* rewritten with a `while True:` loop so the `in` keyword
(an `IDENT` token) is checked alongside the operator tokens.

*`parse_nullco`:* new parse level inserted between `parse_ternary` and
`parse_or`, right-associative via recursion.

*`parse_primary` spread:* spread check is performed **before** the regular
expression, so `[...a, 1]` produces `SPREAD_ITEM` nodes, not regular items.

*`parse_try`:* now returns a five-element tuple with an optional `finally_block`.
`exec_stmt`'s `TRY` handler wraps execution in Python `try/finally`.

*`_call_fn`:* iterates `fn.defaults` and evaluates each default expression in the
function's closure environment if the caller did not supply that argument.

```
## All v1.4 features in one snippet

fn describe(item, prefix="Item") {
    rt f"{prefix}: {item}"
}

L tags = ["sale", "new"]
L extra = ["hot"]
L all_tags = [...tags, ...extra]

lp tag in all_tags {
    ptl describe(tag)
}

L raw = nil
ptl raw ?? "unknown"    ## unknown

L n = 1
do { n++ } wh n < 4    ## n = 4

sw n {
    cs 4 { ptl "four" }
    df   { ptl "other" }
}

try {
    assert n == 4, "expected 4"
} catch e {
    ptl e
} finally {
    ptl "done"
}
```

---

## File index

```
v0.1_minlang.py     — variables and print
v0.2_minlang.py     — arithmetic expressions
v0.3_minlang.py     — conditionals and boolean logic
v0.5_minlang.py     — loops, functions, lexical scoping
v0.8_minlang.py     — lists, dicts, method calls, f-strings
ru/v0.9_minlang.py  — Unlisted version: lists, dicts, method calls, f-strings
v1.0_minlang.py     — standard library and REPL polish
v1.1_minlang.py     — syntax sugar, safety, and modules
v1.2_minlang.py     — structs (OOP) and line numbers in errors
v1.3_minlang.py     — inheritance, typed errors, namespaced modules, bitwise
v1.4_minlang.py     — control flow, safety, spread, new builtins
```

## Usage

```bash
# Run a source file
python minlang.py program.minl

# Interactive REPL (v0.5 and later)
python minlang.py
```