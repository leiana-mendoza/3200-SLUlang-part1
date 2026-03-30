# SLUlang

**Goal:**  Implement a new programming language starting from our calculator code

## Syntax

program: code-block

codeblock: statment | { statement-list }

statement-list: statement | statement \n statement-list

statement: NAME := expression  
  * Declares and initializes variables
  * Infer type from the type of the right-hand side

statement: NAME = expression
  * Sets the value for an existing variable

statement: NAME : type = expression
  * Declares and initializes variables
  * Uses specificed type

statement: NAME : type
  * Declares a new variable of specified type

expression : term + expression | term - expression | term

term : factor * term | factor / term | factor

factor : ( expression ) | NAME | NUMBER

## Types

You will need to figure out the syntax rules
  * int, float, bool, str, none
  * tuples, e.g. (str, int) or (int, int, int)
  * list[type], e.g list[str]
  * Functions: type -> type, e.g. (int, int) -> int

## Conditionals

statement: if ( condition ) code-block

statement: if (condition) code-block else code-block

## While loop

statement: while (condition) code-block

## Functions

Here is an example of a function:

```
plus : (x: int, y: int) -> int {
  total := x + y
  return total
}
```

Note that it's type is (int, int) -> int

Internally, functions should just be stored as their expression trees.  And evaluation should use the typical syntax ```plus(2, 3)```

## Scoping

You should use { and } to deliminate code blocks.  Any variables declared in this scope are local to it and you should not be able to declare a new variable using an existing variable name.

In functions definitions, global variables are not defined so all variables are new.

## Error checking

You should make sure everything is carefully checked for types and raise appropriate error messages

## Note

Some portions of the syntax and semantics are deliberately left vague for you to decide what is the best course of action.
