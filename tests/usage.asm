extern str_concat
extern str_len

section .data
    hello       db "Hello, ", 0
    world       db "World!", 10, 0
    buffer      times 128 db 0

section .text
    global _start

_start:
    lea rdi, [rel hello]
    lea rsi, [rel world]
    lea rdx, [rel buffer]
    call str_concat

    mov rax, 1
    mov rdi, 1
    lea rsi, [rel buffer]
    call str_len
    mov rdx, rax
    mov rax, 1
    mov rdi, 1
    syscall

    mov rsi, buffer
    call str_len
    mov rdx, rax

    mov rax, 60
    xor rdi, rdi
    syscall