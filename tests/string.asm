global str_concat
global str_len

str_concat:
    push rbp
    mov rbp, rsp

    mov r8, rdi
    mov r9, rsi
    mov r10, rdx

.copy_str1:
    mov al, [r8]
    mov [r10], al
    cmp al, 0
    je .copy_str2_start
    inc r8
    inc r10
    jmp .copy_str1

.copy_str2_start:
    mov rsi, r9
    mov rdi, r10

.copy_str2_loop:
    mov al, [rsi]
    mov [rdi], al
    cmp al, 0
    je .done
    inc rsi
    inc rdi
    jmp .copy_str2_loop

.done:
    mov rsp, rbp
    pop rbp
    ret

str_len:
    push rbp
    mov rbp, rsp

    mov rdi, rsi
    xor rax, rax

.len_loop:
    cmp byte [rdi + rax], 0
    je .done_len
    inc rax
    jmp .len_loop

.done_len:
    mov rsp, rbp
    pop rbp
    ret