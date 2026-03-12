## ── Калькулятор MinLang ──

fn calc(a, op, b) {
    if op == "+" { rt a + b }
    elif op == "-" { rt a - b }
    elif op == "*" { rt a * b }
    elif op == "/" {
        if b == 0 { rt "Ошибка: деление на 0" }
        rt a / b
    }
    elif op == "%" { rt a % b }
    elif op == "^" { rt pow(a, b) }
    rt "Неизвестная операция"
}

ptl "=== Калькулятор MinLang ==="
ptl "Введите 'q' для выхода"
ptl ""

wh T {
    inp "Первое число: " rawA
    if rawA == "q" { brk }

    if !canFlt(rawA) {
        ptl "Ошибка: введите число"
        cnt
    }

    inp "Операция (+,-,*,/,%,^): " op
    inp "Второе число: " rawB

    if !canFlt(rawB) {
        ptl "Ошибка: введите число"
        cnt
    }

    L a = flt(rawA)
    L b = flt(rawB)
    L res = calc(a, op, b)
    ptl f"= {res}"
    ptl ""
}

ptl "До свидания!"
