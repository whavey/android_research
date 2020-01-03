#!/usr/bin/python3
import argparse
import javalang

def parse_args():
    parser = argparse.ArgumentParser(description='Parse Layout Files')
    parser.add_argument('-d','--debug', type=str, help='Turn on debug mode.')
    parser.add_argument('-l','--line', type=str, help='line to parse.')
    return parser.parse_args()

class LineParser:
    def __init__(self, *args, **kwargs):
        self.line = args[0].line
        self.debug = args[0].debug

    def _getParser(self):
        tokens = javalang.tokenizer.tokenize(self.line)
        parser = javalang.parser.Parser(tokens)
        return parser

    def getValidParsers(self):
        parsers = [
          'parse',
          'parse_annotation',
          'parse_annotation_element',
          'parse_annotation_method_or_constant_rest',
          'parse_annotation_type_body',
          'parse_annotation_type_declaration',
          'parse_annotation_type_element_declaration',
          'parse_annotation_type_element_declarations',
          'parse_annotations',
          'parse_arguments',
          'parse_array_creator_rest',
          'parse_array_dimension',
          'parse_array_initializer',
          'parse_basic_type',
          'parse_block',
          'parse_block_statement',
          'parse_catch_clause',
          'parse_catches',
          'parse_class_body',
          'parse_class_body_declaration',
          'parse_class_creator_rest',
          'parse_class_or_interface_declaration',
          'parse_compilation_unit',
          'parse_constant_declarator',
          'parse_constant_declarator_rest',
          'parse_constant_declarators_rest',
          'parse_constructor_declarator_rest',
          'parse_created_name',
          'parse_creator',
          'parse_element_value',
          'parse_element_value_array_initializer',
          'parse_element_value_pair',
          'parse_element_value_pairs',
          'parse_element_values',
          'parse_enum_body',
          'parse_enum_constant',
          'parse_enum_declaration',
          'parse_explicit_generic_invocation',
          'parse_explicit_generic_invocation_suffix',
          'parse_expression',
          'parse_expression_2',
          'parse_expression_2_rest',
          'parse_expression_3',
          'parse_expressionl',
          'parse_field_declarators_rest',
          'parse_for_control',
          'parse_for_init_or_update',
          'parse_for_var_control',
          'parse_for_var_control_rest',
          'parse_for_variable_declarator_rest'
        ]
        for parser in parsers:
            try:
                print(parser,'worked:',getattr(self._getParser(),parser)())
            except:
                continue

    def parseUIAssignment(self,line=None):
        if line:
            self.line = line
        if not self.line:
            print("No line to parse given.")
            return

        if self.debug:
            print("Parsing:",self.line)

        try:
            parser = self._getParser().parse_block_statement()
            parser2 = self._getParser().parse_expression()
        except:
            print("\nCouldnt get parser for:",self.line)
            return

        try:
            print('\nVar assigned:', parser.declarators[0].name, '\nUI ID:',parser.declarators[0].initializer.expression.arguments[0].member) #init.value.expression.arguments[0].member)
        except:
            try:
                print('\nVar assigned:', parser2.expressionl.selectors[0].member,'\n',"UI ID:",parser2.value.expression.arguments[0].member)
            except:
                print('\nUnable to parse:',self.line,'\nUsing:\n1)',parser,'\n\n2)',parser2)

        #print(self.expression)
        #init = parser.parse_statement()
        #init = parser.parse_variable_initializer()
        #print(type(init),'\n',init)
        #if type(init) == 'javalang.tree.Statement':
        #    print(
        #print(init.value.type.name, init.expressionl.member, '=', init.value.expression.arguments[0].member)

if __name__ == '__main__':
  args = parse_args()
  lp = LineParser(args)
  lp.parseUIAssignment()
