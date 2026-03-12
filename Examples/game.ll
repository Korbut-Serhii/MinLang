## The computer picks a random number, the player guesses it.

L secret = randInt(1, 100)
L attempts = 0

ptl "I am thinking of a number between 1 and 100."

wh T {
    inp "Your guess: " raw

    if !canInt(raw) {
        ptl "Please enter a whole number."
        cnt
    }

    L guess = int(raw)
    attempts = attempts + 1

    if guess < secret {
        ptl "Too low! Try higher."
    } elif guess > secret {
        ptl "Too high! Try lower."
    } el {
        ptl f"Correct! You got it in {attempts} attempts."
        brk
    }
}