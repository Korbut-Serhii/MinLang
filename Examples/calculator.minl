## ══════════════════════════════════════════
##  MinLang  —  calculator.ll
##  A fully interactive command-line calculator.
##  Run with:  python3 minlang.py calculator.ll
## ══════════════════════════════════════════


## ── Helper: check if a string represents a valid number ──────────
## inp always gives us a string, so we must validate before converting.

fn isNumber(s) {
    rt canFlt(s)        ## canFlt returns T if the string can become a float
}


## ── Core calculation function ─────────────────────────────────────
## Takes two numbers and an operator string.
## Returns the result, or an error string if something went wrong.

fn calculate(a, op, b) {
    if op == "+" { rt a + b }
    elif op == "-" { rt a - b }
    elif op == "*" { rt a * b }
    elif op == "/" {
        if b == 0 { rt "Error: division by zero" }
        rt a / b
    }
    elif op == "%" {
        if b == 0 { rt "Error: modulo by zero" }
        rt a % b
    }
    elif op == "^" { rt pow(a, b) }
    rt f"Error: unknown operator '{op}'"
}


## ── History list — stores every past result ───────────────────────
L history = []


## ── Main loop ─────────────────────────────────────────────────────

ptl "╔════════════════════════════════╗"
ptl "║   MinLang Calculator v1.0      ║"
ptl "║   Operators: + - * / % ^       ║"
ptl "║   Type 'q' to quit             ║"
ptl "║   Type 'h' to see history      ║"
ptl "╚════════════════════════════════╝"
ptl ""

wh T {

    ## ── Read first number ──────────────────────────────────────
    inp "First number: " rawA

    if rawA == "q" { brk }          ## exit

    if rawA == "h" {                ## show history and loop again
        if len(history) == 0 {
            ptl "No history yet."
        } el {
            ptl "── History ──"
            lp entry in history {
                ptl f"  {entry}"
            }
        }
        cnt                         ## cnt = continue → skip to next iteration
    }

    ## Validate: inp always returns a string, check before converting
    if !isNumber(rawA) {
        ptl f"'{rawA}' is not a valid number. Try again."
        cnt
    }

    ## ── Read operator ──────────────────────────────────────────
    inp "Operator (+,-,*,/,%,^): " op

    ## ── Read second number ─────────────────────────────────────
    inp "Second number: " rawB

    if !isNumber(rawB) {
        ptl f"'{rawB}' is not a valid number. Try again."
        cnt
    }

    ## ── Convert strings to numbers ─────────────────────────────
    ## flt() turns a string like "3.14" into the float 3.14
    L numA = flt(rawA)
    L numB = flt(rawB)

    ## ── Calculate and display ──────────────────────────────────
    L result = calculate(numA, op, numB)

    ## Round nicely: if result is a whole number, show as int
    L display = result
    if isStr(result) {
        ## Error message — just print it
        ptl f"  {result}"
        ptl ""
        cnt
    }

    ## Round to avoid floating-point noise like 0.30000000000000004
    display = rnd(result, 10)

    ptl f"  = {display}"
    ptl ""

    ## Save to history
    L entry = f"{rawA} {op} {rawB} = {display}"
    push(history, entry)
}

## ── Show summary on exit ───────────────────────────────────────────
ptl ""
if len(history) > 0 {
    ptl "── Session history ──"
    lp e in history {
        ptl f"  {e}"
    }
}
ptl "Goodbye!"
