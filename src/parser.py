import tokens as tht
import lexer
from pathlib import Path

def generate_func(typ: str, name: str, params: dict):
    exitd = {
        "params": params,
        "name": name,
        "typ:": typ,
        "content": f"{name}:\n"
    }
    return exitd

def generate_func_call(asm, curfunc, func_name, args):
    if func_name in asm["funcs"]:
        num_params = len(asm["funcs"][func_name]["params"])
        if len(args) < num_params:
            print(f"Error: function '{func_name}' expects {num_params} args but got {len(args)}")
            return

    code = ""
    stack_args = []

    for i, arg in enumerate(args):
        val_type, val_name = arg
        if i < 6:
            if val_type == "int" or val_type == "var":
                code += f"mov {tht.PARAM_REGS[i]}, [{val_name}]\n"
            elif val_type == "imm":
                code += f"mov {tht.PARAM_REGS[i]}, {val_name}\n"
        else:
            stack_args.insert(0, arg)

    for arg in stack_args:
        val_type, val_name = arg
        if val_type == "int" or val_type == "var":
            code += f"push qword [{val_name}]\n"
        elif val_type == "imm":
            code += f"push qword {val_name}\n"

    code += f"call {func_name}\n"

    if stack_args:
        code += f"add rsp, {len(stack_args)*8}\n"

    asm["funcs"][curfunc]["content"] += code

def parser(tokens_nested: list, script_path):
    asm = {
        "s.before": "",
        "s.after": "",
        "s.data": "section .data\n",
        "s.text": "section .text\nglobal _start\n",
        "funcs": {
            ".": {"name": ".", "content": "_start:\n", "params": {}, "typ": "none"}
        }
    }
    
    curfunc = ""
    cvars = []
    svars = []

    for tokens in tokens_nested:
        i = 0
        while i < len(tokens):
            curt = tokens[i]
            ntex = tokens[i+1] if i+1 < len(tokens) else None

            # print(curt, i, ntex) # <- debug

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
                elif curt[1] == "printl":
                    if not ntex or (ntex[0] != tht.T_IDENT or ntex[0] != tht.T_STRING):
                        print("Error: Invalid printl usage: expected string or variable after printl.")
                        return
                    
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
                elif curt[1] == "intf":
                    namet = ntex
                    if namet[0] != tht.T_IDENT:
                        print("Error: Invalid intf variable name")
                        return
                    asm["s.data"] += f"{namet[1]} dq 0\n"
                    cvars.append(namet[1])

                    func_call_tok = tokens[i+2]
                    if func_call_tok[0] != tht.T_IDENT:
                        print("Error: Expected function name after intf variable")
                        return
                    func_name = func_call_tok[1]

                    args = []
                    j = i + 3
                    if j < len(tokens) and tokens[j][0] == tht.T_LPRM:
                        j += 1
                        while j < len(tokens) and tokens[j][0] != tht.T_RPRM:
                            t = tokens[j]
                            if t[0] == tht.T_INT:
                                args.append(("imm", t[1]))
                            elif t[0] == tht.T_IDENT:
                                if t[1] in cvars or t[1] in svars:
                                    args.append(("var", t[1]))
                                else:
                                    print(f"Error: Unknown variable '{t[1]}' used as argument")
                                    return
                            j += 1
                            if j < len(tokens) and tokens[j][0] == tht.T_COMMA:
                                j += 1
                        j += 1

                    generate_func_call(asm, curfunc, func_name, args)
                    asm["funcs"][curfunc]["content"] += f"mov [{namet[1]}], rax\n"

                    i = j
                elif curt[1] == "str":
                    if not ntex or ntex[0] != tht.T_IDENT:
                        print("Error: Invalid str usage")
                        return
                    
                    namet = ntex
                    valuet = tokens[i+2]
                    if not namet or namet[0] != tht.T_IDENT:
                        print("Error: Invalid str usage: expected word name for str.")
                        return
                    if not valuet or valuet[0] != tht.T_STRING:
                        print("Error: Invalid str usage: expected string value for str.")
                        return

                    asmc = f'{namet[1]} db "{valuet[1]}"'
                    asm["s.data"] += asmc + "\n"
                    svars.append(namet[1])
                    i += 3
                elif curt[1] == "asm":
                    if curfunc == "":
                        print("Error: Invalid asm usage: expected to be inside a function.")
                        return
                    if not ntex or ntex[0] != tht.T_STRING:
                        print("Error: Invalid asm usage: expected string after asm.")
                        return
                    asm["funcs"][curfunc]["content"] += ntex[1] + "\n"
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
                        print("Error: Invalid ret usage: there is no current function.")
                        return
                    if not ntex:
                        print("Error: Invalid ret usage: expected return value")
                        return

                    def resolve_operand(tok):
                        if tok[0] == tht.T_INT:
                            return ('imm', tok[1])
                        if tok[0] == tht.T_IDENT:
                            name = tok[1]
                            params = asm["funcs"][curfunc]["params"]
                            if name in params:
                                idx = list(params.keys()).index(name)
                                return ('reg', tht.PARAM_REGS[idx])
                            if name in cvars or name in svars:
                                return ('mem', f"[{name}]")
                            print(f"Error: unknown symbol '{name}' in return")
                            return (None, None)
                        print(f"Error: unsupported return token type: {tok}")
                        return (None, None)
                    j = i + 1
                    lhs_tok = tokens[j]
                    j += 1

                    op_tok = None
                    rhs_tok = None
                    if j < len(tokens) and tokens[j][1] in ("+", "-", "*", "/"):
                        op_tok = tokens[j][1]
                        j += 1
                        if j >= len(tokens):
                            print("Error: incomplete binary expression in return")
                            return
                        rhs_tok = tokens[j]
                        j += 1

                    asm_code = ""

                    if rhs_tok is None:
                        kind, val = resolve_operand(lhs_tok)
                        if kind is None:
                            return
                        if kind == 'reg':
                            asm_code += f"mov rax, {val}\n"
                        elif kind == 'mem':
                            asm_code += f"mov rax, {val}\n"
                        elif kind == 'imm':
                            asm_code += f"mov rax, {val}\n"
                    else:
                        k1, v1 = resolve_operand(lhs_tok)
                        k2, v2 = resolve_operand(rhs_tok)
                        if k1 is None or k2 is None:
                            return
                        if k1 == 'reg':
                            asm_code += f"mov rax, {v1}\n"
                        elif k1 == 'mem':
                            asm_code += f"mov rax, {v1}\n"
                        else:
                            asm_code += f"mov rax, {v1}\n"

                        if op_tok == "+":
                            if k2 == 'reg':
                                asm_code += f"add rax, {v2}\n"
                            elif k2 == 'mem':
                                asm_code += f"add rax, {v2}\n"
                            else:
                                asm_code += f"add rax, {v2}\n"
                        elif op_tok == "-":
                            if k2 == 'reg':
                                asm_code += f"sub rax, {v2}\n"
                            elif k2 == 'mem':
                                asm_code += f"sub rax, {v2}\n"
                            else:
                                asm_code += f"sub rax, {v2}\n"
                        elif op_tok == "*":
                            if k2 == 'reg':
                                asm_code += f"imul rax, {v2}\n"
                            elif k2 == 'mem':
                                asm_code += f"mov rbx, {v2}\nimul rax, rbx\n"
                            else:
                                asm_code += f"imul rax, {v2}\n"
                        elif op_tok == "/":
                            if k2 == 'reg':
                                asm_code += f"mov rbx, {v2}\n"
                            elif k2 == 'mem':
                                asm_code += f"mov rbx, {v2}\n"
                            else:
                                asm_code += f"mov rbx, {v2}\n"
                            asm_code += "xor rdx, rdx\n"
                            asm_code += "div rbx\n"
                        else:
                            print(f"Error: unsupported operator '{op_tok}'")
                            return

                    asm_code += "ret\n"
                    asm["funcs"][curfunc]["content"] += asm_code
                    i = j
                elif curt[1] == "get":
                    if not ntex or (ntex[0] != tht.T_STRING and ntex[0] != tht.T_IDENT):
                        print("Error: expected string library name after get or d and string")
                        return

                    if ntex[0] == tht.T_IDENT and ntex[1] == "d":
                        if not tokens[i+2] or tokens[i+2][0] != tht.T_STRING:
                            print("Error: expected string library name after d")
                            return
                        lib_path = Path(script_path).parent.parent / "lib" / tokens[i+2][1]
                        i += 3
                    else:
                        lib_path = ntex[1]
                        i += 2

                    try:
                        with open(lib_path) as lib:
                            content = lib.read()
                            tokenslib, error, errors = lexer.lmain(content)
                            ret = parser(tokenslib, script_path)

                            asm["s.data"] += ret["s.data"]
                            asm["s.text"] += ret["s.text"]
                            asm["s.after"] += ret["s.after"]
                            asm["s.before"] += ret["s.before"]
                            for func, value in ret["funcs"].items():
                                asm["funcs"][func] = value
                    except Exception as e:
                        print("Error: ", e)
                        return
                    
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
                            if curt[1] in asm["funcs"]:
                                func_name = curt[1]

                                args = []
                                j = i + 1
                                if j < len(tokens) and tokens[j][0] == tht.T_LPRM:
                                    j += 1
                                    while j < len(tokens) and tokens[j][0] != tht.T_RPRM:
                                        t = tokens[j]
                                        if t[0] == tht.T_INT:
                                            args.append({"type": "imm", "value": t[1]})
                                        elif t[0] == tht.T_IDENT:
                                            if t[1] in cvars or t[1] in svars:
                                                args.append({"type": "var", "value": t[1]})
                                            else:
                                                print(f"Error: Unknown variable '{t[1]}' used as argument")
                                                return
                                        j += 1
                                        if j < len(tokens) and tokens[j][0] == tht.T_COMMA:
                                            j += 1
                                    j += 1

                                generate_func_call(asm, curfunc, func_name, args)

                                i = j
                            else:
                                print(f"Error: Unknown keyword: {curt[1]}")
                                return
            elif curt[0] == tht.T_RBRC:
                if curfunc == "":
                    print("Error: Invalid right bracket usage: there is no current work.")
                    return
                if curfunc == "main":
                    asm["funcs"]["."]["content"] += "call main\n"
                curfunc = ""
                i+=1
    return asm