global str_concat
global str_len

; str_concat
; str_concat is a label that gets 2 strings and makes them together, returns the value at dest.
; Usage:
; lea rdi, [rel str1]
; lea rsi, [rel str2]
; lea rdx, [rel dest]
; call str_concat
str_concat:
    push rdi
    push rsi
    push rdx
.copy_str1:
    mov al, [rdi]
    mov [rdx], al
    cmp al, 0
    je .copy_str2_start
    inc rdi
    inc rdx
    jmp .copy_str1

.copy_str2_start:
    pop rdx
    push rdx
.find_end:
    mov al, [rdx]
    cmp al, 0
    je .copy_str2
    inc rdx
    jmp .find_end

.copy_str2:
    pop rdx
.copy_str2_loop:
    mov al, [rsi]
    mov [rdx], al
    cmp al, 0
    je .done
    inc rsi
    inc rdx
    jmp .copy_str2_loop

.done:
    pop rdx
    pop rsi
    pop rdi
    ret

str_len:
    xor rax, rax
.len_loop:
    cmp byte [rsi + rax], 0
    je .done
    inc rax
    jmp .len_loop
.done:
    ret