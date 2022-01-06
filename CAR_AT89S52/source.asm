ORG 0000H
	JMP DEFINE_PORT
ORG 000BH
	LJMP ISR_TIMER0	  
ORG 0023H
	LJMP ISRUART
	
DEFINE_REG52:
	T2CON   		DATA    0C8H
	RCAP2L  		DATA    0CAH
	RCAP2H  		DATA    0CBH
	TL2     		DATA    0CCH
	TH2     		DATA    0CDH
		
	ET2    		 	BIT     0ADH
	PT2     		BIT     0BDH
	T2EX    		BIT     91H
	T2      		BIT     90H
	TF2     		BIT     0CFH
	EXF2    		BIT     0CEH
	RCLK    		BIT     0CDH
	TCLK    		BIT     0CCH
	EXEN2  			BIT     0CBH
	TR2     		BIT     0CAH
	C_T2    		BIT     0C9H
	CP_RL2  		BIT     0C8H

DEFINE_PORT:
	MOTOR_A_PORT 	EQU P2.0
	AIN_1_PORT		EQU P2.2
	AIN_2_PORT		EQU P2.1
	BIN_1_PORT		EQU P2.3
	BIN_2_PORT		EQU P2.4
	MOTOR_B_PORT	EQU	P2.5
	SERVO_PORT 		EQU	P1.4
	SENSOR_0_PORT	EQU	P1.0
	SENSOR_1_PORT	EQU P1.2
	SENSOR_2_PORT	EQU	P1.3
	MODE_BUTTON		EQU P3.6
		
DEFINE_ADDRESS:
	MOTOR_SPEED		EQU 30H
	SERVO_ANGLE		EQU 31H
	MOTOR_COUNTER	EQU 32H
	SERVO_COUNTER	EQU 33H
	DISTANCE		EQU 34H
	RECEIVED_DATA	EQU	35H
	DRIVE_MODE		EQU	36H

DEFINE_VALUE:
	MOV SERVO_ANGLE, 	#16
	MOV MOTOR_SPEED, 	#75 ;75/100
	MOV MOTOR_COUNTER, 	#0
	MOV SERVO_COUNTER, 	#0
	MOV DISTANCE, 		#0
	MOV RECEIVED_DATA, 	#0
	MOV DRIVE_MODE, 	#1

MAIN:
	ACALL SETUP
	
	JB MODE_BUTTON, MODE_2
		MODE_1:
			JB SENSOR_0_PORT, $							;wait until signal is set
			LOOP_MODE_1:
				JNB SENSOR_0_PORT, TARGET				;if (signal_0) jmp taget
					JB SENSOR_1_PORT, MISS_LEFT			;if (!signal_1) jmp miss_left
						MOV A, #5						;turn_left mode
						ACALL TB6612_SET_MODE			
						
						JB SENSOR_0_PORT, $				;wait until signal is set		
						
						MOV A, #1						;stop mode
						ACALL TB6612_SET_MODE			
						JMP LOOP_MODE_1			
					MISS_LEFT:
						JB SENSOR_2_PORT, MISS_BOTH		;if (!signal_2) jmp miss_both
						
						MOV A, #4						;turn_right mode
						ACALL TB6612_SET_MODE			
						
						JB SENSOR_0_PORT, $				;wait until signal is set		
						
						MOV A, #1						;stop mode
						ACALL TB6612_SET_MODE			
						JMP LOOP_MODE_1
					MISS_BOTH:
						MOV A, #2						;forward mode
						ACALL TB6612_SET_MODE
						JMP LOOP_MODE_1
				TARGET:
					MOV A, #1
					ACALL TB6612_SET_MODE
					 JMP LOOP_MODE_1
		MODE_2:
			ACALL IS_SAFE
		JMP MODE_2		
RET

SETUP:
	ACALL PORT_SETUP
	
	MOV A, DRIVE_MODE
	ACALL TB6612_SET_MODE
	
	ACALL TIMER_SETUP
	ACALL UART_SETUP
	
	SETB TR0
	SETB TR1
RET

UART_SETUP:
	MOV SCON, #50H
	SETB ES
RET

PORT_SETUP:
	SETB MOTOR_A_PORT;
	SETB MOTOR_B_PORT;
	SETB SERVO_PORT;
	
	SETB SENSOR_0_PORT ;HIGH, INPUT
	SETB SENSOR_1_PORT
	SETB SENSOR_2_PORT
	SETB MODE_BUTTON
RET

TB6612_SET_MODE:	
	SHORT_BRAKE:
		CJNE A, #0, STOP
			SETB AIN_2_PORT
			SETB AIN_1_PORT
			SETB BIN_2_PORT
			SETB BIN_1_PORT
	RET
	
	STOP:
		CJNE A, #1, FORWARD
			CLR AIN_2_PORT
			CLR AIN_1_PORT
			CLR BIN_2_PORT
			CLR BIN_1_PORT
	RET
	
	FORWARD:
		CJNE A, #2, BACK
			SETB AIN_1_PORT
			CLR  AIN_2_PORT
			SETB BIN_2_PORT
			CLR  BIN_1_PORT
	RET
	
	BACK:
		CJNE A, #3, TURN_RIGHT
			CLR  AIN_1_PORT
			SETB AIN_2_PORT
			CLR	 BIN_2_PORT
			SETB BIN_1_PORT
	RET
	
	TURN_RIGHT:
		CJNE A, #4, TURN_LEFT
			SETB AIN_1_PORT
			CLR  AIN_2_PORT
			CLR  BIN_2_PORT
			SETB BIN_1_PORT
	RET
	
	TURN_LEFT:
		CJNE A, #5, SHORT_BRAKE
			CLR  AIN_1_PORT
			SETB AIN_2_PORT
			SETB BIN_2_PORT
			CLR  BIN_1_PORT
	RET
RET

TIMER_SETUP:
	;TIMER0, TIMER1
	SETB EA
	SETB ET0
	
	MOV TMOD, #0022H
	
	MOV TH0, #00A3H ;0.1MS
	MOV TL0, #00A3H
	
	MOV TH1, #00FDH
	MOV TL1, #00FDH
RET

DELAY_10US: 
	MOV R6,	#2
	DJNZ R6, $
RET 

MOTOR_PWM:
	MOV A, MOTOR_COUNTER
	
	;FOR (i = 0; i < 100; i++) {
	;IF (MOTOR_COUNTER <= SPEED) SETB PORT
	;ELSE CLR PORT } duty_cycle = motor_counter
	
	CJNE A, MOTOR_SPEED, NOT_EQUAL_HIGH			
		JMP MOTOR_HIGH					
	NOT_EQUAL_HIGH:
		JC MOTOR_HIGH
		GREATER_HIGH:								
			CJNE A, #100, NOT_EQUAL_LOW
				MOV MOTOR_COUNTER, #0
				JMP MOTOR_LOW		
			NOT_EQUAL_LOW:
				JMP MOTOR_LOW
	MOTOR_HIGH:
		SETB MOTOR_A_PORT
		SETB MOTOR_B_PORT
	RET
	
	MOTOR_LOW:
		CLR MOTOR_A_PORT
		CLR MOTOR_B_PORT
	RET
RET

SERVO_PWM:	
	MOV A, SERVO_COUNTER
	;20ms 0,1ms
	CJNE A, SERVO_ANGLE, NOT_EQUAL_A			
		JMP SERVO_HIGH					
	NOT_EQUAL_A:
		JC SERVO_HIGH
		LESS_A:								
			CJNE A, #201, NOT_EQUAL_20MS
				MOV SERVO_COUNTER, #0
				JMP SERVO_LOW		
			NOT_EQUAL_20MS:
				JMP SERVO_LOW	
				
	SERVO_HIGH:
		SETB SERVO_PORT
	RET
	
	SERVO_LOW:
		CLR SERVO_PORT
	RET
RET

IS_SAFE:
	JNB SENSOR_0_PORT, NOT_SAFE
		MOV A, DRIVE_MODE
		ACALL TB6612_SET_MODE
		RET
	NOT_SAFE:
		MOV A, #1
		ACALL TB6612_SET_MODE
		RET
RET

ISR_TIMER0:
	INC MOTOR_COUNTER
	INC SERVO_COUNTER
	
	LCALL SERVO_PWM
	LCALL MOTOR_PWM
RETI

ISRUART:
	JB RI, RECEIVED
		RETI
	RECEIVED:
		MOV A, SBUF
		MOV R0, A
		
		MOV SERVO_ANGLE, #16	
			
		MOV A, #1
		MOV DRIVE_MODE, A
		ACALL TB6612_SET_MODE
		
		CJNE R0, #';', END_RECEIVED
		
		MOVE_STOP:
			CJNE R0, #'S', MOVE_FORWARD
			
			MOV SERVO_ANGLE, #16	
			
			MOV A, #1
			MOV DRIVE_MODE, A
			ACALL TB6612_SET_MODE	
		JMP END_RECEIVED
		
		MOVE_FORWARD:
			CJNE R0, #'F', MOVE_BACK
			
			MOV SERVO_ANGLE, #16
			
			MOV A, #2
			MOV DRIVE_MODE, A
			ACALL TB6612_SET_MODE	
		JMP END_RECEIVED
				
		MOVE_BACK:
			CJNE R0, #'B', TURNN_LEFT

			MOV SERVO_ANGLE, #16
			
			MOV A, #3
			MOV DRIVE_MODE, A
			ACALL TB6612_SET_MODE
		JMP END_RECEIVED
		
		TURNN_LEFT:
			CJNE R0, #'L', TURNN_RIGHT
			
			MOV SERVO_ANGLE, #12	
		JMP END_RECEIVED
		
		TURNN_RIGHT:
			CJNE R0, #'R', TURNN_LEFT_FORWARD
			
			MOV SERVO_ANGLE, #20
		JMP END_RECEIVED
		
		TURNN_LEFT_FORWARD:
			CJNE R0, #'G', TURNN_RIGHT_FORWARD
			
			MOV SERVO_ANGLE, #12	
			
			MOV A, #2
			MOV DRIVE_MODE, A
			ACALL TB6612_SET_MODE	
		JMP END_RECEIVED
				
		TURNN_RIGHT_FORWARD:
			CJNE R0, #'I', TURNN_LEFT_BACK
			
			MOV SERVO_ANGLE, #20	
			
			MOV A, #2
			MOV DRIVE_MODE, A
			ACALL TB6612_SET_MODE	
		JMP END_RECEIVED
				
		TURNN_LEFT_BACK:
			CJNE R0, #'H', TURNN_RIGHT_BACK
			
			MOV SERVO_ANGLE, #12	
			
			MOV A, #3
			MOV DRIVE_MODE, A
			ACALL TB6612_SET_MODE	
		JMP END_RECEIVED
				
		TURNN_RIGHT_BACK:
			CJNE R0, #'J', END_RECEIVED
			
			MOV SERVO_ANGLE, #20	
			
			MOV A, #3
			MOV DRIVE_MODE, A
			ACALL TB6612_SET_MODE	
		JMP END_RECEIVED
		
		END_RECEIVED: 
			CLR RI
	RETI
RETI

END