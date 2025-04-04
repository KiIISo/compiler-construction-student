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
    instrs = compileStmts(m.stmts, vars)
    idMain = WasmId('$main')
    locals: list[tuple[WasmId, WasmValtype]] = [(identToWasmId(x), 'i64') for x in vars]
    return WasmModule(imports=wasmImports(cfg.maxMemSize),
                    exports=[WasmExport("main", WasmExportFunc(idMain))],
                    globals=[],
                    data=[],
                    funcTable=WasmFuncTable([]),
                    funcs=[WasmFunc(idMain, [], None, locals, instrs)])

def compileStmts(stmts: list[stmt], vars:set[ident]) -> list[WasmInstr]:
    wasmInstrs:list[WasmInstr] = []

    for stmt in stmts:
        wasmInstrs.extend(compileStmt(stmt, vars))

    return wasmInstrs

def compileStmt(s: stmt, vars:set[ident]) -> list[WasmInstr]:
    instrs:list[WasmInstr] = []
    match s:
        case StmtExp():
            print(f'Compiling statement: {s}')
            var_tychecker.tycheckStmt(s, vars)
            instrs.extend(compileExp(s.exp))
        case Assign(var, right):
            print(f'Compiling assignment: {s}')
            var_tychecker.tycheckStmt(s, vars)
            instrs.extend(compileAssign(var, right))

    return instrs



def compileExp(s: exp) -> list[WasmInstr]:
    """
    Compiles an expression statement.
    """
    wasmInstrs:list[WasmInstr] = []
    match s:
        case IntConst(n):
            wasmInstrs.append(WasmInstrConst("i64", n))
        case Name(x):
            wasmInstrs.append(WasmInstrVarLocal("get", identToWasmId(x)))
        case Call(id, args):
            # WasmInstrCall
            for arg in args:
                wasmInstrs.extend(compileExp(arg))
            wasmInstrs.append(WasmInstrCall(WasmId(f'${id.name.split("_")[0]}_i64')))
        case BinOp(left, op, right):
            # WasmInstrNumBinOp
            wasmInstrs.extend(compileExp(left))
            wasmInstrs.extend(compileExp(right))
            
            match op:
                case Add():
                    wasmInstrs.append(WasmInstrNumBinOp("i64", "add"))
                case Sub():
                    wasmInstrs.append(WasmInstrNumBinOp('i64', 'sub'))
                case Mul():
                    wasmInstrs.append(WasmInstrNumBinOp('i64', 'mul'))

        case UnOp(op, e):
            wasmInstrs.extend(compileExp(e))
            wasmInstrs.append(WasmInstrConst('i64', -1))
            wasmInstrs.append(WasmInstrNumBinOp('i64', 'mul'))

    return wasmInstrs

def compileAssign(var: ident, right: exp) -> list[WasmInstr]:
    wasmInstrs:list[WasmInstr] = []
    wasmInstrs.extend(compileExp(right))
    wasmInstrs.append(WasmInstrVarLocal("set", identToWasmId(var)))
    return wasmInstrs

def identToWasmId(i: ident) -> WasmId:
    """
    Converts an identifier to a WasmId.
    """
    return WasmId(f'${i.name}')
