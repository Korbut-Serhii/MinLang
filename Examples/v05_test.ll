fn factorial(n) {
    if n <= 1 { rt 1 }
    rt n * factorial(n - 1)
}
ptl factorial(10)

lp i in rng(5) {
    if i == 3 { cnt }
    ptl i
}