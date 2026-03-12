# MinLang — A Complete Beginner's Guide

> **Who this guide is for:**  
> You have never written a line of code before. You don't know what a variable is.
> You don't know what a function is. That's completely fine — this guide explains
> everything from absolute zero, one step at a time.
>
> By the end you will be able to write real programs in MinLang.

---

## Table of Contents

1. [What is a program?](#1-what-is-a-program)
2. [How to run MinLang](#2-how-to-run-minlang)
3. [Your first line of code](#3-your-first-line-of-code)
4. [Variables — storing information](#4-variables--storing-information)
5. [Numbers and math](#5-numbers-and-math)
6. [Text (strings)](#6-text-strings)
7. [True and False (booleans)](#7-true-and-false-booleans)
8. [Getting input from the user](#8-getting-input-from-the-user)
9. [Making decisions — if / elif / el](#9-making-decisions--if--elif--el)
10. [Repeating things — loops](#10-repeating-things--loops)
11. [Organising code — functions](#11-organising-code--functions)
12. [Lists — keeping many values together](#12-lists--keeping-many-values-together)
13. [Dictionaries — labelled boxes](#13-dictionaries--labelled-boxes)
14. [Error handling — try / catch](#14-error-handling--try--catch)
15. [Structs — grouping data and behaviour together](#15-structs--grouping-data-and-behaviour-together)
16. [Modules — splitting code across files](#16-modules--splitting-code-across-files)
17. [Built-in tools — the standard library](#17-built-in-tools--the-standard-library)
18. [Putting it all together — full projects](#18-putting-it-all-together--full-projects)
19. [Quick Reference Card](#19-quick-reference-card)

---

## 1. What is a program?

A **program** is a list of instructions that you write, and the computer follows them
one by one, from top to bottom.

Think of it like a recipe:

```
1. Boil water
2. Add pasta
3. Wait 10 minutes
4. Drain
5. Serve
```

A MinLang program is exactly the same idea — just written in a language the computer
understands. You write the steps, save them in a file that ends in `.minl`, and then
run them.

The computer doesn't think. It doesn't guess. It does **exactly** what you wrote —
nothing more, nothing less. If you make a mistake, it will either stop with an error
message or do something you didn't expect. Both are normal. Every programmer deals
with this every single day.

---

## 2. How to run MinLang

You need two things:
- **Python 3** installed on your computer
- The file `minlang.py`

### Running a program file

Create a text file, name it something like `hello.minl`, write your code inside it,
then open a terminal and type:

```bash
python3 minlang.py hello.minl
```

The computer reads your `.minl` file and executes every line.

### The interactive mode (REPL)

If you run MinLang without a file:

```bash
python3 minlang.py
```

You get an interactive prompt that looks like this:

```
MinLang REPL v1.3  |  'q' to quit  |  'help' for reference
────────────────────────────────────────────────────────
>>>
```

You can type one line at a time and see the result immediately.
This is great for experimenting. Type `q` and press Enter to quit.

### Reading error messages

When something goes wrong, MinLang tells you exactly where the problem is:

```
[Error] [line 7] Variable 'scroe' is not defined
```

The `[line 7]` part is the line number in your source file where the error happened.
Open your file, go to that line, and that's where you need to look.

---

## 3. Your first line of code

The most basic thing a program can do is **show text on the screen**.

In MinLang, the command for that is `ptl` (short for "print line"):

```
ptl "Hello, world!"
```

Type that, run it, and you will see:

```
Hello, world!
```

### `pt` vs `ptl` — what's the difference?

There are two print commands:

| Command | What it does | Example output |
|---|---|---|
| `ptl "text"` | Prints the text **and moves to a new line** | `Hello` ← then cursor goes down |
| `pt "text"` | Prints the text **and stays on the same line** | `Hello` ← cursor stays here |

Example using both:

```
pt "Hello, "
pt "my "
ptl "friend!"
```

Output:
```
Hello, my friend!
```

All three words end up on the same line because `pt` doesn't move the cursor down.
Only `ptl` does.

### Comments — notes to yourself

A **comment** is a line (or part of a line) that the computer completely ignores.
You use it to leave yourself notes explaining what the code does.

In MinLang, comments start with `##`:

```
## This is a comment. The computer ignores this entire line.
ptl "This line runs."   ## This note is also ignored.
```

Get into the habit of writing comments. When you come back to your code
three weeks later, you'll thank yourself.

---

## 4. Variables — storing information

A **variable** is a named box where you store a piece of information.

Imagine you have a sticky note that says **"x = 5"**. Whenever you need
the number 5, you can just refer to it as "x" instead of writing 5 every time.
If you later change the sticky note to say "x = 10", everywhere that uses "x"
will now use 10.

### Declaring a variable

To create a variable in MinLang, you use the letter `L` (short for "let"):

```
L age = 25
```

This creates a variable called `age` and puts the value `25` inside it.

```
L name = "Alice"
L score = 100
L height = 1.75
```

### Using a variable

Once declared, just write the name wherever you want the value:

```
L age = 25
ptl age
```

Output:
```
25
```

```
L name = "Alice"
ptl "Hello, "
ptl name
```

Output:
```
Hello,
Alice
```

### Changing a variable's value

After you declare a variable with `L`, you can change its value at any time
by just writing the name and `=` again — **without** the `L`:

```
L score = 0
ptl score    ## prints 0

score = 50
ptl score    ## prints 50

score = 100
ptl score    ## prints 100
```

The `L` is only used the **first time** you create a variable.
After that, you just use the name.

### Compound assignment — updating a variable in one step

A very common pattern is updating a variable based on its current value:

```
score = score + 10
```

MinLang provides a shorter form for all five arithmetic operations:

| Write | Means |
|---|---|
| `x += n` | `x = x + n` |
| `x -= n` | `x = x - n` |
| `x *= n` | `x = x * n` |
| `x /= n` | `x = x / n` |
| `x %= n` | `x = x % n` |

So instead of `i = i + 1` in a loop counter, you write:

```
L i = 0
wh i < 10 {
    ptl i
    i += 1
}
```

This works anywhere you would write the long form — loops, scores, totals, anything.

### Why can't I just use `=` without `L` the first time?

If you forget the `L`, MinLang will warn you:

```
score = 50   ## Warning: 'score' used before declaration
```

The `L` makes it clear: "I am creating something new here."
The plain `=` means: "I am changing something that already exists."
This distinction helps you avoid accidental typos creating new variables.

### Variable naming rules

- Names can contain letters, numbers, and underscores `_`
- Names must **start** with a letter or underscore (not a number)
- Names are **case-sensitive**: `Score` and `score` are two different variables
- You cannot use reserved words like `if`, `fn`, `rt`, etc. as variable names

Good names:
```
L playerScore = 0
L first_name = "Bob"
L item2 = "sword"
```

Bad names (will cause errors):
```
L 2item = "sword"    ## starts with a number — not allowed
L if = 5             ## 'if' is a reserved keyword — not allowed
```

### Unpacking — assigning multiple variables at once

When you have a list and want its values in separate variables,
you can unpack them all in one line using `L [...]`:

```
## Old way — three separate lines
L coords = [10, 20, 30]
L x = coords[0]
L y = coords[1]
L z = coords[2]

## New way — one line
L [x, y, z] = [10, 20, 30]
```

The `*name` syntax collects all remaining elements into a sub-list:

```
L [first, *rest] = [1, 2, 3, 4, 5]
ptl first    ## 1
ptl rest     ## [2, 3, 4, 5]
```

You can also unpack a dictionary by key name:

```
L user = {"name": "Alice", "score": 99, "level": 7}
L {name, score, level} = user

ptl f"{name} is level {level} with {score} points."
```

This is exactly equivalent to `L name = user["name"]` etc., just shorter.
The variable names must match the dictionary keys exactly.

---

## 5. Numbers and math

MinLang has two kinds of numbers:

| Type | What it is | Example |
|---|---|---|
| Integer | Whole number, no decimal point | `42`, `-7`, `0` |
| Float | Number with a decimal point | `3.14`, `-0.5`, `100.0` |

### Basic arithmetic

```
L a = 10
L b = 3

ptl a + b    ## 13  (addition)
ptl a - b    ## 7   (subtraction)
ptl a * b    ## 30  (multiplication)
ptl a / b    ## 3.3333...  (division — always gives a float)
ptl a % b    ## 1   (remainder after division — called "modulo")
```

### The modulo operator `%`

This one confuses beginners. `a % b` gives you the **remainder** when
you divide `a` by `b`.

Examples:
```
10 % 3  →  1    (10 ÷ 3 = 3 remainder 1)
10 % 2  →  0    (10 ÷ 2 = 5 remainder 0, meaning it divides evenly)
7  % 4  →  3    (7  ÷ 4 = 1 remainder 3)
```

The most common use: **checking if a number is even or odd**:
```
L n = 8
if n % 2 == 0 {
    ptl "even"
} el {
    ptl "odd"
}
```

### The power operator `**`

`**` raises a number to a power. `2 ** 10` means 2 multiplied by itself 10 times:

```
ptl 2 ** 10    ## 1024
ptl 3 ** 3     ## 27
ptl 9 ** 0.5   ## 3.0  (square root via fractional exponent)
```

`**` is **right-associative**, meaning `2 ** 3 ** 2` is evaluated as
`2 ** (3 ** 2)` = `2 ** 9` = `512`, not `(2 ** 3) ** 2` = `64`.

The `pow(a, b)` built-in function does exactly the same thing — `**` is just shorter.

### Integer division `//`

Regular division `/` always returns a float: `17 / 5` gives `3.4`.
When you want only the whole-number part, use `//`:

```
ptl 17 // 5     ## 3    (not 3.4)
ptl 10 // 3     ## 3
ptl -7 // 2     ## -4   (rounds toward negative infinity)
```

This is useful for things like splitting items into groups, converting seconds
to minutes, or working with grid coordinates:

```
L seconds = 137
L minutes = seconds // 60    ## 2
L remaining = seconds % 60   ## 17
ptl f"{minutes}m {remaining}s"   ## 2m 17s
```

### Bitwise operators

Bitwise operators work on the binary representation of integers. They are mainly
used in low-level programming, flags, masks, and performance-sensitive code.

| Operator | Name | Example | Result |
|---|---|---|---|
| `a & b` | AND — bits set in both | `12 & 10` | `8` |
| `a \| b` | OR — bits set in either | `8 \| 4` | `12` |
| `a ^ b` | XOR — bits set in one but not both | `15 ^ 9` | `6` |
| `~a` | NOT — flip all bits | `~5` | `-6` |
| `a << n` | Left shift — multiply by 2ⁿ | `1 << 4` | `16` |
| `a >> n` | Right shift — divide by 2ⁿ | `256 >> 3` | `32` |

```
ptl 8 & 12      ## 8   (1000 & 1100 = 1000)
ptl 8 | 4       ## 12  (1000 | 0100 = 1100)
ptl 1 << 4      ## 16  (shift left 4 positions = multiply by 16)
ptl 256 >> 3    ## 32  (shift right 3 positions = divide by 8)
ptl ~5          ## -6
```

A common use — checking and setting flags with `&` and `|`:

```
L READ  = 1   ## 001
L WRITE = 2   ## 010
L EXEC  = 4   ## 100

L perms = READ | WRITE   ## 011 = 3
ptl perms & READ   ## 1 — READ is set
ptl perms & EXEC   ## 0 — EXEC is not set
```

### Order of operations

MinLang follows the same rules as maths.
From highest priority to lowest: `**` → `*`, `/`, `%` → `+`, `-`

Use parentheses `()` to change the order:

```
ptl 2 + 3 * 4       ## 14  (3*4 first, then +2)
ptl (2 + 3) * 4     ## 20  (2+3 first, then *4)
ptl 2 ** 3 + 1      ## 9   (2**3=8 first, then +1)
ptl 2 ** (3 + 1)    ## 16  (3+1=4 first, then 2**4)
```

### Math built-in functions

MinLang comes with ready-made math tools.
A **function** is something you call by name with values in parentheses:

```
ptl sqrt(16)        ## 4    — square root
ptl abs(-7)         ## 7    — absolute value (removes the minus sign)
ptl pow(2, 10)      ## 1024 — same as 2 ** 10
ptl floor(3.9)      ## 3    — round DOWN to nearest whole number
ptl ceil(3.1)       ## 4    — round UP to nearest whole number
ptl rnd(3.14159, 2) ## 3.14 — round to 2 decimal places
ptl max(5, 3, 8)    ## 8    — the largest value
ptl min(5, 3, 8)    ## 3    — the smallest value
```

The constant `pi` is available without calling a function:
```
ptl pi    ## 3.141592653589793
```

### Converting between number types

```
L x = int("42")     ## turns the text "42" into the number 42
L y = flt("3.14")   ## turns the text "3.14" into 3.14
L s = str(100)      ## turns the number 100 into the text "100"
```

This is important when working with user input — more on that in Section 8.

### How floats are displayed

Whole-number floats display without the trailing `.0`, and unnecessary trailing
zeros are stripped:

```
ptl 3.0        ## 3       (not "3.0")
ptl 1000000.0  ## 1000000 (not "1000000.0")
ptl 3.14       ## 3.14
```

Use `fmt` when you need precise formatting:
```
ptl fmt(pi, ".2f")    ## "3.14"
ptl fmt(pi, ".4f")    ## "3.1416"
ptl fmt(9.9, ".0f")   ## "10"
```

---

## 6. Text (strings)

A **string** is a piece of text. In MinLang, strings are always
wrapped in double quotes:

```
L greeting = "Hello, world!"
L empty    = ""
L sentence = "MinLang is easy to learn."
```

### Escape sequences — special characters inside strings

Some characters can't be typed directly inside a string.
You represent them with a backslash followed by a letter:

| Write | Meaning |
|---|---|
| `\n` | New line |
| `\t` | Tab (indent) |
| `\"` | A literal double-quote character |

```
ptl "Line one\nLine two"
```
Output:
```
Line one
Line two
```

```
ptl "Name:\tAlice"
```
Output:
```
Name:    Alice
```

### Multiline strings — `"""..."""`

When your text spans several lines, triple-quoted strings preserve
line breaks exactly as you write them:

```
L letter = """Dear Alice,

Thank you for your message.
We will respond shortly.

Regards,
The Team"""

ptl letter
```

Output:
```
Dear Alice,

Thank you for your message.
We will respond shortly.

Regards,
The Team
```

Everything between the opening `"""` and closing `"""` is part of the string,
including blank lines and indentation. Escape sequences like `\n` and `\t`
still work inside them.

### F-strings — putting variables inside text

An **f-string** lets you mix text and variable values in one line.
Put an `f` before the opening quote, and wrap any variable or expression in `{}`:

```
L name = "Alice"
L age  = 30
ptl f"My name is {name} and I am {age} years old."
```
Output:
```
My name is Alice and I am 30 years old.
```

You can put **any expression** inside the `{}`:
```
L a = 5
L b = 3
ptl f"The sum of {a} and {b} is {a + b}."
```
Output:
```
The sum of 5 and 3 is 8.
```

This is one of the most useful features in the language — you'll use it constantly.

### String slices — extracting a piece of text

A **slice** extracts a portion of a string without modifying the original.
Write `[start:stop]` — the result includes the character at `start` but
stops **before** `stop`:

```
L word = "MinLang"

ptl word[0:3]    ## "Min"   — characters 0, 1, 2
ptl word[3:]     ## "Lang"  — from index 3 to the end
ptl word[:3]     ## "Min"   — from the beginning up to index 3
```

Either bound can be omitted. A slice always returns a **new** string.

### String built-in functions

```
L s = "  Hello, World!  "

ptl len(s)              ## 18  — number of characters (including spaces)
ptl up(s)               ## "  HELLO, WORLD!  "  — all uppercase
ptl lo(s)               ## "  hello, world!  "  — all lowercase
ptl trim(s)             ## "Hello, World!"       — removes spaces from both ends
```

```
L sentence = "the quick brown fox"

ptl find(sentence, "quick")   ## 4  — position where "quick" starts (0 = first character)
ptl find(sentence, "cat")     ## -1 — returns -1 if not found

ptl contains(sentence, "fox")       ## T  — does the string contain "fox"?
ptl startsWith(sentence, "the")     ## T  — does it start with "the"?
ptl endsWith(sentence, "fox")       ## T  — does it end with "fox"?
```

```
L word = "hello"

ptl sub(word, 1, 3)          ## "el"            — characters from 1 up to (not including) 3
ptl rep(word, 3)              ## "hellohellohello" — repeat the string 3 times
ptl replace(word, "l", "r")  ## "herro"         — replace all "l" with "r"
```

```
## Splitting and joining
L csv = "apple,banana,cherry"
L parts = split(csv, ",")       ## ["apple", "banana", "cherry"]
ptl parts

L rejoined = join(parts, " | ")  ## "apple | banana | cherry"
ptl rejoined
```

---

## 7. True and False (booleans)

A **boolean** is a value that is either **true** or **false**.
In MinLang, these are written as `T` and `F`.

```
L is_raining = T
L sun_is_out = F
```

Booleans are what you get when you compare two things:

```
ptl 5 > 3      ## T  (5 is greater than 3 — true)
ptl 5 < 3      ## F  (5 is not less than 3 — false)
ptl 5 == 5     ## T  (5 equals 5)
ptl 5 != 3     ## T  (5 is not equal to 3)
ptl 5 >= 5     ## T  (5 is greater than or equal to 5)
ptl 5 <= 4     ## F  (5 is not less than or equal to 4)
```

### Combining conditions with `&&` and `||`

`&&` means **AND** — both sides must be true:
```
ptl 5 > 3 && 10 > 7    ## T  (both are true)
ptl 5 > 3 && 10 < 7    ## F  (second one is false)
```

`||` means **OR** — at least one side must be true:
```
ptl 5 > 3 || 10 < 7    ## T  (first one is true, so the whole thing is true)
ptl 5 < 3 || 10 < 7    ## F  (both are false)
```

`!` means **NOT** — flips true to false and vice versa:
```
ptl !T          ## F
ptl !F          ## T
ptl !(5 > 3)    ## F  (5>3 is true, !true is false)
```

### `nil` — the absence of a value

`nil` means "nothing" or "no value". It's what you get when something
doesn't have a result yet, or when a safe conversion fails:

```
L result = toInt("hello")   ## "hello" is not a number, so result = nil
ptl result                   ## nil
```

You can check for nil:
```
if result == nil {
    ptl "conversion failed"
}
```

### Nil-safe access — `?.`

When a value might be `nil`, calling a method or reading an attribute on it
would normally crash the program. The `?.` operator returns `nil` instead
of crashing:

```
L result = toInt("abc")   ## result = nil

## Old way — had to check manually:
if result != nil {
    ptl len(str(result))
}

## New way — one character does it:
ptl result?.len()    ## nil — no crash, no if needed
```

This works for method calls (`?.method()`) and attribute reads (`?.attr`).
It's most useful in chains where an earlier step might produce `nil`:

```
L user = nil
ptl user?.name          ## nil — no crash
ptl user?.score         ## nil — the whole chain short-circuits
```

---

## 8. Getting input from the user

`inp` pauses the program, waits for the user to type something and press Enter,
then stores what they typed into a variable:

```
inp name
ptl f"Hello, {name}!"
```

You can show a prompt message before they type:
```
inp "What is your name? " name
ptl f"Hello, {name}!"
```

### Important: `inp` always stores text

No matter what the user types, `inp` stores it as a **string** (text).
If you want to use it as a number, you must convert it:

```
inp "Enter your age: " raw_age

## raw_age is the text "25", not the number 25
## You must convert it:
L age = int(raw_age)
ptl f"In 10 years you will be {age + 10}."
```

### Handling bad input safely

What if the user types "hello" when you expected a number?
`int("hello")` will crash. Use `canInt` to check first:

```
inp "Enter a number: " raw

if canInt(raw) {
    L n = int(raw)
    ptl f"Your number doubled is {n * 2}."
} el {
    ptl "That was not a number."
}
```

`canInt` and `canFlt` **never crash** — they just return `T` or `F`.
`toInt` and `toFlt` are also safe — they return `nil` instead of crashing:

```
L n = toInt("hello")   ## n = nil, no crash
if n == nil {
    ptl "Could not convert."
}
```

---

## 9. Making decisions — `if` / `elif` / `el`

This is how you make your program do different things depending on a condition.

### Basic `if`

```
L temperature = 35

if temperature > 30 {
    ptl "It is hot outside."
}
```

The code inside the `{ }` **only runs if the condition is true**.
If the temperature were 20, nothing would print.

### `if` with `el` (else)

```
L temperature = 15

if temperature > 30 {
    ptl "It is hot."
} el {
    ptl "It is not hot."
}
```

`el` is short for "else". The code inside `el { }` runs **only if the
`if` condition was false**.

### `if` with `elif` (else if)

When you have more than two possibilities:

```
L score = 72

if score >= 90 {
    ptl "Grade: A"
} elif score >= 80 {
    ptl "Grade: B"
} elif score >= 70 {
    ptl "Grade: C"
} elif score >= 60 {
    ptl "Grade: D"
} el {
    ptl "Grade: F"
}
```

MinLang checks each condition **from top to bottom** and runs the **first one
that is true**. Once one matches, it skips the rest.

If `score` is 72:
- `score >= 90` → F, skip
- `score >= 80` → F, skip
- `score >= 70` → T ✓ → prints "Grade: C", done

### Nested conditions

You can put `if` inside `if`:

```
L age = 20
L has_ticket = T

if age >= 18 {
    if has_ticket {
        ptl "You may enter."
    } el {
        ptl "You need a ticket."
    }
} el {
    ptl "You must be 18 or older."
}
```

### Conditions with logic operators

```
L age = 25
L has_id = T

if age >= 18 && has_id {
    ptl "Welcome!"
}
```

```
L is_member = F
L has_coupon = T

if is_member || has_coupon {
    ptl "You get a discount."
}
```

### Ternary expression — `cond ? a : b`

A ternary expression is a compact `if/el` that produces a **value** rather
than running a block. It's useful when you want to choose between two values
on one line:

```
L label = score >= 60 ? "pass" : "fail"
```

Read it as: "if `score >= 60` then `"pass"`, otherwise `"fail"`."

Without the ternary, the same logic takes five lines:

```
L label = ""
if score >= 60 {
    label = "pass"
} el {
    label = "fail"
}
```

You can use a ternary anywhere an expression is allowed — inside an
f-string, as a function argument, as part of a larger expression:

```
ptl f"Result: {score >= 60 ? "pass" : "fail"}"
ptl age >= 18 ? "adult" : "minor"
```

Keep ternaries simple. If the condition or either branch is complicated,
a full `if/el` block is easier to read.

---

## 10. Repeating things — loops

A **loop** is a way to run the same block of code multiple times
without copy-pasting it.

### The `wh` loop (while)

`wh` means "while". It keeps running as long as a condition is true.

```
L count = 1

wh count <= 5 {
    ptl count
    count += 1
}
```

Output:
```
1
2
3
4
5
```

Step by step:
1. `count` is 1. Is `count <= 5`? Yes → print 1, add 1 → count is 2
2. `count` is 2. Is `count <= 5`? Yes → print 2, add 1 → count is 3
3. ... continues until count is 6
4. `count` is 6. Is `count <= 5`? No → stop

**Warning:** always make sure the condition will eventually become false,
or the loop will run forever. This is called an **infinite loop** and you
have to force-quit the program with Ctrl+C.

### The `lp` loop (for loop)

`lp` means "loop". It's used when you know exactly how many times you
want to repeat something.

```
lp i in rng(5) {
    ptl i
}
```

Output:
```
0
1
2
3
4
```

`rng(5)` produces the list of numbers `[0, 1, 2, 3, 4]`.
On each repetition, `i` gets the next number from the list.

**Important:** `rng(5)` starts at **0** and goes up to but **not including** 5.
That's standard in programming — counting usually starts at 0.

### `rng` variations

```
rng(5)         ## [0, 1, 2, 3, 4]         — from 0 to 4
rng(1, 6)      ## [1, 2, 3, 4, 5]         — from 1 to 5
rng(0, 10, 2)  ## [0, 2, 4, 6, 8]         — from 0 to 8, step of 2
rng(10, 0, -1) ## [10, 9, 8, 7, ..., 1]   — counting down
```

### Looping over a list

```
L fruits = ["apple", "banana", "cherry"]

lp fruit in fruits {
    ptl f"I like {fruit}"
}
```

Output:
```
I like apple
I like banana
I like cherry
```

### `brk` — stop the loop early

```
lp i in rng(10) {
    if i == 5 {
        brk    ## stop the loop when i reaches 5
    }
    ptl i
}
```

Output:
```
0
1
2
3
4
```

### `cnt` — skip to the next iteration

```
lp i in rng(10) {
    if i % 2 == 0 {
        cnt    ## skip even numbers
    }
    ptl i
}
```

Output:
```
1
3
5
7
9
```

`cnt` (short for "continue") skips the rest of the current loop body
and goes straight to the next number.

### Loops inside loops (nested loops)

```
lp row in rng(3) {
    lp col in rng(3) {
        pt f"({row},{col}) "
    }
    ptl ""    ## new line after each row
}
```

Output:
```
(0,0) (0,1) (0,2)
(1,0) (1,1) (1,2)
(2,0) (2,1) (2,2)
```

---

## 11. Organising code — functions

A **function** is a reusable named block of code.
Instead of writing the same logic over and over, you write it once,
give it a name, and call it whenever you need it.

### Defining a function

```
fn greet() {
    ptl "Hello there!"
}
```

This creates a function called `greet`. The code inside the `{ }` does
**not run yet** — it only runs when you **call** the function.

### Calling a function

```
greet()   ## now it runs
greet()   ## run it again
greet()   ## and again
```

Output:
```
Hello there!
Hello there!
Hello there!
```

### Functions with parameters (inputs)

Parameters are values you send into the function:

```
fn greet(name) {
    ptl f"Hello, {name}!"
}

greet("Alice")
greet("Bob")
greet("the world")
```

Output:
```
Hello, Alice!
Hello, Bob!
Hello, the world!
```

The variable `name` only exists **inside** the function. Each time you call
`greet("Alice")`, `name` becomes `"Alice"` for that one call.

### Functions with multiple parameters

```
fn add(a, b) {
    ptl a + b
}

add(3, 5)    ## prints 8
add(10, 20)  ## prints 30
```

### Functions that return a value

So far our functions just printed things. But usually you want the function
to **compute a result and give it back** to you so you can use it.

Use `rt` (short for "return") to send a value back:

```
fn add(a, b) {
    rt a + b    ## send the result back to whoever called this
}

L result = add(3, 5)    ## result = 8
ptl result               ## prints 8
ptl add(10, 20)          ## prints 30 directly
ptl f"3 + 5 = {add(3, 5)}"   ## works inside f-strings too
```

### A real example — a function that checks if a number is even

```
fn isEven(n) {
    rt n % 2 == 0
}

ptl isEven(4)    ## T
ptl isEven(7)    ## F

lp i in rng(10) {
    if isEven(i) {
        ptl f"{i} is even"
    }
}
```

### Recursion — a function calling itself

A function can call itself. This is called **recursion** and it's useful
for problems that naturally repeat.

The classic example is **factorial** (n! = n × (n-1) × ... × 1):

```
fn factorial(n) {
    if n <= 1 {
        rt 1          ## base case: stop here
    }
    rt n * factorial(n - 1)   ## call ourselves with a smaller number
}

ptl factorial(5)    ## 120  (5 × 4 × 3 × 2 × 1)
ptl factorial(10)   ## 3628800
```

How this works for `factorial(4)`:
```
factorial(4)
  = 4 * factorial(3)
  = 4 * (3 * factorial(2))
  = 4 * (3 * (2 * factorial(1)))
  = 4 * (3 * (2 * 1))
  = 4 * (3 * 2)
  = 4 * 6
  = 24
```

**Every recursive function needs a base case** (the `if n <= 1` part)
that stops the recursion. Without it the function would call itself forever.

### Functions are values too

In MinLang you can store a function in a variable and pass it around:

```
fn double(x) { rt x * 2 }

L myFn = double     ## store the function itself (no parentheses!)
ptl myFn(5)         ## 10 — call it through the variable
```

This becomes very useful with list operations (see Section 12).

### Variadic functions — accepting any number of arguments

A **variadic function** accepts any number of arguments. Add `*name` as the
last parameter and it will collect all extra arguments into a list:

```
fn greetAll(*names) {
    lp name in names {
        ptl f"Hello, {name}!"
    }
}

greetAll("Alice", "Bob", "Charlie")
```

Output:
```
Hello, Alice!
Hello, Bob!
Hello, Charlie!
```

You can mix regular parameters with `*args` — regular ones come first:

```
fn log(level, *messages) {
    lp msg in messages {
        ptl f"[{level}] {msg}"
    }
}

log("INFO", "Server started", "Listening on port 8080")
```

Output:
```
[INFO] Server started
[INFO] Listening on port 8080
```

### Anonymous functions — `fn(x) { rt expr }`

`fn` can appear inside an expression, not just as a statement. This is useful
when passing a simple transformation to `map` or `flt2` without needing to
define a separate named function:

```
## Named function — requires a definition far from where it's used
fn isPositive(x) { rt x > 0 }
L positives = flt2(numbers, isPositive)

## Anonymous function — written right where it's needed
L positives = flt2(numbers, fn(x) { rt x > 0 })
```

Anonymous functions are full closures — they capture variables from the
surrounding scope just like named functions do:

```
L threshold = 5
L big = flt2([1, 3, 7, 2, 9], fn(x) { rt x > threshold })
ptl big    ## [7, 9]
```

You can also store an anonymous function in a variable and call it later:

```
L square = fn(x) { rt x * x }
ptl square(7)    ## 49
```

### Variable scope — what lives where

Variables declared inside a function **do not exist outside** it:

```
fn doSomething() {
    L secret = 42
    ptl secret    ## works fine here
}

doSomething()
ptl secret    ## ERROR: 'secret' is not defined
```

This is called **scope** and it's a feature, not a bug. It means functions
can use whatever variable names they like without interfering with each other.

### Closures — functions that remember their surroundings

A function defined inside another function **remembers** the variables from
the outer scope even after the outer function has finished:

```
fn makeCounter() {
    L c = 0
    fn inc() {
        c += 1
        rt c
    }
    rt inc
}

L counter = makeCounter()
ptl counter()    ## 1
ptl counter()    ## 2
ptl counter()    ## 3
```

Each call to `counter()` increments the same `c` that was created inside
`makeCounter`. This is a **closure** — `inc` closed over the variable `c`.

---

## 12. Lists — keeping many values together

A **list** is an ordered collection of values. Instead of having
100 separate variables for 100 numbers, you have one list.

### Creating a list

```
L numbers = [1, 2, 3, 4, 5]
L names   = ["Alice", "Bob", "Charlie"]
L mixed   = [1, "hello", T, 3.14]    ## different types are allowed
L empty   = []                         ## empty list
```

### Accessing elements by index

Each element has an **index** (position number) starting from **0**:

```
L fruits = ["apple", "banana", "cherry"]
##           index 0   index 1   index 2

ptl fruits[0]    ## apple
ptl fruits[1]    ## banana
ptl fruits[2]    ## cherry
```

**Important:** the first item is at index **0**, not 1.

### Changing an element

```
L fruits = ["apple", "banana", "cherry"]
fruits[1] = "mango"
ptl fruits    ## [apple, mango, cherry]
```

### Slices — extracting a portion of a list

A **slice** extracts a range of elements without modifying the original list.
Write `[start:stop]` — the result includes `start` but stops **before** `stop`:

```
L nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

ptl nums[2:5]    ## [2, 3, 4]   — indices 2, 3, 4
ptl nums[:3]     ## [0, 1, 2]   — from the beginning up to index 3
ptl nums[7:]     ## [7, 8, 9]   — from index 7 to the end
```

Either bound can be omitted. A slice always returns a **new** list.

### List length

```
L nums = [10, 20, 30, 40]
ptl len(nums)    ## 4
```

### Adding and removing elements

```
L nums = [1, 2, 3]

push(nums, 99)    ## add 99 to the end →  [1, 2, 3, 99]
ptl nums

L last = pop(nums)   ## remove and return the last element
ptl last    ## 99
ptl nums    ## [1, 2, 3]
```

### Sorting and reversing

```
L nums = [3, 1, 4, 1, 5, 9, 2]

ptl sort(nums)    ## [1, 1, 2, 3, 4, 5, 9]  — sorted copy
ptl rev(nums)     ## [2, 9, 5, 1, 4, 1, 3]  — reversed copy
ptl nums          ## [3, 1, 4, 1, 5, 9, 2]  — original UNCHANGED
```

Note: `sort` and `rev` return a **new** list. The original is not modified.

### Searching

```
L nums = [10, 20, 30, 20, 10]

ptl count(nums, 20)    ## 2  — how many times 20 appears
ptl idx(nums, 30)      ## 2  — index of first occurrence of 30
ptl idx(nums, 99)      ## -1 — not found
```

### Useful math on lists

```
L nums = [5, 3, 8, 1, 9]

ptl sum(nums)    ## 26  — add all numbers
ptl max(nums)    ## 9   — largest
ptl min(nums)    ## 1   — smallest
```

### Remove duplicates

```
L nums = [1, 2, 2, 3, 3, 3, 4]
ptl uniq(nums)    ## [1, 2, 3, 4]
```

### Higher-order functions — map, flt2, red

These are powerful tools for working with lists without writing explicit loops.

#### `map` — transform every element

`map(list, function)` applies a function to every element and returns a new list:

```
L nums    = [1, 2, 3, 4, 5]
L doubled = map(nums, fn(x) { rt x * 2 })
ptl doubled    ## [2, 4, 6, 8, 10]
```

#### `flt2` — keep only matching elements

`flt2(list, function)` keeps only elements where the function returns `T`:

```
L nums  = [1, 2, 3, 4, 5, 6]
L evens = flt2(nums, fn(x) { rt x % 2 == 0 })
ptl evens    ## [2, 4, 6]
```

#### `red` — combine all elements into one value

`red(list, function, starting_value)` applies the function repeatedly,
accumulating a single result. "red" is short for "reduce":

```
L nums  = [1, 2, 3, 4, 5]
L total = red(nums, fn(a, b) { rt a + b }, 0)
ptl total    ## 15  (0+1+2+3+4+5)
```

What happens step by step:
```
start: 0
0 + 1 = 1
1 + 2 = 3
3 + 3 = 6
6 + 4 = 10
10 + 5 = 15  ← final result
```

#### `zip2` — pair up two lists

```
L names  = ["Alice", "Bob", "Charlie"]
L scores = [95, 87, 92]

L paired = zip2(names, scores)
ptl paired    ## [[Alice, 95], [Bob, 87], [Charlie, 92]]
```

#### `flat` — flatten a nested list

```
L nested = [[1, 2], [3, 4], [5, 6]]
ptl flat(nested)    ## [1, 2, 3, 4, 5, 6]
```

---

## 13. Dictionaries — labelled boxes

A **dictionary** (or "dict") stores values with **named labels** called **keys**,
instead of numbered positions like a list.

Think of it like a real dictionary: you look up a word (key) to find its
definition (value).

### Creating a dictionary

```
L person = {"name": "Alice", "age": 25, "city": "London"}
```

Each entry is a `key: value` pair separated by commas.
Keys are usually strings. Values can be anything.

### Reading values

```
ptl person["name"]    ## Alice
ptl person["age"]     ## 25
```

### Changing values

```
person["age"] = 26
ptl person["age"]    ## 26
```

### Adding new entries

```
L config = {"theme": "dark"}
config["language"] = "english"
config["font_size"] = 14
ptl config    ## {theme: dark, language: english, font_size: 14}
```

### Dict methods — operations you can call directly on a dictionary

Dictionaries have methods you can call with the dot `.` syntax,
making common operations more natural.

**Iterating over a dictionary:**

```
L prices = {"apple": 1.2, "banana": 0.5, "cherry": 2.0}

lp pair in prices.items() {
    ptl f"{pair[0]}: £{pair[1]}"
}
```

Output:
```
apple: £1.2
banana: £0.5
cherry: £2.0
```

**Getting all keys or all values:**

```
ptl prices.keys()      ## [apple, banana, cherry]
ptl prices.values()    ## [1.2, 0.5, 2.0]
```

**Safe lookup with a default:**

```
L price = prices.get("mango", 0.0)
ptl price    ## 0.0 — "mango" wasn't in the dict, so the default was returned
```

Without `.get()`, accessing a missing key crashes. With `.get()` you can
safely provide a fallback value.

**Checking, deleting, and merging:**

```
ptl prices.has("apple")         ## T — does the key exist?
prices.del("banana")            ## remove a key
L updated = prices.merge({"grape": 1.8})  ## combine two dicts into a new one
```

### Unpacking a dictionary into variables

You can pull dictionary values into named variables using `L {key, key} = dict`:

```
L user = {"name": "Alice", "score": 99, "level": 7}
L {name, score, level} = user

ptl f"{name} is level {level} with {score} points."
```

This is exactly equivalent to writing `L name = user["name"]` etc., but in one line.
The variable names must match the dictionary keys exactly.

### A practical example

```
L scores = {"Alice": 95, "Bob": 87, "Charlie": 92}

ptl scores["Alice"]    ## 95

scores["Diana"] = 88
ptl scores["Diana"]    ## 88

## Print everyone in order
lp pair in scores.items() {
    ptl f"{pair[0]}: {pair[1]}"
}
```

### Dictionaries with lists as values

```
L student = {
    "name": "Alice",
    "grades": [90, 85, 92, 88]
}

ptl student["name"]        ## Alice
ptl student["grades"]      ## [90, 85, 92, 88]
ptl student["grades"][0]   ## 90  — first grade
```

---

## 14. Error handling — `try` / `catch`

Some operations can fail at runtime — converting bad input, dividing by zero,
accessing a variable that doesn't exist. Without error handling, any of these
crashes the whole program. `try/catch` lets you handle the failure gracefully.

### Basic syntax

```
try {
    L n = int("hello")    ## this will fail
    ptl f"Got: {n}"
} catch e {
    ptl f"Something went wrong: {e}"
}
```

The code inside `try { }` runs normally. If **any** error occurs, execution
jumps immediately to `catch`, and the variable after `catch` (here `e`) is
set to the error message as a string. Code after the failing line inside `try`
is skipped.

### Practical use — validating user input without crashing

```
inp "Enter a number: " raw

try {
    L n = int(raw)
    ptl f"Doubled: {n * 2}"
} catch e {
    ptl "That was not a valid number."
}
```

### Catching specific failure types

You can put any code inside `try` — the `catch` block handles whatever goes wrong:

```
L caught_div = "no"
try {
    ptl 1 / 0
} catch e {
    caught_div = "yes"
}
ptl caught_div    ## "yes"

L caught_missing = "no"
try {
    ptl undeclaredVariable
} catch e {
    caught_missing = "yes"
}
ptl caught_missing    ## "yes"
```

### What `try/catch` does NOT catch

`try/catch` only catches genuine runtime errors. The control-flow keywords
`rt` (return), `brk` (break), and `cnt` (continue) are not errors —
they pass through `try` blocks completely unaffected:

```
fn example() {
    try {
        rt 42    ## this works fine — rt passes through
    } catch e {
        ptl "never reaches here"
    }
}
ptl example()    ## 42
```

### Throwing errors yourself — `throw`

`throw` lets you signal an error from your own code. You can throw any value —
a string, a number, or a struct instance:

```
fn divide(a, b) {
    if b == 0 {
        throw "cannot divide by zero"
    }
    rt a / b
}

try {
    ptl divide(10, 0)
} catch e {
    ptl f"Error: {e}"    ## Error: cannot divide by zero
}
```

The real power of `throw` is **typed errors** — throw a struct instance so
the handler can inspect it properly:

```
struct ValueError {
    fn init(msg) {
        self.msg  = msg
        self.code = 400
    }
    fn str() { rt f"ValueError: {self.msg}" }
}

struct NotFoundError {
    fn init(resource) {
        self.resource = resource
        self.code = 404
    }
}

fn findUser(users, id) {
    lp user in users {
        if user.id == id { rt user }
    }
    throw NotFoundError(id)
}

try {
    findUser([], 42)
} catch e {
    if instanceof(e, NotFoundError) {
        ptl f"User {e.resource} not found."
    } el {
        ptl f"Unexpected error: {e}"
    }
}
```

This gives you the same kind of structured error handling you'd find in
Python or JavaScript. Throw errors for conditions that should not be silently
ignored; use `try/catch` to handle them in the right place.

`throw` can also be used outside a `try` block — the error will propagate up
the call stack until something catches it, or the program stops with an error.

---

## 15. Structs — grouping data and behaviour together

Until now, data and functions have been separate — you have variables holding
values, and standalone functions that process them. **Structs** let you bundle
both into a single named type. A struct defines what data an object holds
and what operations it can perform.

This is the foundation of **object-oriented programming** (OOP): instead of
asking "what data do I have and what functions manipulate it?", you ask
"what kind of *thing* is this, and what can it *do*?"

### Defining a struct

Use the `struct` keyword, followed by the name and a block of method definitions.
A method is just a function defined inside the struct:

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
```

There are two things to notice:
- `init` is the **constructor** — it runs automatically whenever you create a new Dog.
- `self` refers to **this specific instance** of the struct. `self.name` stores the name
  on the object itself, so each Dog can have its own name.

### Creating an instance

To create a Dog, call the struct name like a function:

```
L d = Dog("Rex", 3)
```

This calls `init` with `name = "Rex"` and `age = 3`. The result is stored in `d`.

Note that `self` is **not** in the parameter list — it is injected automatically.
You never pass `self` when calling a method.

### Accessing attributes

Read any value that was stored with `self.something`:

```
ptl d.name    ## Rex
ptl d.age     ## 3
```

### Calling methods

Call a method on an instance using the dot `.` syntax:

```
d.bark()    ## Woof! I am Rex.
```

### Changing attributes

You can change an attribute from outside the struct:

```
d.name = "Max"
ptl d.name    ## Max
```

Or from inside a method using `self`:

```
struct Counter {
    fn init(start) {
        self.val = start
    }
    fn inc() {
        self.val += 1
    }
    fn get() {
        rt self.val
    }
}

L c = Counter(0)
c.inc()
c.inc()
c.inc()
ptl c.get()    ## 3
```

Compound assignment (`+=`, `-=`, `*=`, etc.) works on `self` attributes too,
as shown above with `self.val += 1`.

### Methods with parameters and return values

Methods work exactly like regular functions — they can take arguments and
return values with `rt`:

```
struct Rectangle {
    fn init(width, height) {
        self.width  = width
        self.height = height
    }

    fn area() {
        rt self.width * self.height
    }

    fn scale(factor) {
        self.width  *= factor
        self.height *= factor
    }

    fn describe() {
        rt f"Rectangle({self.width} x {self.height})"
    }
}

L r = Rectangle(4, 5)
ptl r.area()        ## 20
r.scale(2)
ptl r.describe()    ## Rectangle(8 x 10)
```

### The `str` method — custom display

If you define a method called `str`, it is used whenever the instance is
converted to text — including inside f-strings and when you call `str(obj)`:

```
struct Point {
    fn init(x, y) {
        self.x = x
        self.y = y
    }
    fn str() {
        rt f"Point({self.x}, {self.y})"
    }
}

L p = Point(3, 4)
ptl str(p)           ## Point(3, 4)
ptl f"Location: {str(p)}"   ## Location: Point(3, 4)
```

### Checking the type of an object

Three built-in functions let you inspect instances:

```
L d = Dog("Rex", 3)

ptl isObj(d)              ## T — is it a struct instance?
ptl className(d)          ## "Dog" — what struct was it made from?
ptl instanceof(d, Dog)    ## T — is it specifically a Dog?
```

`instanceof` returns `F` if you check against a different struct:

```
struct Cat {
    fn init(name) { self.name = name }
}

L c = Cat("Whiskers")
ptl instanceof(c, Dog)    ## F — c is a Cat, not a Dog
ptl instanceof(c, Cat)    ## T
```

### Structs as values — using instances in lists and with functions

Instances are regular values. You can store them in lists, pass them to
functions, use them with `map` and `flt2`:

```
struct Item {
    fn init(name, price) {
        self.name  = name
        self.price = price
    }
}

L cart = [Item("apple", 1), Item("banana", 2), Item("cherry", 5)]

## Loop over all items
lp item in cart {
    ptl f"{item.name}: £{item.price}"
}

## Total price
L total = red(cart, fn(acc, item) { rt acc + item.price }, 0)
ptl f"Total: £{total}"    ## Total: £8

## Only cheap items
L cheap = flt2(cart, fn(item) { rt item.price < 3 })
ptl len(cheap)    ## 2
```

### Nil-safe access on instances

The `?.` operator works on struct instances too:

```
L d = Dog("Rex", 3)
L maybe = nil

ptl d?.name      ## Rex
ptl maybe?.name  ## nil — no crash
```

### A complete example

```
struct BankAccount {
    fn init(owner, balance) {
        self.owner   = owner
        self.balance = balance
    }

    fn deposit(amount) {
        self.balance += amount
        ptl f"Deposited £{amount}. New balance: £{self.balance}"
    }

    fn withdraw(amount) {
        if amount > self.balance {
            ptl "Insufficient funds."
            rt F
        }
        self.balance -= amount
        ptl f"Withdrew £{amount}. New balance: £{self.balance}"
        rt T
    }

    fn str() {
        rt f"Account({self.owner}, £{self.balance})"
    }
}

L acc = BankAccount("Alice", 500)
acc.deposit(200)      ## Deposited £200. New balance: £700
acc.withdraw(100)     ## Withdrew £100. New balance: £600
acc.withdraw(1000)    ## Insufficient funds.
ptl str(acc)          ## Account(Alice, £600)
```

### Inheritance — building on existing structs

When several structs share common behaviour, you can put the shared parts in
a **parent struct** and have the others **extend** it. The child inherits all
of the parent's methods automatically.

```
struct Animal {
    fn init(name) {
        self.name = name
    }
    fn describe() {
        ptl f"I am {self.name}."
    }
    fn speak() {
        ptl "..."
    }
}

struct Dog extends Animal {
    fn init(name, breed) {
        super.init(name)    ## call the parent's init
        self.breed = breed
    }
    fn speak() {            ## override the parent's speak
        ptl f"Woof! I am {self.name}."
    }
}

L d = Dog("Rex", "Labrador")
d.speak()       ## Woof! I am Rex.
d.describe()    ## I am Rex.  ← inherited from Animal, no need to rewrite
ptl d.breed     ## Labrador
```

The `Dog` struct does not define `describe` — it is found on `Animal` and
called automatically. Only `speak` is overridden with a Dog-specific version.

#### `super` — calling the parent's version

Inside a child method, `super.method(args)` calls the same-named method from
the parent struct. This is most commonly used in `init` to let the parent set
up its attributes before the child adds its own:

```
struct Vehicle {
    fn init(make, year) {
        self.make = make
        self.year = year
    }
    fn info() {
        rt f"{self.year} {self.make}"
    }
}

struct Car extends Vehicle {
    fn init(make, year, doors) {
        super.init(make, year)    ## Vehicle sets self.make and self.year
        self.doors = doors        ## Car adds self.doors
    }
    fn info() {
        rt f"{super.info()}, {self.doors} doors"   ## extend parent's output
    }
}

L c = Car("Toyota", 2023, 4)
ptl c.info()    ## 2023 Toyota, 4 doors
```

You can chain as many levels as you like. Each struct only needs to describe
what is **different** about it.

#### `instanceof` checks the full chain

When you use inheritance, `instanceof` checks not just the direct type but
every ancestor:

```
L d = Dog("Rex", "Lab")

ptl instanceof(d, Dog)      ## T — directly
ptl instanceof(d, Animal)   ## T — Dog extends Animal
ptl className(d)            ## "Dog" — always the concrete type
```

This is useful when a function should accept any Animal, regardless of which
specific kind it is:

```
fn makeSpeak(animal) {
    if instanceof(animal, Animal) {
        animal.speak()
    } el {
        ptl "not an animal"
    }
}

makeSpeak(Dog("Rex", "Lab"))     ## Woof! I am Rex.
makeSpeak(Animal("Thing"))       ## ...
```

---

## 16. Modules — splitting code across files

MinLang has two ways to load code from another file: `use` (simple, shared
scope) and `import as` (isolated, namespaced). Both let you split a large
project across multiple files.

### `use` — run a file in the current scope

`use` executes another `.minl` file and makes everything it defines available
directly in the calling program, as if you had written the code inline.

**utils.minl:**
```
fn clamp(x, lo, hi) {
    rt x < lo ? lo : (x > hi ? hi : x)
}

fn lerp(a, b, t) {
    rt a + (b - a) * t
}
```

**main.minl:**
```
use "utils.minl"

ptl clamp(150, 0, 100)     ## 100
ptl lerp(0, 100, 0.25)     ## 25
```

All functions and variables defined in the file become available immediately
after the `use` line. There is no separation — every name from the file lands
directly in your scope.

### `import as` — isolated namespace

`import "file.minl" as name` runs the file in its own isolated environment
and binds the result to an alias. Names from the module do **not** appear
in your scope — you access them through the alias with dot notation.

**math_utils.minl:**
```
fn square(x) { rt x * x }
fn cube(x)   { rt x * x * x }
L PI = 3.14159

export square
export cube
export PI
```

**main.minl:**
```
import "math_utils.minl" as math

ptl math.square(5)   ## 25
ptl math.cube(3)     ## 27
ptl math.PI          ## 3.14159
```

The alias `math` is just a regular variable — you can pass it around, store
it in a list, or use it in an f-string.

### `export` — controlling what a module exposes

Inside a module file, `export name` marks a specific name for export. Only
exported names are accessible through the alias.

```
## geometry.minl
fn circleArea(r) { rt pi * r * r }
fn _helper(x) { rt x * 2 }   ## internal — not exported

L VERSION = "2.0"

export circleArea
export VERSION
## _helper is NOT exported
```

If you write **no** `export` statements at all, every top-level name in the
module is exported automatically. This is convenient for small utility files
where everything is meant to be public.

`export` only works inside module files. When you run a `.minl` file directly
(not through `import`), `export` statements are silently ignored — this means
you can lint or test module files standalone without errors.

### Choosing between `use` and `import as`

| | `use "file"` | `import "file" as name` |
|---|---|---|
| Names land in | current scope | alias only |
| Risk of name clash | yes | no |
| Access syntax | direct: `myFn()` | via alias: `mod.myFn()` |
| Supports `export` | no | yes |

Use `use` for small helper files where you want its functions to feel like
built-ins. Use `import as` for larger modules where you want clean separation
and no chance of names colliding with your own code.

### Why split into files?

- Code stays shorter and easier to read
- You can reuse the same utilities in multiple programs
- Working on one part of the code doesn't require scrolling past unrelated code

### Things to know

- File paths are relative to where you run the interpreter from
- Structs, functions, and variables all carry across with both `use` and `import as`
- You can use as many `use` and `import` statements as you need

---

## 17. Built-in tools — the standard library

MinLang comes with many ready-made functions.
This section explains each group with examples.

### Time and dates

```
ptl now()       ## 1741686000.123  — seconds since Jan 1 1970 (unix timestamp)
                ##   (useful for timing how long something takes)

ptl clock()     ## "14:32:05"      — current time as text
ptl date()      ## "2026-03-11"    — current date as text

ptl clock("%H:%M")       ## "14:32"       — custom time format
ptl date("%d/%m/%Y")     ## "11/03/2026"  — custom date format

sleep(2)        ## pause the program for 2 seconds
sleep(0.5)      ## pause for half a second
```

Format codes for `clock()` and `date()`:

| Code | Meaning | Example |
|---|---|---|
| `%H` | Hour (24h) | `14` |
| `%M` | Minute | `32` |
| `%S` | Second | `05` |
| `%d` | Day | `11` |
| `%m` | Month number | `03` |
| `%Y` | Full year | `2026` |

### Random numbers

```
ptl rand()            ## 0.6273...  — random float between 0.0 and 1.0

ptl randInt(1, 6)     ## 4          — random integer from 1 to 6 (like a dice roll)
ptl randInt(1, 100)   ## 73         — random integer from 1 to 100

L colours = ["red", "green", "blue"]
ptl pick(colours)     ## "green"    — pick a random item from a list

L deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
shuffle(deck)
ptl deck              ## [7, 3, 10, 1, ...]  — shuffled in place
```

### Type checking — asking "what kind of value is this?"

```
L x = 42

ptl isInt(x)     ## T   — is it a whole number?
ptl isFlt(x)     ## F   — is it a decimal number?
ptl isStr(x)     ## F   — is it text?
ptl isLst(x)     ## F   — is it a list?
ptl isDct(x)     ## F   — is it a dict?
ptl isBool(x)    ## F   — is it T or F?
ptl isNil(x)     ## F   — is it nil?
ptl isObj(x)     ## F   — is it a struct instance?

ptl type(x)      ## "int"   — returns the type name as text
```

Useful when you don't know what type of value you're working with:

```
fn describe(val) {
    if isInt(val) || isFlt(val) {
        ptl f"{val} is a number"
    } elif isStr(val) {
        ptl f"{val} is text"
    } elif isLst(val) {
        ptl f"a list with {len(val)} items"
    } elif isObj(val) {
        ptl f"a {className(val)} instance"
    } el {
        ptl f"something else: {type(val)}"
    }
}
```

### File reading and writing

```
## Read an entire file into a string
L content = read("notes.txt")
ptl content

## Write text to a file (creates it if it doesn't exist, overwrites if it does)
write("output.txt", "Hello from MinLang!")

## Append to a file (adds to the end without overwriting)
append("log.txt", "\nNew line added")

## Check if a file exists before reading
if exists("config.txt") {
    L cfg = read("config.txt")
}
```

### System functions

```
## Get command-line arguments (values typed after the filename when running)
## Example: python3 minlang.py program.minl Alice 30
L args = sysArgs()
## args = ["Alice", "30"]

## Read environment variables
L home = sysEnv("HOME")    ## e.g. "/home/alice"

## Exit the program immediately
exit(0)     ## 0 means "success"
exit(1)     ## any non-zero number means "something went wrong"
```

---

## 18. Putting it all together — full projects

Now let's combine everything into real programs.

### Project 1 — Number guessing game

```
## The computer picks a random number, the player guesses it.

L secret   = randInt(1, 100)
L attempts = 0

ptl "I am thinking of a number between 1 and 100."

wh T {
    inp "Your guess: " raw

    if !canInt(raw) {
        ptl "Please enter a whole number."
        cnt
    }

    L guess = int(raw)
    attempts += 1

    if guess < secret {
        ptl "Too low! Try higher."
    } elif guess > secret {
        ptl "Too high! Try lower."
    } el {
        ptl f"Correct! You got it in {attempts} attempts."
        brk
    }
}
```

### Project 2 — To-do list

```
## A simple to-do list that keeps running until you quit.

L todos = []

ptl "=== To-Do List ==="
ptl "Commands: add / done / list / quit"

wh T {
    inp "> " command

    if command == "quit" {
        ptl "Goodbye!"
        brk

    } elif command == "add" {
        inp "New task: " task
        push(todos, task)
        ptl f"Added: {task}"

    } elif command == "list" {
        if len(todos) == 0 {
            ptl "No tasks yet."
        } el {
            lp i in rng(len(todos)) {
                ptl f"  {i + 1}. {todos[i]}"
            }
        }

    } elif command == "done" {
        inp "Task number to remove: " raw
        if canInt(raw) {
            L num = int(raw) - 1
            if num >= 0 && num < len(todos) {
                L removed = todos[num]
                todos[num] = nil
                L clean = flt2(todos, fn(x) { rt x != nil })
                todos = clean
                ptl f"Removed: {removed}"
            } el {
                ptl "Invalid task number."
            }
        } el {
            ptl "Please enter a number."
        }

    } el {
        ptl "Unknown command. Try: add / done / list / quit"
    }
}
```

### Project 3 — Simple statistics

```
## Read a list of numbers from the user and compute statistics.

L numbers = []

ptl "Enter numbers one by one. Type 'done' when finished."

wh T {
    inp "> " raw
    if raw == "done" { brk }

    if canFlt(raw) {
        push(numbers, flt(raw))
    } el {
        ptl "Not a number, skipping."
    }
}

if len(numbers) == 0 {
    ptl "No numbers entered."
} el {
    L total   = sum(numbers)
    L average = total / len(numbers)
    L sorted  = sort(numbers)

    ptl f"Count:   {len(numbers)}"
    ptl f"Sum:     {total}"
    ptl f"Average: {rnd(average, 2)}"
    ptl f"Min:     {min(numbers)}"
    ptl f"Max:     {max(numbers)}"
    ptl f"Sorted:  {sorted}"
}
```

### Project 4 — Caesar cipher (encode a message)

```
## Shift every letter in the message by a fixed number of positions.
## "hello" with shift 3 → "khoor"

fn shiftChar(ch, shift) {
    L alphabet = "abcdefghijklmnopqrstuvwxyz"
    L pos = find(alphabet, ch)
    if pos == -1 {
        rt ch    ## not a letter — return unchanged
    }
    L newPos = (pos + shift) % 26
    rt sub(alphabet, newPos, newPos + 1)
}

fn encode(message, shift) {
    L result = ""
    L lower  = lo(message)
    lp i in rng(len(lower)) {
        L ch = sub(lower, i, i + 1)
        result = result + shiftChar(ch, shift)
    }
    rt result
}

inp "Message to encode: " msg
inp "Shift amount (1-25): " raw_shift
L shift = int(raw_shift)

L encoded = encode(msg, shift)
L decoded = encode(encoded, 26 - shift)

ptl f"Encoded: {encoded}"
ptl f"Decoded: {decoded}"
```

### Project 5 — Contact book (using structs)

```
## A contact book where each contact is a struct instance.

struct Contact {
    fn init(name, phone, email) {
        self.name  = name
        self.phone = phone
        self.email = email
    }

    fn display() {
        ptl f"  Name:  {self.name}"
        ptl f"  Phone: {self.phone}"
        ptl f"  Email: {self.email}"
    }

    fn str() {
        rt self.name
    }
}

L contacts = []

ptl "=== Contact Book ==="
ptl "Commands: add / find / list / quit"

wh T {
    inp "> " command

    if command == "quit" {
        ptl "Goodbye!"
        brk

    } elif command == "add" {
        inp "Name:  " cname
        inp "Phone: " cphone
        inp "Email: " cemail
        push(contacts, Contact(cname, cphone, cemail))
        ptl f"Saved {cname}."

    } elif command == "list" {
        if len(contacts) == 0 {
            ptl "No contacts yet."
        } el {
            lp c in contacts {
                c.display()
                ptl "  ─────────"
            }
        }

    } elif command == "find" {
        inp "Search name: " query
        L found = flt2(contacts, fn(c) { rt c.name.lo().has(lo(query)) })
        if len(found) == 0 {
            ptl "No matches."
        } el {
            lp c in found { c.display() }
        }

    } el {
        ptl "Unknown command."
    }
}
```

---

## 19. Quick Reference Card

```
## ── VARIABLES ────────────────────────────────
L x = 5             ## declare
x = 10              ## reassign
x += 1              ## compound assign  (also -=  *=  /=  %=)
L [a, b] = lst      ## list unpack
L [a, *rest] = lst  ## list unpack with rest
L {x, y} = dct      ## dict unpack

## ── OUTPUT ───────────────────────────────────
ptl "text"          ## print with newline
pt  "text"          ## print without newline
ptl f"x = {x}"      ## f-string
L s = """
line one
line two"""         ## multiline string

## ── INPUT ────────────────────────────────────
inp x               ## read into x
inp "Prompt: " x    ## read with prompt

## ── CONDITIONS ───────────────────────────────
if x > 5 {
} elif x == 5 {
} el {
}
cond ? a : b        ## ternary expression

## ── LOOPS ────────────────────────────────────
lp i in rng(10) { }     ## for loop
wh condition { }         ## while loop
brk                      ## break
cnt                      ## continue

## ── FUNCTIONS ────────────────────────────────
fn name(a, b) {
    rt a + b
}
fn name(*args) { }       ## variadic — args is a list
fn(x) { rt x * 2 }       ## anonymous function (lambda)

## ── STRUCTS ───────────────────────────────────
struct Animal {
    fn init(name) { self.name = name }
    fn speak()    { rt "..." }
}
struct Dog extends Animal {      ## inheritance
    fn init(name, breed) {
        super.init(name)         ## call parent init
        self.breed = breed
    }
    fn speak() { rt f"Woof, {self.name}!" }
    fn str()   { rt f"Dog({self.name})" }
}
L d = Dog("Rex", "Lab")  ## create instance
d.speak()                ## call method
ptl d.name               ## read attribute
d.name = "Max"           ## write attribute  (outside)
## self.x += 1           ## compound assign  (inside method)
isObj(d)                 ## T
className(d)             ## "Dog"
instanceof(d, Dog)       ## T
instanceof(d, Animal)    ## T  (walks inheritance chain)

## ── ERROR HANDLING ───────────────────────────
try {
    risky()
} catch e {
    ptl e
}
throw "something went wrong"   ## throw a string
throw MyError("bad input")     ## throw a struct instance

## ── MODULES ──────────────────────────────────
use "utils.minl"               ## run file in current scope
import "utils.minl" as utils   ## isolated namespace
utils.myFunc()                 ## call via alias
utils.myVar                    ## read variable via alias
## inside a module file:
export myFunc                  ## mark name for export

## ── TYPES ────────────────────────────────────
T  F  nil             ## true, false, null
[1, 2, 3]             ## list
{"key": "value"}      ## dict

## ── OPERATORS ────────────────────────────────
+ - * / %             ## arithmetic
//                    ## integer division  (17 // 5 → 3)
**                    ## power (right-associative)
== != < > <= >=       ## comparison
&&  ||  !             ## logical
&  |  ^  ~  <<  >>    ## bitwise

## ── SLICES ───────────────────────────────────
lst[2:5]   lst[:3]   lst[7:]   ## lists
str[1:4]   str[:3]   str[2:]   ## strings

## ── NIL-SAFE ACCESS ──────────────────────────
obj?.method()         ## nil if obj is nil
obj?.attr             ## nil if obj is nil

## ── MATH ─────────────────────────────────────
+ - * / % // **  pow(a,b)  sqrt(x)  abs(x)
floor(x)  ceil(x)  rnd(x, 2)  max(a,b)  min(a,b)
log(x)  sin(x)  cos(x)  tan(x)
fmt(x, ".2f")         ## format number to string

## ── STRINGS ──────────────────────────────────
len(s)  up(s)  lo(s)  trim(s)
split(s, ",")  join(lst, "-")
find(s, sub)  contains(s, sub)
replace(s, old, new)  sub(s, start, end)
startsWith(s, x)  endsWith(s, x)

## ── LISTS ────────────────────────────────────
len(lst)  push(lst, x)  pop(lst)
sort(lst)  rev(lst)  sum(lst)
count(lst, x)  idx(lst, x)  uniq(lst)
flat(lst)  zip2(a, b)  slice(lst, a, b)
map(lst, fn)  flt2(lst, fn)  red(lst, fn, start)

## ── DICTS ────────────────────────────────────
d["key"]  d["key"] = val
d.keys()  d.values()  d.items()
d.get("key", default)
d.has("key")  d.del("key")  d.merge(other)
keys(d)  values(d)  items(d)  hasKey(d, k)

## ── TYPE CHECKS ──────────────────────────────
isInt  isFlt  isStr  isLst  isDct  isBool  isNil
isObj  instanceof(obj, Cls)  className(obj)
canInt  canFlt  toInt  toFlt  int  flt  str  type

## ── TIME ─────────────────────────────────────
now()  clock()  date()  sleep(s)

## ── RANDOM ───────────────────────────────────
rand()  randInt(a, b)  pick(lst)  shuffle(lst)

## ── FILES ────────────────────────────────────
read("file.txt")
write("file.txt", "content")
append("file.txt", "more content")
exists("file.txt")

## ── SYSTEM ───────────────────────────────────
sysArgs()  sysEnv("VAR")  exit(0)
```