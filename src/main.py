import parser
import lexer
import argparse
import os

def write_asm_file(asm: dict, filename: str):
    with open(filename, "w") as f:
        f.write(asm.get("s.data", "") + "\n")
        f.write(asm.get("s.bss", "") + "\n")
        f.write(asm.get("s.text", "") + "\n")

        for fname, fdata in asm.get("funcs", {}).items():
            if isinstance(fdata, str):
                f.write(f"\n; function {fname}\n")
                f.write(fdata + "\n")
            elif isinstance(fdata, dict):
                f.write(f"\n; function {fdata.get('name', fname)}\n")
                f.write(fdata.get("content", "") + "\n")

def compile(content, output, noW, L, kt):
    tokens, error, errors = lexer.lmain(content)
    asmd   = parser.parser(tokens)
    write_asm_file(asmd, output+".s")
    os.system(f"nasm -felf64 {output+".s"} -o {output+".o"}")
    os.system(f"ld {output+".o"} {L} -o {output}")
    if error:
        print("Errors happened while compiling:\n", "\n".join(errors))
    if not kt:
        os.system(f"rm -f {output+".s"} {output+".o"}")

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('file', help='Input file')
    parser.add_argument('-o', metavar='file', help='Output file', type=str)
    parser.add_argument('-Wunused', action='store_true', help='Enable unused warning')
    parser.add_argument('-s', metavar='content', help='Content string', type=str)
    parser.add_argument('-L', metavar='content', help='Linker commands', type=str)
    parser.add_argument('-kt', action='store_true', help='Don\'t delete the temporary files')

    args = parser.parse_args()

    o = args.o
    f = args.file
    s = args.s
    L = args.L
    kt = args.kt
    noW = [args.Wunused]

    if o == None:
        o = "a.out"
    if L == None:
        L = ""

    if s != None:
        compile(s, o, noW, L, kt)
    else:
        with open(f) as file:
            compile(file.read(), o, noW, L, kt)
            file.close()
    
    return 0

if __name__ == "__main__":
    main()