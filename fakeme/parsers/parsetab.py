
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'COMMA CREATE DECIMAL DOUBLE ELSE EXISTS FLOAT ID IF INT INTEGER NEWLINE NOT SMALLINT STRING TABLE THEN TINYINT USE WHILEexpr : CREATE TABLE IF NOT EXISTS ID\n                | CREATE TABLE IF NOT EXISTS ID ID\n                | CREATE TABLE ID\n\n        expr : ID STRING\n                | ID INTEGER\n                | ID INT\n                | ID DOUBLE\n                | ID FLOAT\n                | ID SMALLINT\n                | ID DECIMAL INT\n                | ID DECIMAL INT INT\n                | ID\n        '
    
_lr_action_items = {'CREATE':([0,],[2,]),'ID':([0,4,17,18,],[3,13,18,19,]),'$end':([1,3,5,6,7,8,9,10,13,14,16,18,19,],[0,-12,-4,-5,-6,-7,-8,-9,-3,-10,-11,-1,-2,]),'TABLE':([2,],[4,]),'STRING':([3,],[5,]),'INTEGER':([3,],[6,]),'INT':([3,11,14,],[7,14,16,]),'DOUBLE':([3,],[8,]),'FLOAT':([3,],[9,]),'SMALLINT':([3,],[10,]),'DECIMAL':([3,],[11,]),'IF':([4,],[12,]),'NOT':([12,],[15,]),'EXISTS':([15,],[17,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'expr':([0,],[1,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> expr","S'",1,None,None,None),
  ('expr -> CREATE TABLE IF NOT EXISTS ID','expr',6,'p_expression_table_name','ddl.py',71),
  ('expr -> CREATE TABLE IF NOT EXISTS ID ID','expr',7,'p_expression_table_name','ddl.py',72),
  ('expr -> CREATE TABLE ID','expr',3,'p_expression_table_name','ddl.py',73),
  ('expr -> ID STRING','expr',2,'p_expression_type','ddl.py',79),
  ('expr -> ID INTEGER','expr',2,'p_expression_type','ddl.py',80),
  ('expr -> ID INT','expr',2,'p_expression_type','ddl.py',81),
  ('expr -> ID DOUBLE','expr',2,'p_expression_type','ddl.py',82),
  ('expr -> ID FLOAT','expr',2,'p_expression_type','ddl.py',83),
  ('expr -> ID SMALLINT','expr',2,'p_expression_type','ddl.py',84),
  ('expr -> ID DECIMAL INT','expr',3,'p_expression_type','ddl.py',85),
  ('expr -> ID DECIMAL INT INT','expr',4,'p_expression_type','ddl.py',86),
  ('expr -> ID','expr',1,'p_expression_type','ddl.py',87),
]
