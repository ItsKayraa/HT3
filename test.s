section .data
section .data
x dq 10
y dq 20
result dq 0


section .text
global _start
section .text
global _start



; function .
_start:
call main


; function add
add:
mov rax, rdi
add rax, rsi
ret


; function main
main:
mov rdi, [x]
mov rsi, [y]
call add
mov [result], rax
mov rax, 60
mov rdi, [result]
syscall
ret

