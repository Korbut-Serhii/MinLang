## ══════════════════════════════════════════
##  MinLang  —  examples.ll
##  A tour of every language feature.
##  Run with:  python3 minlang.py examples.ll
## ══════════════════════════════════════════


## ── 1. Variables ────────────────────────────────────────────────
## L declares a new variable. After that, just use the name to reassign.

L name = "MinLang"
L ver  = 1
L pi2  = 3.14
L flag = T          ## T = true,  F = false
L nothing = nil     ## nil = null / None

ptl f"Welcome to {name} v{ver}!"


## ── 2. F-strings ────────────────────────────────────────────────
## Put any expression inside {} — it gets evaluated and inserted.

L a = 10
L b = 3
ptl f"{a} + {b} = {a + b}"
ptl f"{a} * {b} = {a * b}"


## ── 3. Conditions ────────────────────────────────────────────────
## if / elif / el  — no parentheses needed around the condition,
## but the body MUST be inside { }.

L x = 42
if x > 100 {
    ptl "over 100"
} elif x > 10 {
    ptl f"{x} is between 10 and 100"
} el {
    ptl "10 or below"
}

## Logical operators:  && = and,  || = or,  ! = not
if x > 0 && x < 100 {
    ptl "x is positive and below 100"
}


## ── 4. For loop  (lp ... in ...) ─────────────────────────────────
## rng(n)       → 0, 1, 2 … n-1
## rng(a, b)    → a, a+1 … b-1
## rng(a, b, s) → a, a+s, a+2s … (step s)

L total = 0
lp i in rng(1, 6) {
    total = total + i
}
ptl f"Sum 1-5 = {total}"

## Iterate directly over a list
lp fruit in ["apple", "banana", "cherry"] {
    ptl f"  - {fruit}"
}


## ── 5. While loop  (wh) ──────────────────────────────────────────
## brk = break,  cnt = continue

L n = 0
wh T {                  ## T means infinite loop
    n = n + 1
    if n == 3 { cnt }   ## skip printing 3
    if n > 5  { brk }   ## exit at 6
    ptl f"n = {n}"
}


## ── 6. Functions  (fn … rt) ──────────────────────────────────────
## rt = return.  Functions are first-class values.

fn greet(who) {
    rt f"Hello, {who}!"
}
ptl greet("world")

## Recursive function
fn fact(n) {
    if n <= 1 { rt 1 }
    rt n * fact(n - 1)
}
ptl f"10! = {fact(10)}"

## Multiple parameters
fn clamp(val, lo, hi) {
    if val < lo { rt lo }
    if val > hi { rt hi }
    rt val
}
ptl f"clamp(150, 0, 100) = {clamp(150, 0, 100)}"


## ── 7. Lists ──────────────────────────────────────────────────────

L nums = [5, 3, 8, 1, 9, 2]

ptl f"original : {nums}"
ptl f"sorted   : {sort(nums)}"
ptl f"reversed : {rev(nums)}"
ptl f"length   : {len(nums)}"
ptl f"sum      : {sum(nums)}"
ptl f"max      : {max(nums)}"
ptl f"min      : {min(nums)}"

## Mutate: push / pop / index assignment
push(nums, 42)
ptl f"after push(42) : {nums}"
L removed = pop(nums)
ptl f"popped: {removed},  list: {nums}"

nums[0] = 99
ptl f"after nums[0]=99 : {nums}"


## ── 8. Dicts ──────────────────────────────────────────────────────

L user = {"name": "Alex", "age": 25, "active": T}
L uname = user["name"]
L uage  = user["age"]
ptl f"User: {uname}, age {uage}"

user["age"] = 26
user["age"] = 26
L newAge = user["age"]
ptl f"Birthday! Now {newAge}"


## ── 9. Strings ───────────────────────────────────────────────────

L s = "  Hello, World!  "
ptl trim(s)                         ## "Hello, World!"
ptl up("minlang")                   ## "MINLANG"
ptl lo("MINLANG")                   ## "minlang"
ptl split("a,b,c", ",")            ## [a, b, c]
ptl join(["x", "y", "z"], "-")     ## x-y-z
ptl contains("hello world", "world")  ## T
ptl replace("foo bar", "bar", "baz")  ## foo baz
ptl sub("hello", 1, 3)             ## el  (chars 1 and 2)
ptl find("hello", "ll")            ## 2


## ── 10. Type conversion & checking ───────────────────────────────

ptl canInt("42")        ## T  — safe to convert
ptl canInt("hello")     ## F
ptl toInt("99")         ## 99
ptl toInt("oops")       ## nil  (no crash)
ptl type(3.14)          ## float
ptl isStr("hi")         ## T
ptl isLst([1,2])        ## T


## ── 11. Math ─────────────────────────────────────────────────────

ptl sqrt(144)           ## 12.0
ptl abs(-7)             ## 7
ptl pow(2, 8)           ## 256
ptl floor(3.9)          ## 3
ptl ceil(3.1)           ## 4
ptl rnd(3.14159, 2)     ## 3.14
ptl pi                  ## 3.14159...


## ── 12. Time ─────────────────────────────────────────────────────

ptl clock()             ## e.g. "14:32:05"
ptl date()              ## e.g. "2026-03-11"
ptl date("%d/%m/%Y")    ## e.g. "11/03/2026"
## sleep(0.5)           ## pause 0.5 seconds (uncomment to use)


## ── 13. Random numbers ───────────────────────────────────────────

L dice = randInt(1, 6)
ptl f"Dice roll: {dice}"
ptl f"Random 0-1: {rnd(rand(), 4)}"
L chosen = pick(["rock", "paper", "scissors"])
ptl f"Computer picks: {chosen}"


## ── 14. Higher-order functions ───────────────────────────────────
## Functions can be passed as arguments and returned from functions.

fn double(x)  { rt x * 2 }
fn isEven(x)  { rt x % 2 == 0 }
fn add2(a, b) { rt a + b }

L evens   = flt2([1,2,3,4,5,6], isEven)   ## filter
L doubled = map(evens, double)              ## map
L total2  = red(doubled, add2, 0)           ## reduce (fold)

ptl f"evens:   {evens}"
ptl f"doubled: {doubled}"
ptl f"total:   {total2}"


## ── 15. Closures ─────────────────────────────────────────────────
## A function captures the scope it was defined in.

fn makeCounter(start) {
    L count = start
    fn step() {
        count = count + 1
        rt count
    }
    rt step
}

L counter = makeCounter(0)
ptl counter()   ## 1
ptl counter()   ## 2
ptl counter()   ## 3


ptl ""
ptl "All examples finished!"
