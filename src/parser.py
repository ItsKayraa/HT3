import tokens as tht

def generate_func(typ: str, name: str, params: dict):
    exitd = {
        "params": params,
        "name": name,
        "typ:": typ,
        "content": f"{name}:\n"
    }
    return exitd

def parser(tokens_nested: list):
    asm = {
        "s.before": "",
        "s.after": "",
        "s.data": "section .data\n",
        "s.text": "section .text\nglobal _start\n",
        "funcs": {
            ".": "_start:\n"
        }
    }
    
    curfunc = ""
    cvars = []

    for tokens in tokens_nested:
        i = 0
        while i < len(tokens):
            curt = tokens[i]
            ntex = tokens[i+1] if i+1 < len(tokens) else None

            # print(curt, i, ntex) <- debug

            if curt[0] == tht.T_COMMENT_LINE or curt[0] == tht.T_COMMENT_BLOCK:
                    i += 1
                    continue
            elif curt[0] == tht.T_IDENT:
                if curt[1] == "func":
                    if not ntex or ntex[0] != tht.T_IDENT:
                        print("Error: Invalid function usage")
                        return
                    ftyp = "any"
                    fnamet = ntex
                    plc = i+2
                    if ntex[1] in tht.TYPES:
                        ftyp = ntex[1]
                        fnamet = tokens[i+2]
                        if fnamet[0] != tht.T_IDENT:
                            print("Error: Invalid function name")
                            return
                        plc = i+3
                    if plc >= len(tokens) or tokens[plc][0] != tht.T_LPRM:
                        print("Error: Invalid function usage: expected param")
                        return
                    plc += 1
                    params = {}
                    while plc < len(tokens) and tokens[plc][0] != tht.T_RPRM:
                        typ_token = tokens[plc]
                        plc += 1
                        if plc >= len(tokens):
                            print("Error: Parameter name missing")
                            return
                        name_token = tokens[plc]
                        plc += 1

                        if typ_token[0] != tht.T_IDENT or name_token[0] != tht.T_IDENT:
                            print("Error: Parameter type or name invalid")
                            return

                        params[name_token[1]] = typ_token[1]

                        if plc < len(tokens) and tokens[plc][0] == tht.T_COMMA:
                            plc += 1
                    plc+=1
                    funcd = generate_func(ftyp, fnamet[1], params)
                    asm["funcs"][fnamet[1]] = funcd
                    i = plc
                    if tokens[i][0] == tht.T_LBRC:
                        curfunc = fnamet[1]
                        i+=1
                elif curt[1] == "int":
                    if not ntex or ntex[0] != tht.T_IDENT:
                        print("Error: Invalid int usage")
                        return
                    
                    namet = ntex
                    valuet = tokens[i+2]
                    if not namet or namet[0] != tht.T_IDENT:
                        print("Error: Invalid int usage: expected word name for int.")
                        return
                    if not valuet or valuet[0] != tht.T_INT:
                        print("Error: Invalid int usage: expected int value for int.")
                        return

                    asmc = f"{namet[1]} dq {valuet[1]}"
                    asm["s.data"] += asmc + "\n"
                    cvars.append(namet[1])
                    i += 3
                elif curt[1] == "eret":
                    if curfunc == "":
                        print("Error: Invalid eret usage: there is no current function.")
                        return
                    if not ntex:
                        print("Error: Invalid eret usage:expected return")
                        return
                    ecode = ntex[1]
                    if ntex[1] == tht.T_IDENT:
                        ecode = f"qword [{ntex[1]}]"
                    asmc = f"mov rax, 60\nmov rdi, [{ecode}]\nsyscall\nret\n"
                    asm["funcs"][curfunc]["content"] += asmc
                    i+=2
                elif curt[1] == "ret":
                    if curfunc == "":
                        print("Error: Invalid eret usage: there is no current function.")
                        return
                    if not ntex:
                        print("Error: Invalid eret usage:expected return")
                        return
                    ecode = ntex[1]
                    if ntex[1] == tht.T_IDENT:
                        ecode = f"qword [{ntex[1]}]"
                    asmc = f"mov rax, {ecode}"
                    asm["funcs"][curfunc]["content"] += asmc
                    i+=2
                else:
                    if curt[1] in cvars:
                        if not ntex:
                            print("Error: Unused variable name.")
                            return
                        if ntex[0] == tht.T_DOOPER:
                            if curfunc == "":
                                print("Error: Invalid double operator usage: there is no current work.")
                                return
                            if ntex[1] == "++":
                                asm["funcs"][curfunc]["content"] += f"inc dword [{curt[1]}]\n"
                            elif ntex[1] == "--":
                                asm["funcs"][curfunc]["content"] += f"dec dword [{curt[1]}]\n"
                            elif ntex[1] == "**":
                                asm["funcs"][curfunc]["content"] += f"push rax\nmov rax, [{curt[1]}]\nshl rax, 1\nmov [{curt[1]}], rax\npop rax\n"
                            elif ntex[1] == "//":
                                asm["funcs"][curfunc]["content"] += f"push rax\nmov rax, [{curt[1]}]\nshr rax, 1\nmov [{curt[1]}], rax\npop rax\n"
                            
                            elif ntex[1] == "+=":
                                if not tokens[i+1]:
                                    print("Error: Invalid double operator usage: missing other number | variable.")
                                    return
                                valt = tokens[i+2]
                                if valt[0] == tht.T_IDENT:
                                    if not valt[1] in cvars:
                                        print("Error: Invalid double operator usage: missing other number | variable.")
                                        return
                                    asm["funcs"][curfunc]["content"] += f"push rax\nmov rax, [{curt[1]}]\nadd rax, [{valt[1]}]\nmov [{curt[1]}], rax\npop rax\n"
                                elif valt[0] == tht.T_INT:
                                    asm["funcs"][curfunc]["content"] += f"add qword [{curt[1]}], {valt[1]}\n"
                                elif valt[0] == tht.T_STRING or valt[0] == tht.T_CHAST:
                                    print("Warning: the operation you gave was with int and string or character. Please consider this if you made an mistake, adding the lenght of the string or character.")
                                    asm["funcs"][curfunc]["content"] += f"add qword [{curt[1]}], {len(valt[1])}\n"
                                i+=1
                            elif ntex[1] == "-=":
                                if not tokens[i+1]:
                                    print("Error: Invalid double operator usage: missing other number | variable.")
                                    return
                                valt = tokens[i+2]
                                if valt[0] == tht.T_IDENT:
                                    if not valt[1] in cvars:
                                        print("Error: Invalid double operator usage: missing other number | variable.")
                                        return
                                    asm["funcs"][curfunc]["content"] += f"push rax\nmov rax, [{curt[1]}]\nsub rax, [{valt[1]}]\nmov [{curt[1]}], rax\npop rax\n"
                                elif valt[0] == tht.T_INT:
                                    asm["funcs"][curfunc]["content"] += f"sub qword [{curt[1]}], {valt[1]}\n"
                                elif valt[0] == tht.T_STRING or valt[0] == tht.T_CHAST:
                                    print("Warning: the operation you gave was with int and string or character. Please consider this if you made an mistake, adding the lenght of the string or character.")
                                    asm["funcs"][curfunc]["content"] += f"sub qword [{curt[1]}], {valt[1]}\n"
                                i+=1
                            elif ntex[1] == "*=":
                                if not tokens[i+1]:
                                    print("Error: Invalid double operator usage: missing other number | variable.")
                                    return
                                valt = tokens[i+2]
                                if valt[0] == tht.T_IDENT:
                                    if not valt[1] in cvars:
                                        print("Error: Invalid double operator usage: missing other number | variable.")
                                        return
                                    asm["funcs"][curfunc]["content"] += f"push rax\npush rbx\nmov rax, [{curt[1]}]\nmov rbx, [{valt[1]}]\nimul rax, rbx\nmov [{curt[1]}], rax\npop rax\npop rbx\n"
                                elif valt[0] == tht.T_INT:
                                    asm["funcs"][curfunc]["content"] += f"push rax\npush rbx\nmov rax, [{curt[1]}]\nmov rbx, [{valt[1]}]\nimul rax, rbx\nmov [{curt[1]}], rax\npop rax\npop rbx\n"
                                elif valt[0] == tht.T_STRING or valt[0] == tht.T_CHAST:
                                    print("Warning: the operation you gave was with int and string or character. Please consider this if you made an mistake, adding the lenght of the string or character.")
                                    asm["funcs"][curfunc]["content"] += f"push rax\npush rbx\nmov rax, [{curt[1]}]\nmov rbx, {len(valt[1])}\nimul rax, rbx\nmov [{curt[1]}], rax\npop rax\npop rbx\n"
                                i+=1
                            elif ntex[1] == "/=":
                                if not tokens[i+1]:
                                    print("Error: Invalid double operator usage: missing other number | variable.")
                                    return
                                valt = tokens[i+2]
                                if valt[0] == tht.T_IDENT:
                                    if not valt[1] in cvars:
                                        print("Error: Invalid double operator usage: missing other number | variable.")
                                        return
                                    asm["funcs"][curfunc]["content"] += f"push rax\npush rdx\nmov rax, [{curt[1]}]\nxor rdx, rdx\nmov rbx, [{valt[1]}]\ndiv rbx\nmov [{curt[1]}], rax\npop rdx\npop rax\n"
                                elif valt[0] == tht.T_INT:
                                    asm["funcs"][curfunc]["content"] += f"push rax\npush rdx\nmov rax, [{curt[1]}]\nxor rdx, rdx\nmov rbx, {valt[1]}\ndiv rbx\nmov [{curt[1]}], rax\npop rdx\npop rax\n"
                                elif valt[0] == tht.T_STRING or valt[0] == tht.T_CHAST:
                                    print("Warning: division by string/char is not standard. Using length as divisor.")
                                    asm["funcs"][curfunc]["content"] += f"push rax\npush rdx\nmov rax, [{curt[1]}]\nxor rdx, rdx\nmov rbx, {len(valt[1])}\ndiv rbx\nmov [{curt[1]}], rax\npop rdx\npop rax\n"
                                i+=1
                            i+=2
                        else:
                            print(f"Error: Unknown keyword: {curt[1]}")
                            return
            elif curt[0] == tht.T_RBRC:
                if curfunc == "":
                    print("Error: Invalid right bracket usage: there is no current work.")
                    return
                if curfunc == "main":
                    asm["funcs"]["."] += "call main\n"
                curfunc = ""
                i+=1
    return asm