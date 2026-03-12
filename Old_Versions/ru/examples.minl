## MinLang — примеры программ
## Символ ## — это комментарий

## ── 1. Переменные и вывод ──
L name = "MinLang"
L ver = 1
ptl f"Добро пожаловать в {name} v{ver}!"

## ── 2. Условия ──
L x = 42
if x > 100 {
    ptl "Больше 100"
} elif x > 10 {
    ptl f"{x} — между 10 и 100"
} el {
    ptl "Маленькое число"
}

## ── 3. Цикл for ──
L sum = 0
lp i in rng(1, 6) {
    sum = sum + i
}
ptl f"Сумма 1-5 = {sum}"

## ── 4. Цикл while с break ──
L n = 0
wh T {
    n = n + 1
    if n >= 3 { brk }
}
ptl f"Вышли при n={n}"

## ── 5. Функции ──
fn fact(n) {
    if n <= 1 { rt 1 }
    rt n * fact(n - 1)
}
ptl f"10! = {fact(10)}"

fn isPrime(n) {
    if n < 2 { rt F }
    lp i in rng(2, n) {
        if n % i == 0 { rt F }
    }
    rt T
}

## Простые числа до 20
L primes = []
lp i in rng(2, 21) {
    if isPrime(i) { primes = push(primes, i) }
}
ptl f"Простые до 20: {primes}"

## ── 6. Работа со строками ──
L s = "  Hello, World!  "
ptl trim(s)
ptl up("minlang")
ptl split("a,b,c", ",")

## ── 7. Списки и словари ──
L nums = [5, 3, 8, 1, 9, 2]
ptl f"Исходный: {nums}"
ptl f"Сортированный: {sort(nums)}"
ptl f"Макс: {max(nums)}  Мин: {min(nums)}"

L person = {"name": "Алекс", "age": 25}
L pname = person["name"]
L page = person["age"]
ptl f"Имя: {pname}, Возраст: {page}"

## ── 8. Функции высшего порядка ──
fn double(x) { rt x * 2 }
fn isEven(x) { rt x % 2 == 0 }

L result = map([1,2,3,4,5], double)
ptl f"Удвоенные: {result}"

L evens = flt2([1,2,3,4,5,6], isEven)
ptl f"Чётные: {evens}"

## ── 9. Вложенные функции ──
fn makeAdder(n) {
    fn adder(x) { rt x + n }
    rt adder
}
L add5 = makeAdder(5)
ptl f"add5(10) = {add5(10)}"

ptl "\n✓ Все примеры выполнены!"
