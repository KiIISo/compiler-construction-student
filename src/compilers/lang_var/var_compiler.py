from lang_var.var_ast import *
from common.wasm import *
import lang_var.var_tychecker as var_tychecker
from common.compilerSupport import *
# import common.utils as utils

def compileModule(m: mod, cfg: CompilerConfig) -> WasmModule:
    """
    Compiles the given module.
    """
    vars = var_tychecker.tycheckModule(m)
    instrs = compileStmts(m.stmts)
    idMain = WasmId('$main')
    locals: list[tuple[WasmId, WasmValtype]] = [(identToWasmId(x), 'i64') for x in vars]
    return WasmModule(imports=wasmImports(cfg.maxMemSize),
                    exports=[WasmExport("main", WasmExportFunc(idMain))],
                    globals=[],
                    data=[],
                    funcTable=WasmFuncTable([]),
                    funcs=[WasmFunc(idMain, [], None, locals, instrs)])

def compileStmts(stmts: list[stmt]) -> list[WasmInstr]:
    instr1 = WasmInstrConst("i64", 42)
    instrcall = WasmInstrCall(WasmId("$print_i64"))
    return [instr1, instrcall]
    # for stmt in stmts:
    #     instrs.append(WasmInstrCall(identToWasmId(Ident("print"))))
    # return instrs

def compileStmt(s: stmt) -> list[WasmInstr]:
    instrs:list[WasmInstr] = []
    match s:
        case StmtExp():
            print(f'Compiling statement: {s}')
            compileExp(s.exp, instrs)
        case Assign(x, IntConst(n)):
            instrs.append(WasmInstrConst("i64", n))
            instrs.append(WasmInstrCall(identToWasmId(x)))
            print(f'Compiling assignment: {s}')
        case Assign(_,_):
            print(f'Compiling assignment: {s}')

    return instrs

def compileAssign(var: ident, right: exp):
    return compileExp(right)


def compileExp(s: exp, instrs: list[WasmInstr]):
    """
    Compiles an expression statement.
    """
    match s:
        case IntConst(n):
            instrs.append(WasmInstrConst("i64", n))
        case Name(x):
            instrs.append(WasmInstrVarLocal("get", identToWasmId(x)))
        case Call(id, args):

        case _:
            raise CompileError.typeError(f'Unsupported expression type: {type(s.exp)}')


def identToWasmId(i: ident) -> WasmId:
    """
    Converts an identifier to a WasmId.
    """
    return WasmId(f'${i.name}')
