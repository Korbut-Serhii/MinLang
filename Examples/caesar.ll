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