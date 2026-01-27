REM ============================================================================
REM GOING - Exit/Cleanup Routine for CAVE
REM ============================================================================
REM This program is executed via *GOING command to exit CAVE gracefully
REM It contains machine code routines and displays a farewell message
REM ============================================================================

   10 REM Machine code entry points
   20 REM .0 = Clear screen routine at &3000
   30 REM 60 = Display message routine at &3060
   40 REM F0 = Clear memory routine at &30F0
   50 REM i0 = Copy screen data routine at &3069
   
   60 REM Machine code at &3000:
   70 REM Clear screen and display farewell message
   80 REM Then execute BYE and BASIC commands
   
   90 REM The program contains embedded data:
  100 REM - "BYE" command (to log off network)
  110 REM - "BASIC" command (to return to BASIC prompt)
  120 REM - MODE 7 teletext screen data for farewell message

REM ============================================================================
REM MACHINE CODE DISASSEMBLY
REM ============================================================================
REM
REM &3000: Clear screen routine
REM   LDY #&00        ; Y = 0
REM   TYA             ; A = 0
REM   PHA             ; Push A
REM   LDA #&12        ; VDU 18 (set graphics mode)
REM   JSR &FFF4       ; OSWRCH
REM   LDA #&12        ; VDU 18 again
REM   JSR &FFF4       ; OSWRCH
REM   PLA             ; Pull A
REM   TAY             ; Y = A
REM   INY             ; Y++
REM   BNE loop        ; Loop until Y wraps to 0
REM   LDA #&16        ; VDU 22 (MODE command)
REM   JSR &FFEE       ; OSBYTE
REM   LDA #&07        ; MODE 7
REM   JSR &FFEE       ; OSBYTE
REM   RTS
REM
REM &3030: Execute OS command
REM   LDX #&71        ; Point to command string
REM   LDY #&30        ; at &3071
REM   JSR &FFF7       ; OSCLI
REM   RTS
REM
REM &3040: Clear memory routine
REM   LDA &18         ; Get HIMEM low byte
REM   STA &71         ; Store in zero page
REM   LDA #&00        ; A = 0
REM   STA &70         ; Store in zero page
REM   LDY #&00        ; Y = 0
REM   STA (&70),Y     ; Clear memory
REM   INY             ; Y++
REM   BNE loop        ; Loop
REM   RTS
REM
REM &3060: Display screen data
REM   LDA #&12        ; VDU 18
REM   JSR &FFF4       ; OSWRCH
REM   LDY #&00        ; Y = 0
REM   LDA &307B,Y     ; Load screen data
REM   STA &7C00,Y     ; Store to screen memory
REM   LDA &317B,Y     ; Load more data
REM   STA &7D00,Y     ; Store to screen
REM   LDA &327B,Y     ; Load more data
REM   STA &7E00,Y     ; Store to screen
REM   LDA &337B,Y     ; Load more data
REM   STA &7F00,Y     ; Store to screen
REM   INY             ; Y++
REM   BNE loop        ; Loop
REM   RTS
REM
REM &3075: Execute commands
REM   LDX #&75        ; Point to "BYE" command
REM   LDY #&30        ; at &3075
REM   JSR &FFF7       ; OSCLI (execute BYE)
REM   RTS

REM ============================================================================
REM EMBEDDED DATA
REM ============================================================================
REM
REM &3071: Command strings
REM   "BYE" + CR      ; Network logoff command
REM   "BASIC" + CR    ; Return to BASIC
REM
REM &307B onwards: MODE 7 teletext screen data
REM   Contains the farewell message displayed on exit:
REM
REM   Line with spaces (padding)
REM   CHR$134 + "You have just left.."  (Yellow text)
REM   More padding
REM   CHR$141 + CHR$129 + "  CAVE"      (Double height, cyan)
REM   CHR$141 + CHR$129 + "  CAVE"      (Second line of double height)
REM   More padding
REM   CHR$134 + CHR$168 + "(C)" + CHR$169 + " 1985 XOB Partners."
REM   (Yellow text with flashing copyright symbol)

REM ============================================================================
REM SUMMARY
REM ============================================================================
REM When *GOING is executed:
REM 1. Clears the screen
REM 2. Switches to MODE 7 (teletext)
REM 3. Displays farewell message with:
REM    - "You have just left.."
REM    - "CAVE" in double-height text
REM    - "(C) 1985 XOB Partners."
REM 4. Executes BYE command (logs off Econet)
REM 5. Returns to BASIC prompt
REM ============================================================================
