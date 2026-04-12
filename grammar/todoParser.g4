grammar todoParser;

options { caseInsensitive = true; }

program
	: (line)* EOF
	;

line
	: command NEWLINE?
	| NEWLINE
	;

command
	: ADD STRING priority? deadline? depends? note? #addCommand
	| DONE INT #doneCommand
	| DELETE INT #deleteCommand
	| LIST listView? #listCommand
	| NOTE INT STRING #noteCommand
    ;

priority
    : PRIORITY (LOW | MEDIUM | HIGH)
    ;

deadline
    : DEADLINE DATE
    ;

depends
    : DEPENDS ON INT (',' INT)*
    ;

note
    : NOTE STRING
    ;

listView
    : ALL | DONE | DEPENDENCIES
    ;

ADD: 'ADD';
DONE: 'DONE';
DELETE: 'DELETE';
LIST: 'LIST';
NOTE: 'NOTE';

PRIORITY: 'PRIORITY';
LOW: 'LOW';
MEDIUM: 'MEDIUM';
HIGH: 'HIGH';

DEADLINE: 'DEADLINE';
DATE: [0-9][0-9][0-9][0-9] '-' [0-9][0-9] '-' [0-9][0-9];

DEPENDS: 'DEPENDS';
ON: 'ON';

ALL: 'ALL';
DEPENDENCIES: 'DEPENDENCIES';

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
