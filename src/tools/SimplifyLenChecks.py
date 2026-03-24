import ast
import copy


EMPTY=0
NON_EMPTY=1
NONE=2

#P = (len(x) OP CONST)
def transform(op, const):
    if const not in (0, 1):
        return NONE
    
    if isinstance(op, ast.Eq):
        return EMPTY if const == 0 else NONE
    
    if isinstance(op, ast.NotEq):
        return NON_EMPTY if const == 0 else NONE
        
    if isinstance(op, ast.Gt):
        return NON_EMPTY if const == 0 else NONE
    
    if isinstance(op, ast.GtE):
        return NON_EMPTY if const == 1 else NONE
    
    if isinstance(op, ast.Lt):
        return EMPTY if const == 1 else NONE

    return NONE

def is_len_call(expr):
    return (
        isinstance(expr, ast.Call)
        and isinstance(expr.func, ast.Name)
        and expr.func.id == "len"
        and len(expr.args) == 1
    )

def flip_operator(op):
    if isinstance(op, ast.Lt):
        return ast.Gt()
    if isinstance(op, ast.LtE):
        return ast.GtE()
    if isinstance(op, ast.Gt):
        return ast.Lt()
    if isinstance(op, ast.GtE):
        return ast.LtE()
    return op


def normalize_comparison(node):
    left = node.left
    right = node.comparators[0]
    op = node.ops[0]

    if not is_len_call(left) and is_len_call(right):
        node.left = right
        node.comparators = [left]
        node.ops[0] = flip_operator(op)

    return node
        

class SimplifyLenChecks(ast.NodeTransformer):
    def visit_Compare(self, node):
        self.generic_visit(node)

        if len(node.comparators) != 1:
            return node

        node = normalize_comparison(node)

        left = node.left
        right = node.comparators[0]
        op = node.ops[0]

        if is_len_call(left) and isinstance(right, ast.Constant):
            res = transform(op, right.value)
            target = left.args[0]

            if res == EMPTY:
                new_node = ast.UnaryOp(
                    op=ast.Not(),
                    operand=copy.deepcopy(target)
                )
                new_node = ast.copy_location(new_node, node)
                ast.fix_missing_locations(new_node)
                return new_node

            elif res == NON_EMPTY:
                new_node = copy.deepcopy(target)
                new_node = ast.copy_location(new_node, node)
                ast.fix_missing_locations(new_node)
                return new_node

        return node
