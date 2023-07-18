import tree_sitter
from tree_sitter import Language

# Load the Java grammar
Language.build_library(
    './build/languages.so',
    ['./tree-sitter-java']
)
JAVA_LANGUAGE = Language('./build/languages.so', 'java')
parser = tree_sitter.Parser()
parser.set_language(JAVA_LANGUAGE)

# Parse Java code and generate AST
code = """
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
"""
tree = parser.parse(bytes(code, 'utf8'))

# Get the root node of the AST
root_node = tree.root_node