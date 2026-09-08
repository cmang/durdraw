    .model tiny
    .8086
    .code
    org 100h
start:
    ; clear screen by initializing text mode
    mov ax, 3 
    int 10h

    ; Prepare to copy ansi to video memory
    mov ax, 0B800h  ; segment address of color text mode
    mov es, ax

    mov si, offset num_bytes ; Source is now the address of num_bytes
    ;mov di, 160    ; Destination address in video frame
    mov di, 0    ; Destination address in video frame

    mov cx, word ptr [si]      ; Get number of bytes from memory
    add si, 2                ; Point SI to screen_data

    ; Copy data to video memory
copy_loop:
    lodsb      ; load a byte from [si] into al, increment si
    stosb      ; store al into [es:di], increment di
    loop copy_loop  ; decrement cx, jump to copy_loop if not zero

    ; Move cursor to last line while ANSI is showing.
    mov ah, 2   ; 2 = position cursor (BIOS call)
    mov bh, 0   ; page 0
    mov dh, 24   ; line 24
    mov dl, 0  ; col 0
    int 10h

    ;; delay for a split sceond
    ;mov ah, 86h		; 86h = BIOS delay
    ;mov al, 0	; clear low bits
    ;mov cx, 10  ; cx and dx are high and low for
    ;mov dx, 000     ; 32 bit unsigned int (delay time in msec)
    ;                ; 01f4h = 500
    ;int 15h 

    ; Wait for the user to press a key.
    call wait_for_key

; Move cursor to 2nd last line, to keep ANSI from scrolling
; off screen
    mov ah, 2   ; 2 = position cursor (BIOS call)
    mov bh, 0   ; page 0
    mov dh, 23   ; line
    mov dl, 0  ; column
    int 10h

exit:
    mov ax, 4C00h    ; DOS terminate program function
    int 21h

wait_for_key:
    mov ah, 6   ; function 6, DOS console i/o
    mov dl, 0ffh        ; paramater for read
    int 21h             ; dos interrupt
    jz wait_for_key     ; loop until key is pressed
    ret

    ; Data segment (within code segment in .COM)
num_bytes dw 1920  ; Number of bytes to copy (was 1920)
screen_data:
    db 'D', 02h, 'u', 03h, 'R', 04h, 'r', 51h
    ;times 30 db 'H', 51h, 'i', 51h

    end start

