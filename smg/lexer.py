import ply.lex as lex

reserved = {
    'PREFIX': 'PREFIX',
    'DECLARE_ENV': 'DECLARE_ENV',
    'TRANSITIONS': 'TRANSITIONS',
    'STATE_FN': 'STATE_FN',
}


class SMGLexer(object):
    def build(self, **kwargs):
        return lex.lex(module=self, **kwargs)

    states = (
        ('ccode', 'exclusive'),
        ('transitions', 'inclusive'),
        ('ccodeguards', 'exclusive'),
    )

    # Checked after all other regular expressions
    literals = ['(', ')', '{', '}', ';']


    tokens = (
        'COMMENT',
        'CCODE',
        'CCODEGUARD',
        'NAME',
        'GUARD',
        'TRANSITION'
    ) + tuple(reserved.values())


    #####################
    ### INITIAL State ###
    #####################

    # Ignored characters (whitespace)
    t_ignore = " \t\n"

    # C style comments
    def t_COMMENT(self, t):
        r'(/\*(.|\n)*?\*/)|(//.*)'
        t.lexer.lineno += t.value.count('\n')

    def t_NAME(self, t):
        r'[a-zA-Z_]+'
        t.type = reserved.get(t.value, 'NAME')
        t.lexer.previous_name_token = t.type
        return t

    # Define a rule so we can track line numbers
    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def t_begin_new_state(self, t):
        r'\{'
        if t.lexer.previous_name_token == 'TRANSITIONS':
            t.lexer.begin('transitions')
        else:
            t.lexer.ccode_startpos = t.lexer.lexpos
            t.lexer.level = 1
            t.lexer.begin('ccode')


    #########################
    ### TRANSITIONS State ###
    #########################
    def t_transitions_TRANSITION(self, t):
        r'\-\>'
        t.type = 'TRANSITION'
        return t

    def t_transitions_GUARD(self, t):
        r'\:\:'
        t.type = 'GUARD'
        t.lexer.ccode_startpos = t.lexer.lexpos
        t.lexer.begin('ccodeguards')
        return t


    ########################
    ### CODEGUARDS State ###
    ########################
    def t_ccodeguards_SEMICOLON(self, t):
        r';'
        t.type = 'CCODEGUARD'
        t.value = t.lexer.lexdata[t.lexer.ccode_startpos:t.lexpos]
        t.lexer.lineno += t.value.count('\n')
        t.lexer.begin('transitions')
        t.lexer.lexpos -= 1
        return t

    # Ignore comments
    def t_ccodeguards_comment(self, t):
        r'(/\*(.|\n)*?\*/)|(//.*)'

    # C strings
    def t_ccodeguards_string(self, t):
        r'\"([^\\\n]|(\\.))*?\"'

    # C character literal
    def t_ccodeguards_char(self, t):
        r'\'([^\\\n]|(\\.))*?\''

    # Any sequence of non-whitespace characters (not braces, strings, semicolon)
    def t_ccodeguards_nonspace(self, t):
        r'[^\s;\{\}\'\"]+'

    # Ignored characters (whitespace)
    t_ccodeguards_ignore = " \t\n"

    def t_ccodeguards_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)


    ###################
    ### CCODE State ###
    ###################

    # Keep track of brace nesting level
    def t_ccode_LBRACE(self, t):
        r'\{'
        t.lexer.level += 1

    def t_ccode_RBRACE(self, t):
        r'\}'
        t.lexer.level -= 1
        # Record entire block of c-code after closing brace is found
        if t.lexer.level == 0:
            txt = t.lexer.lexdata[t.lexer.ccode_startpos:t.lexer.lexpos]
            t.value = txt[:-1]
            t.lexer.lineno += txt.count('\n')
            t.type = 'CCODE'
            t.lexer.begin('INITIAL')
            return t

    # Ignore comments
    def t_ccode_comment(self, t):
        r'(/\*(.|\n)*?\*/)|(//.*)'
        pass

    # C strings
    def t_ccode_string(self, t):
        r'\"([^\\\n]|(\\.))*?\"'

    # C character literal
    def t_ccode_char(self, t):
        r'\'([^\\\n]|(\\.))*?\''

    # Any sequence of non-whitespace characters (not braces, strings)
    def t_ccode_nonspace(self, t):
        r'[^\s\{\}\'\"]+'

    # Ignored characters (whitespace)
    t_ccode_ignore = " \t\n"

    # For bad characters, we just skip over it
    def t_ccode_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)
