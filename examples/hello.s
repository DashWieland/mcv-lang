# hello.s -- prints "Hello, World!\n"
# For each character: push its ASCII code, then output it as a character.
# Assembles to hello.mcv.

push 72     # H
outchar
push 101    # e
outchar
push 108    # l
outchar
push 108    # l
outchar
push 111    # o
outchar
push 44     # ,
outchar
push 32     # (space)
outchar
push 87     # W
outchar
push 111    # o
outchar
push 114    # r
outchar
push 108    # l
outchar
push 100    # d
outchar
push 33     # !
outchar
push 10     # newline
outchar
end
