import ast
import pathlib
from ast import ClassDef, Import, ImportFrom
from collections import defaultdict

import astor


def generate_r4b(schema: dict, codegen_result: str):
    print("running generate_r4b")
    print(schema["definitions"].keys())
    generated_schema_file = pathlib.Path(__file__).parent / "r4b.py"
    with open(generated_schema_file, "r") as f:
        data = f.read()
    r4_ast = ast.parse(data)
    # get all imports
    parse_result = parse_ast(r4_ast)
    print(parse_result)
    grouped_clases = group_classes(parse_result["classes"])
    print(grouped_clases)


def parse_ast(ast_node: ast.Module) -> dict:
    parse_result = {
        "imports": [],
        "classes": [],
        "functions": [],
        "function_calls": [],
    }

    for node in ast_node.body:
        if _is_import(node):
            parse_result["imports"].append(node)
        elif isinstance(node, ClassDef):
            parse_result["classes"].append(node)
        elif isinstance(node, ast.FunctionDef):
            parse_result["functions"].append(node)
        elif isinstance(node, ast.Expr):
            parse_result["function_calls"].append(node)
    return parse_result


def group_classes(ast_nodes: list[ast.ClassDef]):
    classes = defaultdict(list)
    for node in ast_nodes:
        print(node.name)
        keys = classes.keys()
        print(keys)
        for key in keys:
            if node.name in key:
                classes[key].append(node)
                break
            else:
                classes[node.name].append(node)
    return classes


def ast_to_source(ast_nodes: list[ast.AST]):
    source_code = ""
    for node in ast_nodes:
        source_code += astor.to_source(node) + "\n"
    return source_code


def _get_imports(ast_node: ast.Module):
    imports = [node for node in ast_node.body if _is_import(node)]
    return imports


def _is_import(node: ast.AST):
    return isinstance(node, Import) or isinstance(node, ImportFrom)


if __name__ == "__main__":
    generate_r4b({}, "")
