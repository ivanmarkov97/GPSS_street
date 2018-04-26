import copy
import block
from block import random
import numpy as np
from goto import with_goto
import math

T_NUM = 0
T_TIME = 1
T_CUR = 2
T_NEXT = 3
T_WAITING = 4

class Device:
	def __init__(self, num):
		self.num = num
		self.is_free = True

class Generate(block.Block):
	def __init__(self, b_id, seed=0, road="MAIN"):
		self.b_id = b_id
		self.seed = seed
		self.road = road
		random.seed(self.seed)
		super(Generate, self).__init__(b_id)
	def execute(self, trans):
		global TIME
		global TRANS_NUM
		global CUR_BLOCK
		global INTENSIVE1
		global INTENSIVE2
		if self.road == "MAIN":
			time = random.expovariate(1.0 / 3.0)
			#time = 3
		if self.road == "SEC":
			time = random.expovariate(1.0 / 8.5)
			#time = 8.5
		TRANS_NUM += 1
		#print("GENERATE")
		CUR_BLOCK = self.b_id
		return [TRANS_NUM, TIME + time, None, self.b_id, False]


class Transfer(block.Block):
	def __init__(self, b_id, prob=None, block1=None, block2=None):
		self.prob = prob
		self.block1 = block1
		self.block2 = block2
		super(Transfer, self).__init__(b_id)
	def execute(self, trans):
		global CUR_BLOCK
		p = random.uniform(0,1)
		p = np.random.sample()
		#print("p, prob ", p, self.prob)
		if p < self.prob:
			#print("GONNA TO ", self.block1)
			CUR_BLOCK = self.block1 - 1
		else:
			#print("GONNA TO ", self.block2)
			CUR_BLOCK = self.block2 - 1
		self.enter_count += 1
		#print("TRANSFER")


class Test(block.Block):
	def __init__(self, b_id, opt, pos1, pos2, Q_type, block_exit):
		self.b_id = b_id
		self.opt = opt
		self.pos1 = pos1
		self.pos2 = pos2
		self.Q_type = Q_type
		self.block_exit = block_exit
		super(Test, self).__init__(b_id)
	def execute(self, trans):
		global CUR_BLOCK
		global MAIN_Q
		global SEC_Q
		self.enter_count += 1
		if self.Q_type == "MAIN":
			if MAIN_Q[self.pos1] < MAIN_Q[self.pos2]:
				CUR_BLOCK = self.b_id
				print("TO LEFT ", CUR_BLOCK)
			else:
				CUR_BLOCK = self.block_exit - 1
				print("TO CENTER ", CUR_BLOCK)
		if self.Q_type == "SEC":
			if SEC_Q[self.pos1] < SEC_Q[self.pos2]:
				CUR_BLOCK = self.b_id
			else:
				CUR_BLOCK = self.block_exit - 1
		#print("TEST")


class Queue(block.Block):
	def __init__(self, b_id, Q_pos, Q_type):
		self.b_id = b_id
		self.Q_pos = Q_pos
		self.Q_type = Q_type
		super(Queue, self).__init__(b_id)
	def execute(self, trans):
		global MAIN_Q
		global SEC_Q
		global CUR_BLOCK
		if self.Q_type == "MAIN":
			MAIN_Q[self.Q_pos] += 1
		if self.Q_type == "SEC":
			SEC_Q[self.Q_pos] += 1
		CUR_BLOCK = self.b_id
		self.enter_count += 1
		#print("QUEUE")


class Depart(block.Block):
	def __init__(self, b_id, Q_pos, Q_type):
		self.b_id = b_id
		self.Q_pos = Q_pos
		self.Q_type = Q_type
		super(Depart, self).__init__(b_id)
	def execute(self, trans):
		global MAIN_Q
		global SEC_Q
		global CUR_BLOCK
		if self.Q_type == "MAIN":
			MAIN_Q[self.Q_pos] -= 1
		if self.Q_type == "SEC":
			SEC_Q[self.Q_pos] -= 1
		CUR_BLOCK = self.b_id
		self.enter_count += 1
		#print("DEPART")


class Seize(block.Block):
	def __init__(self, b_id, pos, D_type):
		self.b_id = b_id
		self.pos = pos
		self.D_type = D_type
		super(Seize, self).__init__(b_id)
	def execute(self, trans):
		global MAIN_LINE
		global SEC_LINE
		global CUR_BLOCK
		if self.D_type == "MAIN":
			if MAIN_LINE[self.pos].is_free == True:
				MAIN_LINE[self.pos].is_free = False
				trans[T_WAITING] = False
				CUR_BLOCK = self.b_id
				self.enter_count += 1
			else:
				trans[T_WAITING] = True
		if self.D_type == "SEC":
			if SEC_LINE[self.pos].is_free == True:
				SEC_LINE[self.pos].is_free = False
				trans[T_WAITING] = False
				CUR_BLOCK = self.b_id
				self.enter_count += 1
			else:
				trans[T_WAITING] = True
		#print("SEIAE")


class Release(block.Block):
	def __init__(self, b_id, pos, D_type):
		self.b_id = b_id
		self.pos = pos
		self.D_type = D_type
		super(Release, self).__init__(b_id)
	def execute(self, trans):
		global MAIN_LINE
		global SEC_LINE
		global CUR_BLOCK
		if self.D_type == "MAIN":
			MAIN_LINE[self.pos].is_free = True
		if self.D_type == "SEC":
			SEC_LINE[self.pos].is_free = True
		self.enter_count += 1
		CUR_BLOCK = self.b_id
		#print("RELEASE")


class Advance(block.Block):
	def __init__(self, b_id, time=None, role=None):
		self.b_id = b_id
		self.time = time
		self.role = role
		super(Advance, self).__init__(b_id)
	def execute(self, trans):
		global TIME
		global CUR_BLOCK
		global INTENSIVE1
		global INTENSIVE2
		global INTENSIVE_TURN
		self.enter_count += 1
		if self.role == "TURN":
			trans[T_TIME] = TIME + INTENSIVE_TURN
		elif self.role == "STRAIGHT_MAIN":
			trans[T_TIME] = TIME + INTENSIVE1
		elif self.role == "STRAIGHT_SEC":
			trans[T_TIME] = TIME + INTENSIVE2
		else:
			trans[T_TIME] = TIME + self.time
		#print("ADVANCE BLOCK ",self.b_id)
		#print("ADVANCE TIME ",self.time)
		#trans[T_TIME] = TIME + self.time
		#print("ADVANCE TRANS TIME ", trans[T_TIME])
		CUR_BLOCK = self.b_id - 1 #!!!!!!!!!?????????????
		#print("ADVANCE")
		return trans


class Gate(block.Block):
	def __init__(self, b_id, opt, pos):
		self.opt = opt
		self.pos = pos
		super(Gate, self).__init__(b_id)
	def execute(self, trans):
		global GREEN
		global CUR_BLOCK
		if self.opt == "LS":
			if GREEN[self.pos] is True:
				CUR_BLOCK = self.b_id
				trans[T_WAITING] = False
				self.enter_count += 1
			else:	
				trans[T_WAITING] = True
		if self.opt == "LR":
			if GREEN[self.pos] is False:
				CUR_BLOCK = self.b_id
				trans[T_WAITING] = False
				self.enter_count += 1
			else:	
				trans[T_WAITING] = True
		#print("GATE")


class Logic(block.Block):
	def __init__(self, b_id, opt, pos):
		self.b_id = b_id
		self.opt = opt
		self.pos = pos
		super(Logic, self).__init__(b_id)
	def execute(self, trans):
		global GREEN
		global CUR_BLOCK
		self.enter_count += 1
		if self.opt == "S":
			GREEN[self.pos] = True
		if self.opt == "R":
			GREEN[self.pos] = False
		CUR_BLOCK = self.b_id
		#print("LOGIC")


class Savevalue(block.Block):
	def __init__(self, b_id, val, S_type):
		self.b_id = b_id
		self.val = val
		self.S_type = S_type
		super(Savevalue, self).__init__(b_id)
	def execute(self, trans):
		global INTENSIVE1
		global INTENSIVE2
		global CUR_BLOCK
		global TIME
		if self.S_type == "MAIN":
			INTENSIVE1 = self.val
		if self.S_type == "SEC":
			INTENSIVE2 = self.val
		self.enter_count += 1
		CUR_BLOCK = self.b_id
		#print("SAVEVALUE")


class Terminate(block.Block):
	def __init__(self, b_id):
		self.b_id = b_id
		super(Terminate, self).__init__(b_id)
	def execute(self, trans):
		self.enter_count += 1
		#print("TERMINATE")

class Start(block.Block):
	def __init__(self, b_id):
		self.b_id = b_id
		super(Start, self).__init__(b_id)
	def execute(self, trans):
		self.enter_count += 1
		#print("START")


GREEN_TIME_LIGHT_MAIN = 120
GREEN_TIME_LIGHT_SEC = 80
GREEN_TIME_DELTA = 60

INTENSIVE_TURN = 3
INTENSIVE1 = 3 
INTENSIVE2 = 3 

L_MAIN = 0
C_MAIN = 1
R_MAIN = 2

L_SEC = 0
R_SEC = 1

TIME = 0
TRANS_NUM = 0

CUR_BLOCK = 0
GREEN = [False, False, False, False] 

MAIN_LINE = [Device(1), Device(2), Device(3)]
SEC_LINE = [Device(4), Device(5)]

MAIN_Q = [0, 0, 0]
SEC_Q = [0, 0]

MEAN_MAIN_Q_LEFT = []
MEAN_MAIN_Q_CENTER = []
MEAN_MAIN_Q_RIGHT = []

MEAN_SEC_Q_LEFT = []
MEAN_SEC_Q_RIGHT = []

def correct_timer(cur_events, fut_events):
	global TIME
	global MAIN_Q
	global SEC_Q
	global MEAN_MAIN_Q_RIGHT
	global MEAN_MAIN_Q_CENTER
	global MEAN_MAIN_Q_LEFT
	global MEAN_SEC_Q_RIGHT
	global MEAN_SEC_Q_LEFT

	MEAN_MAIN_Q_RIGHT.append(copy.copy(MAIN_Q[2]))
	MEAN_MAIN_Q_CENTER.append(copy.copy(MAIN_Q[1]))
	MEAN_MAIN_Q_LEFT.append(copy.copy(MAIN_Q[0]))

	MEAN_SEC_Q_RIGHT.append(copy.copy(SEC_Q[1]))
	MEAN_SEC_Q_LEFT.append(copy.copy(SEC_Q[0]))

	time = fut_events[0][T_TIME]
	TIME = time
	print("TIME ", TIME)
	add_to_cur = []
	for tran in fut_events:
		if tran[T_TIME] == time:
			add_to_cur.append(copy.copy(tran))
	for tran in add_to_cur:
		del fut_events[fut_events.index(tran)]
	for tran in add_to_cur:
		cur_events.append(copy.copy(tran))
	for tran in cur_events:
		tran[T_TIME] = TIME
@with_goto
def view_phase(cur_events, fut_events, model):
	global CUR_BLOCK
	label .begin
	cur_events_go = copy.copy(cur_events)
	for trans in cur_events_go:
		CUR_BLOCK = copy.copy(trans[T_NEXT]) - 1
		while 1:
			if isinstance(model[CUR_BLOCK], Generate):
				if model[CUR_BLOCK].b_id != 57:
					trans[T_CUR] = trans[T_NEXT]
					trans[T_NEXT] += 1
					new_trans = model[CUR_BLOCK].execute(trans)
					fut_events.append(copy.copy(new_trans))
					fut_events.sort(key = lambda tr: tr[T_TIME])
					continue
				else:
					trans[T_CUR] = trans[T_NEXT]
					trans[T_NEXT] += 1
					CUR_BLOCK += 1
			elif isinstance(model[CUR_BLOCK], Advance):
				trans = model[CUR_BLOCK].execute(trans)
				trans[T_CUR] = trans[T_NEXT]
				trans[T_NEXT] += 1
				fut_events.append(copy.copy(trans))
				fut_events.sort(key = lambda tr: tr[T_TIME])
				del cur_events[cur_events.index(trans)]
				break
			elif isinstance(model[CUR_BLOCK], Terminate):
				model[CUR_BLOCK].execute(trans)
				del cur_events[cur_events.index(trans)]	
				goto .begin
				break
			else:
				model[CUR_BLOCK].execute(trans)
				if trans[T_WAITING]:
					break
				trans[T_CUR] = trans[T_NEXT]
				trans[T_NEXT] = CUR_BLOCK + 1

model = [
	Generate(b_id=1, seed=1, road="MAIN"),							#			    GENERATE (Exponential(1, 0, 3)) 
	Transfer(2, 0.5, block1=3, block2=5),							#			    TRANSFER 0.5,STRAIGHT_MAIN,TURN_MAIN 
	Test(3, "L", L_MAIN, C_MAIN, "MAIN", block_exit=21),			#STRAIGHT_MAIN  TEST L Q$Q_LEFT_MAIN,Q$Q_CENTER,SEIZE_CENTER 
	Transfer(4, prob=1, block1=6),									#				TRANSFER ,SEIZE_LEFT_MAIN

	Transfer(5,prob=0.5,block1=14,block2=6),						#TURN_MAIN 		TRANSFER 0.5,SEIZE_RIGHT_MAIN,SEIZE_LEFT_MAIN 

	Queue(6, L_MAIN, "MAIN"),										#SEIZE_LEFT_MAIN QUEUE Q_LEFT_MAIN 
	Seize(7, L_MAIN, "MAIN"),										#				SEIZE LEFT_LINE_MAIN 
	Gate(8, "LS", 0),												#				GATE LS GREEN1 
	Transfer(9,prob=0.75,block1=10,block2=28),						#				TRANSFER 0.75,LEFT_LEFT_LINE_MAIN 
	Depart(10, L_MAIN, "MAIN"),										#				DEPART Q_LEFT_MAIN 
	Advance(11, INTENSIVE1, role="STRAIGHT_MAIN"),					#				ADVANCE X$INTENSIVE1 
	Release(12, L_MAIN, "MAIN"),									#				RELEASE LEFT_LINE_MAIN
	Terminate(13),													#				TERMINATE

	Queue(14, R_MAIN, "MAIN"),										#SEIZE_RIGHT_MAIN QUEUE Q_RIGHT_MAIN 
	Seize(15, R_MAIN, "MAIN"),										#				SEIZE RIGHT_LINE_MAIN 
	Gate(16, "LS", 0),												#				GATE LS GREEN1
	Depart(17, R_MAIN, "MAIN"),										#				DEPART Q_RIGHT_MAIN 
	Advance(18, INTENSIVE_TURN, role="TURN"),						#				ADVANCE INTENSIVE_TURN
	Release(19, R_MAIN, "MAIN"),									#				RELEASE RIGHT_LINE_MAIN 
	Terminate(20),													#				TERMINATE

	Queue(21, C_MAIN, "MAIN"),										#SEIZE_CENTER QUEUE Q_CENTER 							
	Seize(22, C_MAIN, "MAIN"),										#				SEIZE CENTER_LINE 
	Gate(23, "LS", 0),												#				GATE LS GREEN1
	Depart(24, C_MAIN, "MAIN"),										#				DEPART Q_CENTER 
	Advance(25, INTENSIVE1, role="STRAIGHT_MAIN"),					#				ADVANCE X$INTENSIVE1 
	Release(26, C_MAIN, "MAIN"),									#				RELEASE CENTER_LINE 
	Terminate(27),													#				TERMINATE

	Gate(28, "LR", 2),												#LEFT_LEFT_LINE_MAIN GATE LR GREEN3 
	Depart(29, L_MAIN, "MAIN"),										#				DEPART Q_LEFT_MAIN 
	Advance(30, INTENSIVE_TURN, role="TURN"),						#				ADVANCE INTENSIVE_TURN
	Release(31, L_MAIN, "MAIN"),									#				RELEASE LEFT_LINE_MAIN
	Terminate(32),													#				TERMINATE

	Generate(b_id=33, seed=2, road="SEC"),							#				GENERATE (Exponential(2, 0, 8.5)) 
	Transfer(34,prob=0.5,block1=35,block2=36),						#				TRANSFER 0.5,STRAIGHT_SEC,TURN_SEC 
	Transfer(35,prob=1,block1=37),									#STRAIGHT_SEC   TRANSFER ,SEIZE_LEFT_SEC 

	Transfer(36,prob=0.5,block1=45,block2=37),						#TURN_SEC 		TRANSFER 0.5,SEIZE_RIGHT_SEC,SEIZE_LEFT_SEC

	Queue(37, L_SEC, "SEC"),										#SEIZE_LEFT_SEC QUEUE Q_LEFT_SEC 
	Seize(38, L_SEC, "SEC"),										#				SEIZE LEFT_LINE_SEC 
	Gate(39, "LS", 1),												#				GATE LS GREEN2 
	Transfer(40,prob=0.75,block1=41,block2=52),						#				TRANSFER 0.75,LEFT_LEFT_LINE_SEC 

	Depart(41, L_SEC, "SEC"),										#				DEPART Q_LEFT_SEC 
	Advance(42, INTENSIVE2, role="STRAIGHT_SEC"),					#				ADVANCE X$INTENSIVE2 
	Release(43, L_SEC, "SEC"),										#				RELEASE LEFT_LINE_SEC 
	Terminate(44),													#				TERMINATE

	Queue(45, R_SEC, "SEC"),										#SEIZE_RIGHT_SEC QUEUE Q_RIGHT_SEC 
	Seize(46, R_SEC, "SEC"),										#				SEIZE RIGHT_LINE_SEC 
	Gate(47, "LS", 1),												#				GATE LS GREEN2 
	Depart(48, R_SEC, "SEC"),										#				DEPART Q_RIGHT_SEC 
	Advance(49, INTENSIVE_TURN, role="TURN"),						#				ADVANCE INTENSIVE_TURN 
	Release(50, R_SEC, "SEC"),										#				RELEASE RIGHT_LINE_SEC 
	Terminate(51),													#				TERMINATE

	Gate(52, "LR", 3),												#LEFT_LEFT_LINE_SEC GATE LR GREEN4 
	Depart(53, L_SEC, "SEC"),										#				DEPART Q_LEFT_SEC 
	Advance(54, INTENSIVE_TURN, role="TURN"),						#				ADVANCE INTENSIVE_TURN 
	Release(55, L_SEC, "SEC"),										#				RELEASE LEFT_LINE_SEC 
	Terminate(56),													#				TERMINATE

	Generate(b_id=57),												#				GENERATE,,,1 
	Logic(58, "S", 0),												#LIGHT 			LOGIC S GREEN1 
	Savevalue(59, 3, "MAIN"),										#				SAVEVALUE INTENSIVE1,3 
	Advance(60, time=10),											#				ADVANCE 10 
	Savevalue(61, 1.2, "MAIN"),										#				SAVEVALUE INTENSIVE1,1.2 
	Advance(62, GREEN_TIME_DELTA-10),								#				ADVANCE (GREEN_TIME_DELTA-10) 
	Logic(63, "S", 2),												#				LOGIC S GREEN3 
	Savevalue(64, 3, "SEC"),										#				SAVEVALUE INTENSIVE2,3 
	Advance(65, time=10),											#				ADVANCE 10 
	Savevalue(66, 1.2, "SEC"),										#				SAVEVALUE INTENSIVE2,1.2 
	Advance(67, GREEN_TIME_LIGHT_MAIN - GREEN_TIME_DELTA - 10),		#				ADVANCE (GREEN_TIME_LIGHT_MAIN-GREEN_TIME_DELTA-10) 
	Logic(68, "R", 0),												#				LOGIC R GREEN1 
	Advance(69, GREEN_TIME_DELTA),									#				ADVANCE GREEN_TIME_DELTA
	Logic(70, "R", 2),												#				LOGIC R GREEN3 


	Logic(71, "S", 1),												#				LOGIC S GREEN2
	Savevalue(72, 3, "MAIN"),										#				SAVEVALUE INTENSIVE1,3 
	Advance(73, time=10),											#				ADVANCE 10 
	Savevalue(74, 1.2, "MAIN"),										#				SAVEVALUE INTENSIVE1,1.2 
	Advance(75, GREEN_TIME_DELTA - 10),								#				ADVANCE (GREEN_TIME_DELTA-10)
	Logic(76, "S", 3),												#				LOGIC S GREEN4 
	Savevalue(77, 3, "SEC"),										#				SAVEVALUE INTENSIVE2,3 
	Advance(78, time=10),											#				ADVANCE 10 
	Savevalue(79, 1.2, "SEC"),										#				SAVEVALUE INTENSIVE2,1.2 
	Advance(80,GREEN_TIME_LIGHT_SEC - GREEN_TIME_DELTA - 10),		#				ADVANCE (GREEN_TIME_LIGHT_SEC-GREEN_TIME_DELTA-10) 
	Logic(81, "R", 1),												#				LOGIC R GREEN2 
	Advance(82, GREEN_TIME_DELTA),									#				ADVANCE GREEN_TIME_DELTA 
	Logic(83, "R", 3),												#				LOGIC R GREEN4 

	Transfer(84, prob=1, block1=58),								#				TRANSFER ,LIGHT 

	Generate(b_id=85),												#				GENERATE 3600 
	Terminate(86),													#				TERMINATE 1 
	Start(87)														#				START 1

]

cur_events = []
fut_events = []

for op in model:
	if isinstance(op, Generate):
		if op.b_id != 57 and op.b_id != 85:
			trans = [0, 0, 0, 0, False]
			fut_events.append(copy.copy(op.execute(trans)))

fut_events.append([3, 0, None, 57, False])
fut_events.append([4, 3600, None, 85, False])
TRANS_NUM += 2

fut_events.sort(key = lambda tr: tr[T_TIME])

while TIME < 3600:
	correct_timer(cur_events, fut_events)
	view_phase(cur_events, fut_events, model)

print("GLOBAL TIME ", TIME)

print("CHECk")
print(cur_events)
print(fut_events)
print("LIGHT ", GREEN)
print("MAIN_DEVICE")
for ml in MAIN_LINE:
	print(ml.is_free)
print("SEC_DEVICE")
for sl in SEC_LINE:
	print(sl.is_free)
print("MAIN_QUEUE")
print(MAIN_Q)
print("SEC_QUEUE")
print(SEC_Q)

print("TRANS_NUM" ,TRANS_NUM)

print("MEAN")
print("MEAN_MAIN_Q_LEFT", np.mean(MEAN_MAIN_Q_LEFT))
print("MEAN_MAIN_Q_CENTER", np.mean(MEAN_MAIN_Q_CENTER))
print("MEAN_MAIN_Q_RIGHT", np.mean(MEAN_MAIN_Q_RIGHT))
print("MEAN_SEC_Q_LEFT", np.mean(MEAN_SEC_Q_LEFT))
print("MEAN_SEC_Q_RIGHT", np.mean(MEAN_SEC_Q_RIGHT))

print("MAX")
print("MAX_MAIN_Q_LEFT", np.max(MEAN_MAIN_Q_LEFT))
print("MAX_MAIN_Q_CENTER", np.max(MEAN_MAIN_Q_CENTER))
print("MAX_MAIN_Q_RIGHT", np.max(MEAN_MAIN_Q_RIGHT))
print("MAX_SEC_Q_LEFT", np.max(MEAN_SEC_Q_LEFT))
print("MAX_SEC_Q_RIGHT", np.max(MEAN_SEC_Q_RIGHT))

