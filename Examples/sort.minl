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