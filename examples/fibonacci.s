# fibonacci.s -- prints the first 10 Fibonacci numbers, one per line.
# Heap layout: [0]=a (current), [1]=b (next), [2]=counter (numbers left).
# Assembles to fibonacci.mcv. Labels: C = loop, V = end.

push 0      # a = 0
push 0
store
push 1      # b = 1
push 1
store
push 2      # counter = 10
push 10
store

mark C      # --- loop ---
push 2
retrieve    # counter
jz V        # counter == 0 -> done

push 0
retrieve    # a
outnum
push 10     # newline
outchar

# next = a + b
push 0
retrieve
push 1
retrieve
add         # stack: [next]

# a = b
push 0
push 1
retrieve
store       # heap[0] = b ; stack still [next]

# b = next
push 1
swap        # stack: [1, next]
store       # heap[1] = next

# counter = counter - 1
push 2
push 2
retrieve
push 1
sub
store

jmp C

mark V      # --- done ---
end
