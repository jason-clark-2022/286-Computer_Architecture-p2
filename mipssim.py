import sys
import os
import struct

registers = [0] * 32
addy = []
immediate = []
memoryAccess = [0] * 264

def dissasembler():
    with open ( sys.argv[2], 'rb') as file:
        data = file.read()

    fileOut = open("OUTPUTFILENAME_dis.txt", "w")
    counter = 0
    instruction = []
    breached = False
    global assembly
    global memory
    global binary
    #Grabs bits, disassembles and populates arrays for simulator
    for i in range(0, len(data), 4):
        asUInt = struct.unpack_from(">I", data, i)[0]
        instruction.append(struct.unpack_from(">I", data, i)[0])
        currI = instruction[len(instruction) -1]
        asBin = format(asUInt, '0>32b')
        asBinSpace = asBin[0] + ' ' + asBin[1:6] + ' ' + asBin[6:11] + ' ' + asBin[11:16] + ' ' + asBin[16:21] + ' ' + asBin[21:26] + ' ' + asBin[26:]
        valid = asUInt >> 31
        opcode = asUInt >> 26
        fnCode = int(asBin[26:], 2)
        rsInt = int(asBin[6:11], 2)
        rtInt = int(asBin[11:16], 2)
        offset = int(asBin[16:], 2)
        offset18 = int(asBin[16:], 2) << 2
        imm = ((currI << 16) & 0xFFFFFFFF) >> 16
        imm = unsigned_to_signed_converter(imm)
        shiftAmount = int(asBin[21:26], 2)
        jTarget = int(asBin[6:], 2) << 2
        rd = ((asUInt << 16) & 0x0FFFFFFFF) >> 27
        rs = ((asUInt << 6) & 0x0FFFFFFFF) >> 27
        rt = ((asUInt << 11) & 0x0FFFFFFFF) >> 27
        ins = unsigned_to_signed_converter(asUInt)
        shiftBits = unsigned_to_signed_converter(imm)
        shiftBits <<= 2
        text = ''
        instType = -50
        binary.append(currI)
        if not breached:
            if valid == 1:
                if opcode == 40: 
                    text = 'ADDI\tR' + str(rt) + ', R' + str(rs) + ', #' + str(imm)
                    instType = 1
                    assembly.append([instType,rt,rs,imm])
                elif opcode == 43: 
                    text = 'SW\tR' + str(rt) + ', ' + str(offset) + '(R' + str(rs) + ')'
                    instType = 2
                    assembly.append([instType,rt,imm,rs])
                elif opcode == 35: 
                    text = 'LW\tR' + str(rt) + ', ' + str(offset) + '(R' + str(rs) + ')'
                    instType = 3
                    assembly.append([instType,rt,imm,rs])
                elif opcode == 34: 
                    text = 'J\t#' + str(jTarget)
                    instType = 4 
                    assembly.append([instType,jTarget])
                elif opcode == 36: 
                    text = 'BEQ\tR' + str(rs) + ',R' + str(rt) + ' ' + str(offset)
                    instType = 5 
                    assembly.append([instType,rs,rt,shiftBits])
                elif opcode == 33: 
                    text = 'BLTZ\tR' + str(rs) + ', #' + str(offset18)
                    instType = 6 
                    assembly.append([instType,rs,shiftBits])
                elif opcode == 60: 
                    text = 'MUL\tR' + str(rd) + ', R' + str(rs) + ', R' + str(rt)
                    instType = 7
                    assembly.append([instType,rd,rs,rt])
                elif ( opcode == 32 and fnCode == 8 ): 
                    text = 'JR\tR' + str(rs)
                    instType = 8
                    assembly.append([instType,rs])
                elif ( opcode == 32 and fnCode == 32 ): 
                    text = 'ADD\tR' + str(rd) + ', R' + str(rs) + ', R' + str(rt)
                    instType = 9
                    assembly.append([instType,rd,rs,rt])
                elif ( opcode == 32 and fnCode == 0 ): 
                    text = 'SLL\tR' + str(rd) + ', R' + str(rt) + ', #' + str(shiftAmount)
                    instType = 10
                    assembly.append([instType,rd,rt,shiftAmount])
                elif ( opcode == 32 and fnCode == 34 ): 
                    text = 'SUB\tR' + str(rd) + ', R' + str(rs) + ', R' + str(rt)
                    instType = 11
                    assembly.append([instType,rd,rs,rt])
                elif ( opcode == 32 and fnCode == 2 ): 
                    text = 'SRL\tR' + str(rd) + ', R' + str(rt) + ', #' + str(shiftAmount)
                    instType = 12
                    assembly.append([instType,rd,rt,shiftAmount])
                elif ( opcode == 32 and fnCode == 36 ): 
                    text = 'AND\tR' + str(rd) + ', R' + str(rs) + ', R' + str(rt)
                    instType = 13
                    assembly.append([instType,rd,rs,rt])
                elif ( opcode == 32 and fnCode == 10 ): 
                    text = 'MOVZ\tR' + str(rd) + ', R' + str(rs) + ', R' + str(rt)
                    instType = 14
                    assembly.append([instType,rd,rs,rt])
                elif ( opcode == 32 and fnCode == 37 ): 
                    text = 'OR\tR' + str(rd) + ', R' + str(rs) + ', R' + str(rt)
                    instType = 15
                    assembly.append([instType,rd,rs,rt])
                if ( opcode == 32 and fnCode == 0 and rsInt == 0 and rtInt == 0 ): 
                    text = 'NOP'
                    instType = 16
                    assembly.append([instType])
                elif ( opcode == 32 and fnCode == 13 ):
                    text = 'BREAK'
                    breached = True
                    instType = 0
                    assembly.append([instType])
            else:
                instrType = -1
                assembly.append([instType])
        else:
            instType = -2
            if memory[0] == 0:
                memory[0] = (i) + 96
            memory[1] = (i) + 96
            memoryI = (i)  + 96
            memory[memoryI] = ins
            memoryI += 4
        
        #Format for what will be outputted to file.
        item = {'addr':96+i, 'binspace':asBinSpace, 'text': text , 'rs':rs, 'rt':rt}
        output = ( item['binspace'] + ' ' + str(item['addr']) + '\t' + item['text'] + '\n')
        fileOut.write(output)
    toMem()

def toMem():
    global memory
    for i in range(len(assembly)):
        curr = ((i * 4) + 96)
        memory[curr] = assembly[i]

def writeToReg():
    global modified
    modified = False
    cache_initialize()
    global postMem_empty
    global postMem
    global postAlu_empty
    global postAlu
    if postMem_empty == False:
        regDest = assembly[postMem[0]][1]
        registers[regDest] = postMem[1]
        postMem_empty = True
        modified = True
        postMem = [-1, -1]
    if postAlu_empty == False:
        regDest = assembly[postAlu[0]][1]
        registers[regDest] = postAlu[1]
        postAlu_empty = True
        modfied = True
        postAlu = [-1, -1]

def postmemWrite():
    global postMem
    global postMem_empty
    global modified
    if preMem_empty == False:
        currInstruction = preMem[0][0]
        modified = True
        if assembly[currInstruction][0] == 2:
            regVal = registers[assembly[currInstruction][1]]
            memoryLocation = preMem[0][1]
            cacheWriteCheck = cache_setter(memoryLocation, regVal)
            if cacheWriteCheck == -1:
                return 
            shiftMem()
        elif assembly[currInstruction][0] == 3:
            memAddy = assembly[currInstruction][2] + registers[assembly[currInstruction][3]]
            regVal = cache_getter(memAddy)
            if regVal == -1:
                return
            postMem = ([currInstruction, regVal])    
            postMem_empty = False
            shiftMem()

def ALU():
    global postAlu
    global postAlu_empty
    if preAlu_empty == False:
        currInstruction1 = preAlu[0][0]
        if assembly[currInstruction1][0] == 9:
            addVal = preAlu[0][1] + preAlu[0][2]
            postAlu[0] = currInstruction1
            postAlu[1] = addVal
        elif assembly[currInstruction1][0] == 1:
            addVal = preAlu[0][1] + preAlu[0][2]
            postAlu[0] = currInstruction1
            postAlu[1] = addVal
        shiftAlu()
        postAlu_empty = False 

def updateIss():
    global preIssue
    if not preIssue_empty:
        count = 0
        for i in preIssue:
            if not i == -1:
                currInst = assembly[i]
                if (currInst[0] == 2 or currInst[0] == 3) and not preMemFull():
                    address = currInst[1]
                    immediateVal = currInst[2]
                    base = currInst[3]
                    if not (checkHaz(count) or checkHaz(count)):
                        if not loadBeforeStore(count):
                            offset = registers[base] + immediateVal
                            insertMemory([i, offset])
                            preIssue[count] = -1

                elif not preALUFull() and not (currInst[0] == 2 or currInst[0] == 3): 
                    if currInst[0] == 1:
                        if not (checkHaz(count) or checkHaz(count) ):
                            if not loadBeforeStore(count):
                                num1 = registers[currInst[2]]
                                num2 = currInst[3]
                                insertAlu([i, num1, num2])
                                preIssue[count] = -1

                    elif currInst[0] == 9:
                        if not (checkHaz(count) or checkHaz(count) or checkHaz(count)):
                            if not loadBeforeStore(count):
                                num1 = registers[currInst[2]]
                                num2 = registers[currInst[3]]
                                insertAlu([i, num1, num2])
                                preIssue[count] = -1
                    else:
                        if not loadBeforeStore(count):
                            num1 = currInst[2]
                            num2 = currInst[3]
                            insertAlu([i, num1, num2])
                            preIssue[count] = -1
            count += 1
    shiftIssue()    

def fetch():
    global lineCounter
    global run
    if preIssue_full == False:
        for i in range(0,2):
            currInstruction2 = cache_getter(lineCounter)
            if currInstruction2 == -1:
                return

            if currInstruction2[0] == 16:
                lineCounter += 4
                return

            if currInstruction2[0] == -1:
                lineCounter += 4

            elif currInstruction2[0] == 4:
                lineCounter = currInstruction2[1]

            elif currInstruction2[0] == 8:  
                if readAfterWrite(-1) == False:
                    lineCounter = registers[currInstruction2[1]]
                    return

            elif currInstruction2[0] == 6: 
                if readAfterWrite(-1) == False:
                    if registers[currInstruction2[1]] < 0:
                        lineCounter += currInstruction2[2] + 4
                    else:
                        lineCounter += 4
                else:
                    return
            elif currInstruction2[0] == 0: 
                if preIssue_empty and preMem_empty and preAlu_empty and postMem_empty and postAlu_empty and not modified:
                    wbd()
                    run = False
                return
            if not preIssue_full and not (currInstruction2[0] == 5 or currInstruction2[0] == 4  or currInstruction2[0] == 8 or currInstruction2[0] == 6 or currInstruction2[0] == -1):
                insertIssue(int((lineCounter-96) / 4))
                lineCounter += 4
def shiftMem():
    global preMem_empty 
    global preMem
    preMem[0] = preMem[1]
    if preMem[0] != -1:
        preMem[1] = -1
    else:
        preMem_empty = True
        preMem = [-1,-1]

def shiftAlu():
    global preAlu
    global preAlu_empty
    preAlu[0] = preAlu[1]
    if preAlu[0] != -1:
        preAlu[1] = -1
    else:
        preAlu_empty = True
        preAlu = [-1,-1]

def shiftIssue():
    global preIssue
    global preIssue_empty
    global preIssue_full
    empty = True
    shift = False
    for currInst in preIssue:
        if currInst != -1:
            empty = False
    if empty == False:
        for i in range(0, 2):
            if preIssue[0] == -1 and preIssue[1] != -1:
                preIssue[0], preIssue[1] = preIssue[1], preIssue[0]
                shift = True
            if preIssue[1] == -1 and preIssue[2] != -1:
                preIssue[1], preIssue[2] = preIssue[2], preIssue[1]
                shift = True
            if preIssue[2] == -1 and preIssue[3] != -1:
                preIssue[2], preIssue[3] = preIssue[3], preIssue[2]
                shift= True
    else:
        preIssue_empty = True

    if preIssue_full and shift:
        preIssue_full = False      

def insertAlu(value):
    global preAlu
    global preAlu_empty
    if preAlu[0] == -1:
        preAlu[0] = value
        preAlu_empty = False
    elif preAlu[1] == -1:
        preAlu[1] = value
    else:
        sys.exit(1)
def insertMemory(value):
    global preMem
    global preMem_empty
    if preMem[0] == -1:
        preMem[0] = value
        preMem_empty = False
    elif preMem[1] == -1:
        preMem[1] = value
    else:
        sys.exit(1)
def insertIssue(value):
    global preIssue
    global preIssue_empty
    global preIssue_full
    if preIssue[0] == -1:
        preIssue[0] =  value
        preIssue_empty = False
    elif preIssue[1] == -1:
        preIssue[1] =  value
    elif preIssue[2] == -1:
        preIssue[2] =  value
    elif preIssue[3] == -1:
        preIssue[3] =  value
        preIssue_full = True
    else:
        sys.exit(1)

def loadBeforeStore(count):
    if count == 1:
        firstIns = assembly[preIssue[0]]
        if firstIns[0] == 2:
            return True
    elif count == 2:
        firstIns = assembly[preIssue[0]]
        secIns = assembly[preIssue[1]]
        if firstIns[0] == 2 or secIns[0] == 2:
            return True
    elif count == 3:
        firstIns = assembly[preIssue[0]]
        secIns = assembly[preIssue[1]]
        thirdIns = assembly[preIssue[2]]
        if firstIns[0] == 2 or secIns[0] == 2 or thirdIns[0] == 2:
            return True 
    else:
        return False

# Check if preIssue is full
def preIssueFull():
    issueFull = False
    if preIssue[0] != -1 and preIssue[1] != -1 and preIssue[2] != -1 and preIssue[3] != -1:
                    issueFull = True
    return issueFull

# Check if preALU is full
def preALUFull():
    return True if preAlu[0] != -1 and preAlu[1] != -1 else False
    
# Check if preMem is full
def preMemFull():
    return True if preMem[0] != -1 and preMem[1] != -1 else False


def cache_getter(mem_address):
    global queue
    tag = mem_address >> 5
    word = (((mem_address << 29) & 0xFFFFFFFF) >> 31) + 3 
    set_select = ((mem_address << 27) & 0xFFFFFFFF) >> 30
    if(cache[set_select][1][2] == tag):
       cache[set_select][0] = 1
       return cache[set_select][1][word]
    elif(cache[set_select][2][2] == tag):
        cache[set_select][0] = 0
        return cache[set_select][2][word]
    else:
        queue.append(mem_address)
        return -1
        
def cache_setter(mem_address, mem_val):
    global cache
    currInstruction3 = cache_getter(mem_address)
    if currInstruction3 == -1:
        return currInstruction3
    tag = mem_address >> 5
    word = (((mem_address << 29) & 0xFFFFFFFF) >> 31) + 3
    set_select = ((mem_address << 27) & 0xFFFFFFFF) >> 30
    if cache[set_select][1][2] == tag:
        cache[set_select][1][word] = mem_val
        cache[set_select][1][1] = 1
    else:
        cache[set_select][2][word] = mem_val
        cache[set_select][2][1] = 1

def cache_initialize():
    global queue
    global cache
    if len(queue) > 0:
        for i in range(len(queue)):
            tag = queue[i] >> 5
            word = (((queue[i] << 29) & 0xFFFFFFFF) >> 31) + 3
            set_select = ((queue[i] << 27) & 0xFFFFFFFF) >> 30
            if cache[set_select][1][0] != 1: 
                cache[set_select][1][2] = tag
                cache[set_select][1][0] = 1
                if word == 3: 
                    cache[set_select][1][3] = memory[queue[i]]
                    cache[set_select][1][4] = memory[(queue[i] + 4)]
                    writeUpdate(queue[i], queue[i] + 4, set_select, 0)
                else: 
                    cache[set_select][1][4] = memory[queue[i]]
                    cache[set_select][1][3] = memory[(queue[i] - 4)]
                    writeUpdate(queue[i] - 4, queue[i], set_select, 0)
                cache[set_select][0] = 1

            elif cache[set_select][2][0] != 1: 
                cache[set_select][2][2] = tag
                cache[set_select][2][0] = 1
                if word == 3:
                    cache[set_select][2][3] = memory[queue[i]]
                    cache[set_select][2][4] = memory[(queue[i] + 4)]
                    writeUpdate(queue[i], queue[i] + 4, set_select, 1)
                else: 
                    cache[set_select][2][4] = memory[queue[i]]
                    cache[set_select][2][3] = memory[(queue[i] - 4)]
                    writeUpdate(queue[i] - 4, queue[i], set_select, 1)
                
                cache[set_select][0] = 0

            else: 
                LRU = cache[set_select][0] + 1
                if cache[set_select][LRU][1] == 1: 
                    wb(set_select, LRU - 1)
                cache[set_select][LRU][2] = tag
                if word == 3:
                    cache[set_select][LRU][3] = memory[queue[i]]
                    cache[set_select][LRU][4] = memory[(queue[i] + 4)]
                    writeUpdate(queue[i], queue[i] + 4, set_select, LRU - 1)
                else: 
                    cache[set_select][LRU][4] = memory[queue[i]]
                    cache[set_select][LRU][3] = memory[(queue[i] - 4)]
                    writeUpdate(queue[i] - 4, queue[i], set_select, LRU - 1)
                cache[set_select][0] = LRU % 1 
        queue = []

def writeUpdate(w1, w2, set_select1, way):
    global write_queue
    to = way * 2
    write_queue[set_select1][to] = w1
    write_queue[set_select1][to + 1] = w2

def wb(set_select, way):
    global memory
    global cache
    to = way * 2
    memAddress = write_queue[set_select][to]
    memory[memAddress] = cache[set_select][way + 1][3]
    memory[memAddress + 4] = cache[set_select][way + 1][4]
    cache[set_select][way + 1][1] = 0

def wbd():
    if cache[0][1][1] == 1:
        wb(0, 0)
    if cache[0][2][1] == 1:
        wb(0, 1)
    if cache[1][1][1] == 1:
        wb(1, 0)
    if cache[1][2][1] == 1:
        wb(1, 1)
    if cache[2][1][1] == 1:
        wb(2, 0)
    if cache[2][2][1] == 1:
        wb(2, 1)
    if cache[3][1][1] == 1:
        wb(3, 0)
    if cache[3][2][1] == 1:
        wb(3, 1)


def checkHaz(count):
    waw = writeAfterWrite(count)
    raw = readAfterWrite(count)
    war = writeAfterRead(count)
    return waw or raw or war    

def writeAfterWrite(count):
    check = assembly[preIssue[count]][1]
    if count == 3:
        issue_element = 2
    elif count == 2:
        issue_element = 1
    elif count == 1:
        issue_element = 0
    else:
        issue_element = -1
    if preIssue_empty == False:
        for i in range(issue_element, -1, -1):
            currInst = preIssue[i]
            if currInst != -1:
                currAssemb = assembly[currInst]
                regAddress = currAssemb[1]
                if check == regAddress:
                    return True
    if preAlu_empty == False:
        for currInst in preAlu:
            if currInst != -1:
                currAssemb = assembly[currInst[0]]
                regAddress = currAssemb[1]
                if check == regAddress:
                    return True    
    if postAlu_empty == False:
        currAssemb = assembly[postAlu[0]]
        regAddress = currAssemb[1]
        if check == regAddress:
            return True              
    if preMem_empty == False:
        for currInst in preMem:
            if currInst != -1:
                currAssemb = assembly[currInst[0]]
                regAddress = currAssemb[1]
                if check == regAddress:
                    return True  
    if postMem_empty == False:
        currAssemb = assembly[postMem[0]]
        regAddress = currAssemb[1]
        if check == regAddress:
            return True
    return False
def writeAfterRead(count):
    check = assembly[preIssue[count]][1]
    if count == 3:
        issue_element = 2
    elif count == 2:
        issue_element = 1
    elif count == 1:
        issue_element = 0
    else:
        issue_element = -1

    for i in range(issue_element, -1, -1):
        curr_inst = preIssue[i]
        if curr_inst != -1:
            currAssemb = assembly[preIssue[i]]
            if currAssemb[0] == 2 or currAssemb[0] == 3:
                if check == currAssemb[1] or check == currAssemb[3]:
                    return True
            elif currAssemb[0] == 1 or currAssemb[0] == 10 or currAssemb[0] == 12:
                if check == currAssemb[1] or check == currAssemb[2]:
                    return True
            else:
                if check == currAssemb[1] or check == currAssemb[2] or check == currAssemb[3]:
                    return True
    if assembly[preIssue[count]][0] == 2 or assembly[preIssue[count]][0] == 3:
        if preAlu_empty == False:
            for currInst in preAlu:
                if currInst != -1:
                    currAssemb = assembly[currInst[0]]
                    if currAssemb[0] == 1 or currAssemb[0] == 10 or currAssemb[0] == 12:
                        if check == currAssemb[1] or check == currAssemb[2]:
                            return True
                    else:
                        if check == currAssemb[1] or check == currAssemb[2] or check == currAssemb[3]:
                            return True 
    else:
        if preMem_empty == False:
            for currInst in preMem:
                if currInst != -1:
                    currAssemb = assembly[currInst[0]]
                    if check == currAssemb[1] or check == currAssemb[3]:
                            return True
    return False
def readAfterWrite(count):
    if count == -1:
        issue_element = 3
        inst_curr = memory[lineCounter]
    if count == 3:
        issue_element = 2
        inst_curr = assembly[preIssue[3]]
    elif count == 2:
        issue_element = 1
        inst_curr = assembly[preIssue[2]]
    elif count == 1:
        issue_element = 0
        inst_curr = assembly[preIssue[1]]
    else:
        issue_element = -1
        inst_curr = assembly[preIssue[0]]

    if inst_curr[0] == 1 or inst_curr[0] == 10 or inst_curr[0] == 12:
        checkcount = 1
        check = [inst_curr[2]]
    elif inst_curr[0] == 2 or inst_curr[1] == 3:
        checkcount = 1
        check = [inst_curr[3]]
    elif inst_curr[0] == 6 or inst_curr[0] == 8:
        checkcount = 1
        check = [inst_curr[1]]
    else:
        checkcount = 2
        check = [inst_curr[2], inst_curr[3]]    

    for i in range(0, checkcount):
        if preIssue_empty == False:
            for j in range(issue_element, -1, -1):
                currInst = preIssue[j]
                if currInst != -1:
                    currAssemb = assembly[currInst]
                    regAddress = currAssemb[1] 
                    if check[i] == regAddress:
                        return True
        if preAlu_empty == False:
            for currInst in preAlu:
                if currInst != -1:
                    currAssemb = assembly[currInst[0]]
                    regAddress = currAssemb[1]
                    if check[i] == regAddress:
                        return True    
        if postAlu_empty == False:
            currAssemb = assembly[postAlu[0]]
            regAddress = currAssemb[1]
            if check[i] == regAddress:
                return True                 
        if preMem_empty == False:
            for currInst in preMem:
                if currInst != -1:
                    currAssemb = assembly[currInst[0]]
                    regAddress = currAssemb[1]
                    if check[i] == regAddress:
                        return True    
        if postMem_empty == False:
            currAssemb = assembly[postMem[0]]
            regAddress = currAssemb[1]
            if check[i] == regAddress:
                return True    
    return False
    
out = open("OUTPUTFILENAME_pipeline", 'w')
def printOutput():
    global cycle
    output = ""
    pre_Issue0 = ""
    pre_Issue1 = ""
    pre_Issue2 = ""
    pre_Issue3 = ""
    pre_ALU0 = ""
    pre_ALU1 = ""
    post_ALU = ""
    pre_MEM0 = ""
    pre_MEM1 = ""
    post_MEM = ""

    if preIssue[0] != -1:
        pre_Issue0 = instruction(preIssue[0])
        if preIssue[1] != -1:
            pre_Issue1 = instruction(preIssue[1])
            if preIssue[2] != -1:
                pre_Issue2 = instruction(preIssue[2])
                if preIssue[3] != -1:
                    pre_Issue3 = instruction(preIssue[3])
    if preMem[0] != -1:
        pre_MEM0 = instruction(preMem[0][0])
        if preMem[1] != -1:
            pre_MEM1 = instruction(preMem[1][0])
    if preAlu[0] != -1:
        pre_ALU0 = instruction(preAlu[0][0])
        if preAlu[1] != -1:
            pre_ALU1 = instruction(preAlu[1][0])
    if postMem[0] != -1:
        post_MEM = instruction(postMem[0])
    if postAlu[0] != -1:
        post_ALU = instruction(postAlu[0])

    print("--------------------",file=out)
    print("Cycle: " + str(cycle) + "\n",file=out)
    print("Pre-Issue Buffer: ",file=out)
    print("\tEntry 0:\t" + pre_Issue0 ,file=out)
    print("\tEntry 1:\t" + pre_Issue1 ,file=out)
    print("\tEntry 2:\t" + pre_Issue2 ,file=out)
    print("\tEntry 3:\t" + pre_Issue3 ,file=out)
    print("Pre_ALU Queue: ",file=out)
    print("\tEntry 0:\t" + pre_ALU0 ,file=out)
    print("\tEntry 1:\t" + pre_ALU1,file=out)
    print("Post_ALU Queue: ",file=out)
    print("\tEntry 0:\t" + post_ALU,file=out)
    print("Pre_MEM Queue: ",file=out)
    print("\tEntry 0:\t" + pre_MEM0,file=out)
    print("\tEntry 1:\t" + pre_MEM1,file=out)
    print("Post_MEM Queue: ",file=out)
    print("\tEntry 0:\t" + post_MEM + "\n" ,file=out)

    reg = ""
    extra = ""
    for i in range(0,4):
        extra = "0" if i==0 or i==1 else ""
        reg += "R" + extra + str(8*i) + ": \t" + str(registers[(8*i)+0]) + "\t" + str(registers[(8*i)+1]) + "\t" + str(registers[(8*i)+2]) + "\t" + str(registers[(8*i)+3]) + "\t" + \
                                               str(registers[(8*i)+4]) + "\t" + str(registers[(8*i)+5]) + "\t" + str(registers[(8*i)+6]) + "\t" + str(registers[(8*i)+7]) + "\n"
    
    output += "Registers\n"
    output += str(reg) + "\n"
    output += "Cache\n"

    getCache = ""
    getCache += "Set 0: LRU=" + str(cache[0][0]) + "\n"
    getCache += "\tEntry 0:[(" + str(cache[0][1][0]) + "," + str(cache[0][1][1]) + "," + str(cache[0][1][2]) + ")<" + str(format(getBin(0,0,0),'032b')) + "," + str(format(getBin(0,0,1),'032b')) + ">" + "\n"
    getCache += "\tEntry 1:[(" + str(cache[0][2][0]) + "," + str(cache[0][2][1]) + "," + str(cache[0][2][2]) + ")<" + str(format(getBin(0,1,0),'032b')) + "," + str(format(getBin(0,1,1),'032b')) + ">" + "\n"
    
    getCache += "Set 1: LRU=" + str(cache[1][0]) + "\n"
    getCache += "\tEntry 0:[(" + str(cache[1][1][0]) + "," + str(cache[1][1][1]) + "," + str(cache[1][1][2]) + ")<" + str(format(getBin(1,0,0),'032b')) + "," + str(format(getBin(1,0,1),'032b')) + ">" + "\n"
    getCache += "\tEntry 1:[(" + str(cache[1][2][0]) + "," + str(cache[1][2][1]) + "," + str(cache[1][2][2]) + ")<" + str(format(getBin(1,1,0),'032b')) + "," + str(format(getBin(1,1,1),'032b')) + ">" + "\n"

    getCache += "Set 2: LRU=" + str(cache[2][0]) + "\n"
    getCache += "\tEntry 0:[(" + str(cache[2][1][0]) + "," + str(cache[2][1][1]) + "," + str(cache[2][1][2]) + ")<" + str(format(getBin(2,0,0),'032b')) + "," + str(format(getBin(2,0,1),'032b')) + ">" + "\n"
    getCache += "\tEntry 1:[(" + str(cache[2][2][0]) + "," + str(cache[2][2][1]) + "," + str(cache[2][2][2]) + ")<" + str(format(getBin(2,1,0),'032b')) + "," + str(format(getBin(2,1,1),'032b')) + ">" + "\n"
    
    getCache += "Set 3: LRU=" + str(cache[3][0]) + "\n"
    getCache += "\tEntry 0:[(" + str(cache[3][1][0]) + "," + str(cache[3][1][1]) + "," + str(cache[3][1][2]) + ")<" + str(format(getBin(3,0,0),'032b')) + "," + str(format(getBin(3,0,1),'032b')) + ">" + "\n"
    getCache += "\tEntry 1:[(" + str(cache[3][2][0]) + "," + str(cache[3][2][1]) + "," + str(cache[3][2][2]) + ")<" + str(format(getBin(3,1,0),'032b')) + "," + str(format(getBin(3,1,1),'032b')) + ">" + "\n"
    
    output += getCache
    print(output, file = out)
    
    data = memory[0]
    getMem = ""
    for i in range(0, int((((memory[1] - memory[0])/4) +1))):
        if i == 0:
            getMem += str(data) + ":\t"
        elif i % 8 == 0:
                getMem += "\n" + str(data) + ":\t"
        getMem += str(memory[data]) + "\t"
        data += 4

    print("Data",file=out)
    print(str(getMem),file=out)   

def unsigned_to_signed_converter(num):
    neg_bit_mask = 0x00008000
    if (neg_bit_mask & num) > 0:
        num |= 0xFFFF0000
        num ^= 0xFFFFFFFF
        num += 1
        num *= -1
    return num
    
def getBin(sett, way, word):
    bina = cache[sett][way + 1][word + 3]
    if bina == 0: 
        return 0
    if isinstance(bina, int):
        if bina < 0:
            return unsigned_to_signed_converter(bina)
        return bina
    else:
        element = (way * 2) + word
        instr = int((write_queue[sett][element] - 96) /4)
        return binary[instr]

# Get full instruction from assembly array and reassemble 
def instruction(instruction):
    instr = assembly[instruction][0]
    if instr == 1: # ADDI
        output = "[ADDI\tR" + str(assembly[instruction][1]) + ", R" + str(assembly[instruction][2]) + ", #" + str(assembly[instruction][3]) + "]"
    elif instr == 2: # SW
        output = "[SW\tR" + str(assembly[instruction][1]) + ", " + str(assembly[instruction][2]) + "(R" + str(assembly[instruction][3]) + ")]"
    elif instr == 3: # LW
        output = "[LW\tR" + str(assembly[instruction][1]) + ", " + str(assembly[instruction][2]) + "(R" + str(assembly[instruction][3]) + ")]"
    elif instr == 4: # J
        output = "[J\t" + str(assembly[instruction][1]) + "]"
    elif instr == 5: # BEQ
        output = "[BEQ\tR" + str(assembly[instruction][1]) + " R" + str(assembly[instruction][2]) + " #" + str(assembly[instruction][3]) + "]"
    elif instr == 6: # BLTZ
        output = "[BLTZ\tR" + str(assembly[instruction][1]) + " Offset: " + str(assembly[instruction][2]) + "]"
    elif instr == 7: # MUL
        output = "[MUL\tR" + str(assembly[instruction][1]) + " R" + str(assembly[instruction][2]) + " R" + str(assembly[instruction][3]) + "]"
    elif instr == 8: # JR
        output = "[JR\tR" + str(assembly[instruction][1]) + "]"
    elif instr == 9: # ADD
        output = "[ADD\tR" + str(assembly[instruction][1]) + ", R" + str(assembly[instruction][2]) + ", R" + str(assembly[instruction][3]) + "]"
    elif instr == 10: # SLL
        output = "[SLL\tR" + str(assembly[instruction][1]) + " R" + str(assembly[instruction][2]) + " #" + str(assembly[instruction][3]) + "]"
    elif instr == 11: # SUB
        output = "[SUB\tR" + str(assembly[instruction][1]) + " R" + str(assembly[instruction][2]) + " R" + str(assembly[instruction][3]) + "]"
    elif instr == 12: # SRL
        output = "[SRL\tR" + str(assembly[instruction][1]) + " R" + str(assembly[instruction][2]) + " #" + str(assembly[instruction][3]) + "]"
    elif instr == 13: # AND
        output = "[AND\tR" + str(assembly[instruction][1]) + " R" + str(assembly[instruction][2]) + " R" + str(assembly[instruction][3]) + "]"
    elif instr == 14: # MOVZ
        output = "[MOVZ\tR" + str(assembly[instruction][1]) + " R" + str(assembly[instruction][2]) + " R" + str(assembly[instruction][3]) + "]"
    elif instr == 15: # OR
        output = "[OR\tR" + str(assembly[instruction][1]) + " R" + str(assembly[instruction][2]) + " R" + str(assembly[instruction][3]) + "]"
    return output

def main():
    global cycle
    dissasembler()
    cycle = 1
    while (run):
        writeToReg()
        ALU()
        postmemWrite()
        updateIss()
        fetch()
        printOutput()
        cycle += 1

assembly = []
binary = []
memory = [0] * 1000
lineCounter = 96
cycle = 1

preIssue = [-1,-1,-1,-1]
preIssue_empty = True
preIssue_full = False
preAlu = [-1,-1]
preAlu_empty = True
preAlu_full = False
postAlu = [-1,-1]
postAlu_empty = True
preMem = [-1,-1]
preMem_empty = True
preMem_full = False
postMem = [-1,-1]
postMem_empty = True
modified = False
run = True

cache = [
#   LRU     way0         way1
    [0, [0,0,0,0,0], [0,0,0,0,0]], # Set1
    [0, [0,0,0,0,0], [0,0,0,0,0]], # Set2
    [0, [0,0,0,0,0], [0,0,0,0,0]], # Set3
    [0, [0,0,0,0,0], [0,0,0,0,0]], # Set4
]
write_queue = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
queue = []
main()