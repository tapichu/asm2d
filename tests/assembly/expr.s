CONST1      EQU     -10
CONST2      EQU     #CONST1 * 2
CONST3      EQU     #CONST2 / #CONST1
CONST4      EQU     #CONST2 - #CONST3 + #CONST1
CONST5      EQU     5 * 4 / 2 + 1
CONST6      EQU     5 * 4 / (2 + 1)
CONST7      EQU     5 * -4 - -2

.main       LDX     #CONST1
            LDX     #CONST2
            LDX     #CONST3
            LDX     #CONST4
            LDX     #CONST5
            LDX     #CONST6
            LDX     #CONST7
