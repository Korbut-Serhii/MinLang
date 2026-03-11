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

## Usage

```bash
# Run a source file
python minlang.py program.ll

# Interactive REPL (v0.5 and later)
python minlang.py
```
