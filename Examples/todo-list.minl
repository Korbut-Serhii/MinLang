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
                ## rebuild list without nil
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