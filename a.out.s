section .data
text db "Hello, World!
", 0


section .text
global _start



; function .
_start:
call main


; function main
main:
mov rax, 1
mov rdi, 1
mov rsi, text
mov rdx, 13
syscall
mov rdi, 0
mov rax, 60
syscall

