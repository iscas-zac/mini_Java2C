import json
import javalang

def inline(body: list[javalang.parser.tree.Declaration]) -> str:
    lines = "\n".join([visit(decl) for decl in body])
    return lines

def visit(decl: javalang.parser.tree.Declaration | str) -> str:
    def chain(funcs: list[javalang.parser.tree.MethodInvocation], core: str) -> str:
        for func in funcs:
            core = "%s(%s)" % (func.member, ", ".join([core] + [visit(arg) for arg in func.arguments]))
        return core
    match decl:
        case basic if isinstance(basic, str | int | float | javalang.tokenizer.Null):
            match basic:
                case "null":
                    return "0"
                case "true":
                    return "1"
                case "false":
                    return "0"
                case "String":
                    return "String*"
                case "boolean":
                    return "bool"
                case _:
                    return str(basic)
        case javalang.parser.tree.BinaryOperation(operandl=op_l, operandr=op_r, operator=op):
            return "%s %s %s" % (visit(op_l), visit(op), visit(op_r))
        case javalang.parser.tree.MemberReference(member=memb, qualifier = qual, selectors=slts, postfix_operators=postf, prefix_operators=pref):
            return "".join(pref) + \
                visit(qual) + ("__" if qual else "") + visit(memb) + \
                    "".join("[%s]" % visit(slt.index) for slt in slts)  + \
                        "".join(postf)
        case javalang.parser.tree.Assignment(expressionl=exp, type=op, value=v):
            return visit(exp) + visit(op) + visit(v)
        case javalang.parser.tree.BlockStatement(statements=stmts):
            return inline(stmts)
        case javalang.parser.tree.StatementExpression(expression=exp):
            return visit(exp) + ";"
        case javalang.parser.tree.MethodInvocation(member=memb, arguments=args, qualifier=qual, selectors=slts):
            if memb == "println":
                return "printf(%s)" % (", ".join(visit(arg) for arg in args))
            return chain(slts,
                         "%s(%s)" % (visit(memb), ", ".join(([visit(qual)] if qual else []) + [visit(arg) for arg in args]))
                        )
        case javalang.parser.tree.Literal(value=v, selectors=slts):
            return chain(slts, visit(v))
        case javalang.parser.tree.LocalVariableDeclaration(type=ty, declarators=dcts):
            return init_visitor(ty, dcts)
        case javalang.parser.tree.VariableDeclaration(type=ty, declarators=dcts):
            return init_visitor(ty, dcts)
        case javalang.parser.tree.IfStatement(condition=cond, then_statement=then_stmt, else_statement=else_stmt):
            return "if (%s) {\n%s\n} %s" % (visit(cond), visit(then_stmt), ("else {\n%s\n}" % visit(else_stmt)) if else_stmt else "")
        case javalang.parser.tree.WhileStatement(condition=cond, body=body):
            return "while (%s) {\n%s\n}" % (visit(cond), visit(body))
        case javalang.parser.tree.ForStatement(control=ctrl, body=body):
            return "for (%s %s; %s) {\n%s\n}" % (visit(ctrl.init), visit(ctrl.condition), ", ".join(visit(upd) for upd in ctrl.update), visit(body))
        case javalang.parser.tree.ReturnStatement(expression=exp):
            return "return %s;" % visit(exp.value)
        case _:
            return ""

def init_visitor(ty: javalang.parser.tree.Type, dcts: list[javalang.parser.tree.VariableDeclarator]) -> str:
    def initializer_visitor(initializer: javalang.parser.tree.Declaration):
        if isinstance(initializer, javalang.parser.tree.ArrayInitializer):
            return "{ %s }" % ", ".join(initializer_visitor(its)
                for its in initializer.initializers)
        else:
            return visit(initializer)
    def dimension_visitor(initializer: javalang.parser.tree.Declaration):
        if isinstance(initializer, javalang.parser.tree.ArrayInitializer):
            #TODO: for now the array length is fixed to 100
            return "[100]" + max((dimension_visitor(its) for its in initializer.initializers), key=len)
        else:
            return ""
    return "%s %s;" % (visit(ty.name), ", ".join(dct.name + dimension_visitor(dct.initializer) + 
                    (("/* %s */" if ty.name == "String" else "%s") % (" = " + initializer_visitor(dct.initializer))
                        if dct.initializer else "")
                    for dct in dcts))

def format_field(field: dict):
    if isinstance(field['type'], dict):
        dims = ['[100]' if dim == -1 else '[%d]' % dim for dim in field['type']['array size']]

        return "%s %s%s;\n" % (
                                field['type']['base type'],
                                field['name'],
                                ''.join(dims)
                            )
    else:
        return "%s %s;\n" % (field['type'], field['name'])

def struct_def_inline(template: dict) -> str:
    body = ''.join([format_field(field) for field in template['fields']])
    return "typedef struct %s {\n%s} %s;\n" % (template['name'], body, template['name'])

def type_cast(ty: javalang.parser.tree.Type) -> str:
    type_name = ty.name
    base = ""
    if type_name == "int":
        base = "int"
    elif type_name == "boolean":
        base = "bool"
    else:
        base = type_name
    suffix = "".join("[]" for _ in ty.dimensions) if hasattr(ty, "dimensions") else ""
    if suffix == "" and not base == "int":
        return f"{base}* %s"
    else:
        return f"{base} %s{suffix}"
        

with open("./string_rewrite.json") as apis:
    blocks: list = json.load(apis)
    with open("SomethingToInterpret.java") as java_file, open("interpreted.c", 'w') as new_file:
        java_ast = javalang.parse.parse(java_file.read())
        if java_ast.package:
            new_file.write("// package name: " + java_ast.package.name)
        new_file.write("#include <stdbool.h>\n#include <stdio.h>\nint Integer__MAX_VALUE = 10000;\n")
        [new_file.write(struct_def_inline(block) + "\n") for block in blocks if block['type'] == "struct definition"]
        # TODO: add attrs to classes
        for ty in java_ast.types:
            new_file.write("typedef struct %s { char* annotation; } %s;\n\n" % (ty.name, ty.name))
        # bugfix: the two for, if exchanged, will result in `meth` be the same
        for ty, meth in [(ty, meth) for ty in java_ast.types for meth in ty.body]:
            new_file.write("%s %s(%s) {\n%s\n}\n" % ("void" if not meth.return_type else (type_cast(meth.return_type) % ""),
                           meth.name,
                           ", ".join(
                               [type_cast(ty) % "_this",
                                *[type_cast(param.type) % param.name for param in meth.parameters]
                                ]),
                           inline(meth.body)))
        # new_file.write(''.join([translate(blocks, stmt) for stmt in java_file.readlines()]))
