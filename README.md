# MinLang — Language Reference

Minimalist programming language. Maximum power, minimum keystrokes.  
Source files use the `.ll` extension.

---

## Installation & Running

### Run a file
```bash
python minlang.py program.ll
```

### Interactive REPL
```bash
python minlang.py
```

### Make the `minlang` command available (Windows)
Create a file called `minlang.bat` and put it in any folder that is already in your PATH
(e.g. `C:\Windows\System32`, or create `C:\tools\` and add it to PATH yourself):
```bat
@echo off
python "C:\full\path\to\minlang.py" %*
```
Now you can just type:
```
minlang program.ll
```

### Build a standalone `.exe` (no Python required on the target machine)
```bash
pip install pyinstaller
pyinstaller --onefile minlang.py
```
The file `dist/minlang.exe` will contain a self-contained interpreter.
Copy it anywhere in your PATH and it works like any native language.

---

## Syntax Quick-Reference

| Code | What it does |
|---|---|
| `## comment` | Everything after `##` is ignored |
| `L x = 5` | Declare a variable |
| `x = 10` | Reassign an existing variable |
| `x[0] = 9` | Mutate a list or dict element |
| `pt "text"` | Print without newline |
| `ptl "text"` | Print with newline |
| `pt f"{x}"` | Interpolated f-string |
| `inp x` | Read line from user into `x` |
| `inp "Prompt: " x` | Read with a prompt |
| `if cond { }` | Condition |
| `elif cond { }` | Else-if branch |
| `el { }` | Else branch |
| `lp i in rng(n) { }` | For loop |
| `wh cond { }` | While loop |
| `brk` | Break out of loop |
| `cnt` | Continue to next iteration |
| `fn f(a,b) { rt a+b }` | Define a function |
| `rt expr` | Return from a function |
| `T` / `F` / `nil` | true / false / null |
| `[1, 2, 3]` | List literal |
| `{"k": "v"}` | Dict literal |

---

## Variables

```
L x   = 42           ## integer
L f   = 3.14         ## float
L s   = "hello"      ## string
L b   = T            ## boolean  (T or F)
L n   = nil          ## null
L lst = [1, 2, 3]    ## list
L dct = {"a": 1}     ## dict
```

`L` declares a brand-new variable in the current scope.  
After that, just use the name to reassign:
```
x = 99
```

---

## Output

```
pt  "no newline"         ## cursor stays on same line
ptl "with newline"       ## moves to next line
ptl f"x = {x}"          ## f-string: {expr} is evaluated and inserted
ptl f"2+2 = {2 + 2}"    ## any expression works inside {}
```

---

## Input

`inp` always stores the result as a **string**.  Convert explicitly for numbers:

```
inp "Enter a number: " raw

## Safe — returns nil if the string isn't a number
L n = toInt(raw)

## Strict — crashes if not a valid integer
L n = int(raw)

## Check first, then convert
if canInt(raw) {
    L n = int(raw)
    ptl f"You entered: {n}"
} el {
    ptl "That is not a number"
}
```

---

## Conditions

```
if x > 100 {
    ptl "big"
} elif x > 10 {
    ptl "medium"
} el {
    ptl "small"
}
```

Operators: `==` `!=` `<` `>` `<=` `>=` `&&` `||` `!`

```
if x > 0 && x < 100 { ptl "in range" }
if !flag { ptl "flag is false" }
if a == 1 || b == 2 { ptl "either" }
```

---

## Loops

### For loop — `lp`
```
lp i in rng(5) { ptl i }          ## 0 1 2 3 4
lp i in rng(1, 6) { ptl i }       ## 1 2 3 4 5
lp i in rng(0, 10, 2) { ptl i }   ## 0 2 4 6 8   (step of 2)
lp item in [10, 20, 30] { ptl item }
```

### While loop — `wh`
```
L x = 0
wh x < 5 {
    ptl x
    x = x + 1
}
```

### Loop control
```
brk   ## exit the loop immediately
cnt   ## skip to the next iteration
```

---

## Functions

```
fn add(a, b) {
    rt a + b        ## rt = return
}

L result = add(3, 4)    ## result = 7
```

Recursion works:
```
fn fact(n) {
    if n <= 1 { rt 1 }
    rt n * fact(n - 1)
}
ptl fact(10)    ## 3628800
```

Functions are first-class — you can pass them around:
```
fn double(x) { rt x * 2 }
L nums = map([1, 2, 3], double)    ## [2, 4, 6]
```

Closures work — inner functions capture their outer scope:
```
fn makeAdder(n) {
    fn add(x) { rt x + n }
    rt add
}
L add5 = makeAdder(5)
ptl add5(10)    ## 15
```

---

## Lists

```
L nums = [3, 1, 4, 1, 5]

nums[0]             ## read element at index 0 → 3
nums[0] = 99        ## write element at index 0
len(nums)           ## number of elements → 5
push(nums, 9)       ## append to end; returns the list
pop(nums)           ## remove and return last element
sort(nums)          ## return a sorted copy (original unchanged)
rev(nums)           ## return a reversed copy
sum(nums)           ## add all numbers
max(nums)           ## largest value
min(nums)           ## smallest value
count(nums, 1)      ## how many times 1 appears
idx(nums, 4)        ## index of value 4, or -1 if missing
uniq(nums)          ## remove duplicates, keep order
flat([[1,2],[3]])   ## flatten one level → [1, 2, 3]
```

Higher-order list functions:
```
fn isEven(x)  { rt x % 2 == 0 }
fn double(x)  { rt x * 2 }
fn add2(a, b) { rt a + b }

map(nums, double)        ## apply double to every element
flt2(nums, isEven)       ## keep only elements where isEven returns T
red(nums, add2, 0)       ## fold left: (((0+n1)+n2)+n3)...
zip2([1,2], ["a","b"])   ## [[1,"a"], [2,"b"]]
```

---

## Dicts

```
L user = {"name": "Alex", "age": 25}

L nm  = user["name"]    ## read
user["age"] = 26         ## write
```

---

## Strings

```
len("hello")                           ## 5
up("hello")                            ## "HELLO"
lo("HELLO")                            ## "hello"
trim("  hi  ")                         ## "hi"
split("a,b,c", ",")                   ## ["a","b","c"]
join(["a","b","c"], "-")              ## "a-b-c"
find("hello world", "world")          ## 6  (index), -1 if absent
sub("hello", 1, 3)                    ## "el"  (slice index 1..2)
rep("ab", 3)                          ## "ababab"
replace("foo bar", "bar", "baz")      ## "foo baz"
contains("hello world", "world")      ## T
startsWith("hello", "he")             ## T
endsWith("hello", "lo")               ## T
```

---

## Math

```
sqrt(16)          ## 4.0
abs(-5)           ## 5
pow(2, 10)        ## 1024
floor(3.9)        ## 3
ceil(3.1)         ## 4
rnd(3.14159, 2)   ## 3.14  (round to 2 decimal places)
max([3,1,4])      ## 4
min([3,1,4])      ## 1
sum([1,2,3])      ## 6
pi                ## 3.141592653589793
inf               ## infinity
```

---

## Time

```
now()              ## seconds since epoch (unix timestamp)
clock()            ## "14:32:05"
date()             ## "2026-03-11"
clock("%H:%M")     ## custom format → "14:32"
date("%d/%m/%Y")   ## "11/03/2026"
sleep(1.5)         ## pause execution for 1.5 seconds
```

---

## Random

```
rand()             ## random float  0.0 – 1.0
randInt(1, 6)      ## random integer 1 – 6 (both ends inclusive)
pick([1,2,3])      ## random element from a list
shuffle(lst)       ## shuffle the list in place, return it
```

---

## Type Checking & Conversion

```
## Check the type
isInt(x)     ## T if integer
isFlt(x)     ## T if float
isStr(x)     ## T if string
isLst(x)     ## T if list
isDct(x)     ## T if dict
isBool(x)    ## T if T or F
isNil(x)     ## T if nil
type(x)      ## returns "int", "float", "str", "list", "dict", "bool", "NoneType"

## Convert (strict — raises an error if it fails)
int("42")    ## 42
flt("3.14")  ## 3.14
str(42)      ## "42"
bool(0)      ## F

## Convert (safe — returns nil on failure)
toInt("42")    ## 42
toInt("oops")  ## nil

## Check before converting (returns T/F, never crashes)
canInt("42")   ## T
canFlt("3.x")  ## F
```

---

## File I/O

```
L text = read("input.txt")         ## read entire file as a string
write("output.txt", "hello!")      ## write (or overwrite) a file
```

---

## Full Example — Calculator

```
fn calculate(a, op, b) {
    if op == "+" { rt a + b }
    elif op == "-" { rt a - b }
    elif op == "*" { rt a * b }
    elif op == "/" {
        if b == 0 { rt "Error: division by zero" }
        rt a / b
    }
    elif op == "^" { rt pow(a, b) }
    rt "Unknown operator"
}

wh T {
    inp "First number: " rawA
    if rawA == "q" { brk }

    if !canFlt(rawA) {
        ptl "Not a number, try again."
        cnt
    }

    inp "Operator (+,-,*,/,^): " op
    inp "Second number: " rawB

    if !canFlt(rawB) {
        ptl "Not a number, try again."
        cnt
    }

    L result = calculate(flt(rawA), op, flt(rawB))
    ptl f"= {result}"
}
```

---

## Cheat Sheet

```
L x = 5           declare variable
x = 10            reassign
ptl "text"        print line
pt  f"{x}"        print inline, f-string
inp ":" x         read input
if c { }          condition
elif c { }        else-if
el { }            else
lp i in rng(n) { }   for loop
wh cond { }       while loop
brk               break
cnt               continue
fn f(a,b) { rt a+b }  function
T / F / nil       true / false / null
[1,2,3]           list
{"k":"v"}         dict
## comment
```
