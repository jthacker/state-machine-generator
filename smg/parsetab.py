
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.8'

_lr_method = 'LALR'

_lr_signature = 'F20A8FBFB157F0F81777EA2AF2D06A71'
    
_lr_action_items = {'COMMENT':([0,1,2,3,5,6,9,10,11,13,14,18,19,22,23,26,34,35,],[-21,3,-1,-7,-3,19,-5,-9,-6,-4,-14,-10,-8,-13,-12,-16,-11,-15,]),'NAME':([4,15,17,20,21,24,25,32,37,],[16,-18,16,27,28,29,-17,-20,-19,]),')':([27,28,],[30,31,]),'(':([7,8,],[20,21,]),'TRANSITION':([16,],[24,]),'GUARD':([29,],[33,]),'CCODEGUARD':([33,],[36,]),'PREFIX':([0,1,2,3,5,6,9,10,11,13,14,18,19,22,23,26,34,35,],[-21,7,-1,-7,7,-2,-5,-9,-6,-4,-14,-10,-8,-13,-12,-16,-11,-15,]),'DECLARE_ENV':([0,1,2,3,5,6,9,10,11,13,14,18,19,22,23,26,34,35,],[-21,12,-1,-7,-3,-2,-5,-9,-6,-4,-14,-10,-8,-13,-12,-16,-11,-15,]),';':([29,30,36,],[32,34,37,]),'TRANSITIONS':([0,1,2,3,5,6,9,10,11,13,14,18,19,22,23,26,34,35,],[-21,4,-1,-7,-3,-2,-5,-9,-6,-4,-14,-10,-8,-13,-12,-16,-11,-15,]),'}':([15,17,25,32,37,],[-18,26,-17,-20,-19,]),'CCODE':([12,31,],[23,35,]),'STATE_FN':([0,1,2,3,5,6,9,10,11,13,14,18,19,22,23,26,34,35,],[-21,8,-1,-7,-3,-2,-5,-9,8,-4,-14,-10,-8,-13,-12,-16,-11,-15,]),'$end':([0,1,2,3,5,6,9,10,11,13,14,18,19,22,23,26,34,35,],[-21,0,-1,-7,-3,-2,-5,-9,-6,-4,-14,-10,-8,-13,-12,-16,-11,-15,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'transition':([4,17,],[15,25,]),'declarations':([1,],[5,]),'comments':([1,],[6,]),'transitions_body':([4,],[17,]),'state_fn':([1,11,],[14,22,]),'env':([1,],[9,]),'declaration':([1,5,],[10,18,]),'state_fns':([1,],[11,]),'transitions':([1,],[13,]),'config':([0,],[1,]),'empty':([0,],[2,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> config","S'",1,None,None,None),
  ('config -> empty','config',1,'p_config','parser.py',17),
  ('config -> config comments','config',2,'p_config','parser.py',18),
  ('config -> config declarations','config',2,'p_config','parser.py',19),
  ('config -> config transitions','config',2,'p_config','parser.py',20),
  ('config -> config env','config',2,'p_config','parser.py',21),
  ('config -> config state_fns','config',2,'p_config','parser.py',22),
  ('comments -> COMMENT','comments',1,'p_comments','parser.py',26),
  ('comments -> comments COMMENT','comments',2,'p_comments','parser.py',27),
  ('declarations -> declaration','declarations',1,'p_declarations','parser.py',30),
  ('declarations -> declarations declaration','declarations',2,'p_declarations','parser.py',31),
  ('declaration -> PREFIX ( NAME ) ;','declaration',5,'p_declaration','parser.py',34),
  ('env -> DECLARE_ENV CCODE','env',2,'p_env','parser.py',38),
  ('state_fns -> state_fns state_fn','state_fns',2,'p_state_fns','parser.py',42),
  ('state_fns -> state_fn','state_fns',1,'p_state_fns','parser.py',43),
  ('state_fn -> STATE_FN ( NAME ) CCODE','state_fn',5,'p_state_fn','parser.py',50),
  ('transitions -> TRANSITIONS transitions_body }','transitions',3,'p_transitions','parser.py',54),
  ('transitions_body -> transitions_body transition','transitions_body',2,'p_transitions_body','parser.py',58),
  ('transitions_body -> transition','transitions_body',1,'p_transitions_body','parser.py',59),
  ('transition -> NAME TRANSITION NAME GUARD CCODEGUARD ;','transition',6,'p_transition','parser.py',66),
  ('transition -> NAME TRANSITION NAME ;','transition',4,'p_transition','parser.py',67),
  ('empty -> <empty>','empty',0,'p_empty','parser.py',77),
]