import ast

class SimplifyBooleanComparison(ast.NodeTransformer):

    def visit_Compare(self, node):
        self.generic_visit(node)

        if (len(node.ops) != 1):
            return node
        
        comp = node.comparators[0]
        ops = node.ops[0]
        
        if isinstance(comp, ast.Constant):
            if isinstance(ops, ast.Eq):
                if comp.value == True:
                    return ast.copy_location(node.left, node)
                elif comp.value == False:
                    new_node = ast.UnaryOp(op=ast.Not(), operand= node.left)
                    return ast.copy_location(new_node, node)

        return node
