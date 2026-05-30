# cat.s -- echo input to output, character by character, until EOF.
# readchar stores -1 at end of input; -1 is negative, so jneg detects EOF.
# Heap address 0 is scratch. Labels: C = loop, V = done.

mark C      # --- loop ---
push 0
readchar    # heap[0] = next char, or -1 at EOF
push 0
retrieve    # stack: [c]
dup         # stack: [c, c]
jneg V      # if c < 0 (EOF) -> done (pops one copy)
outchar     # output the character (pops the other copy)
jmp C

mark V      # --- done ---
discard     # drop the leftover -1
end
