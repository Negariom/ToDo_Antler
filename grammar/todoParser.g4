grammar todoParser;

program
	: (line)* EOF
	;

line
	: command NEWLINE?
	| NEWLINE
	;

command
	: ADD STRING #addCommand
	| DONE INT #doneCommand
	| DELETE INT #deleteCommand
	| LIST #listCommand
    ;

ADD: 'ADD';
DONE: 'DONE';
DELETE: 'DELETE';
LIST: 'LIST';

INT: [0-9]+;

STRING
	: '"' (~["\\\r\n])* '"'
	;


NEWLINE
	: '\r'? '\n'
	;

WS
	: [ \t]+ -> skip
	;

COMMENT
	: '#' ~[\r\n]* -> skip
	;

