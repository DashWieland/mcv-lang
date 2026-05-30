# truth_machine.s -- read a number N.
#   N == 0 : print 0 once and halt.
#   N != 0 : print 1 forever.
# The canonical esolang sanity check. Heap address 0 is scratch.
# Labels: C = print-one loop, V = zero case.

push 0
readnum     # heap[0] = N
push 0
retrieve    # stack: [N]
jz V        # N == 0 -> zero case (pops N)

mark C      # --- print 1 forever ---
push 1
outnum
jmp C

mark V      # --- zero case ---
push 0
outnum
end
