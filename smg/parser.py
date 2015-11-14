import ply.yacc as yacc
from lexer import SMGLexer


class SMGParser(object):
    tokens = SMGLexer.tokens

    def __init__(self):
        self.config = {
            'prefix': None,
            'env': None,
            'transitions': [],
            'state_fns': []
        }

    def p_config(self, p):
        '''config : empty
                  | config comments
                  | config declarations
                  | config transitions
                  | config env
                  | config state_fns '''
        return 1

    def p_comments(self, p):
        '''comments : COMMENT
                    | comments COMMENT'''

    def p_declarations(self, p):
        '''declarations : declaration
                        | declarations declaration'''

    def p_declaration(self, p):
        '''declaration : PREFIX '(' NAME ')' ';' '''
        self.config[p[1].lower()] = p[3]

    def p_env(self, p):
        '''env : DECLARE_ENV CCODE'''
        self.config['env'] = p[2]

    def p_state_fns(self, p):
        '''state_fns : state_fns state_fn
                     | state_fn'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_state_fn(self, p):
        '''state_fn : STATE_FN '(' NAME ')' CCODE'''
        p[0] = p[3], p[5]

    def p_transitions(self, p):
        '''transitions : TRANSITIONS transitions_body '}' '''
        self.config['transitions'] = p[2]

    def p_transitions_body(self, p):
        '''transitions_body : transitions_body transition
                            | transition'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_transition(self, p):
        '''transition : NAME TRANSITION NAME GUARD CCODEGUARD ';'
                      | NAME TRANSITION NAME ';' '''
        # Drop the semicolon
        from_state, to_state = p[1], p[3]
        if len(p) == 5:
            guard = ''
        else:
            guard = p[5]
        p[0] = (from_state, to_state, guard)

    def p_empty(self, p):
        '''empty : '''

    def p_error(self, p):
        print('ERROR', p.lineno, p.type, p.value)


def parse(txt):
    lexer = SMGLexer()
    parser = SMGParser()
    p = yacc.yacc(module=parser)
    p.parse(txt, lexer=lexer.build())
    return parser.config


if __name__ == '__main__':
    from terseparse import Parser, Arg, types
    p = Parser('parser', 'test lexer or parser on input',
        Arg('file', 'input file', types.File.r))
    _, args = p.parse_args()

    cfg = parse(args.ns.file.read())
    print(cfg)
