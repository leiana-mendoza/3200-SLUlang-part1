from dataclasses import dataclass

from lark import Lark, Transformer, v_args

calc_grammar = r"""
	# The top-level forms distinguish declaration, initial binding, and reassignment.
	start : expression			-> value
		| NAME ":=" expression	-> assign_value
		| NAME "=" expression	-> reassign_value
		| NAME ":" NAME "=" expression	-> declare_typed_value
		| NAME ":" NAME			-> declare_typed_variable
		
	expression : term "+" expression	-> add
		| term "-" expression			-> sub
		| term							-> value
		
	term : factor "*" term	-> mult
		| factor "/" term	-> div
		| factor			-> value

	factor : "(" expression ")"	-> value
		| NAME					-> lookup_value
		| NUMBER				-> number
		
	NAME : /[a-z]+/
	NUMBER : /[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?/

	WHITESPACE: /[ \t]+/
	%ignore WHITESPACE
"""


@dataclass
class CalcResult:
	type: str | None = None
	value: object | None = None
	error: str | None = None


@v_args(inline=True)	# Allows access to children through seperate parameters
class Calculate(Transformer):
	def __init__(self):
		# vars stores the current runtime value; declared_types stores any explicit type annotation.
		self.vars = {}
		self.declared_types = {}

	def _combine(self, expr1, expr2, op):
		if expr1.error:
			return expr1
		if expr2.error:
			return expr2
		try:
			value = op(expr1.value, expr2.value)
			return CalcResult(type=type(value).__name__, value=value, error=None)
		except Exception as exc:
			return CalcResult(type=None, value=None, error=str(exc))

	def value(self, value):
		return value

	def _declare_type(self, name, declared_type):
		if declared_type not in {"int", "float"}:
			return CalcResult(type=None, value=None, error=f"Unsupported type: {declared_type}")
		if name in self.vars:
			return CalcResult(type=None, value=None, error="Variable already exists: %s" % name)
		# A typed declaration creates the name immediately, even before it has a value.
		self.declared_types[name] = declared_type
		self.vars[name] = CalcResult(type=declared_type, value=None, error=None)
		return None

	def declare_typed_variable(self, name, declared_type):
		name = str(name)
		declared_type = str(declared_type)
		error = self._declare_type(name, declared_type)
		if error:
			return error
		return CalcResult(type=declared_type, value=None, error=None)

	def declare_typed_value(self, name, declared_type, value):
		name = str(name)
		declared_type = str(declared_type)
		error = self._declare_type(name, declared_type)
		if error:
			return error
		return self._store_value(name, value, require_existing=True)

	def _store_value(self, name, value, require_existing=False):
		if value.error:
			return value
		if require_existing and name not in self.vars:
			return CalcResult(type=None, value=None, error="Variable not found: %s" % name)
		declared_type = self.declared_types.get(name)
		# Allow integer expressions to initialize or update float variables.
		if declared_type == "float" and value.type == "int":
			value = CalcResult(type="float", value=float(value.value), error=None)
		elif declared_type is not None and value.type != declared_type:
			return CalcResult(
				type=None,
				value=None,
				error=f"Type mismatch for {name}: expected {declared_type}, got {value.type}",
			)
		self.vars[name] = CalcResult(type=value.type, value=value.value, error=None)
		return CalcResult(type=value.type, value=value.value, error=None)

	def assign_value(self, name, value):
		name = str(name)
		# := is only for introducing a new variable.
		if name in self.vars:
			return CalcResult(type=None, value=None, error="Variable already exists: %s" % name)
		return self._store_value(name, value)

	def reassign_value(self, name, value):
		return self._store_value(str(name), value, require_existing=True)

	def lookup_value(self, name):
		name = str(name)
		try:
			value = self.vars[name]
			if value.value is None:
				return CalcResult(type=value.type, value=None, error="Variable declared but not assigned: %s" % name)
			return CalcResult(type=type(value.value).__name__, value=value.value, error=None)
		except KeyError:
			return CalcResult(type=None, value=None, error="Variable not found: %s" % name)
			
	def number(self, token):
		text = str(token)
		if any(ch in text for ch in '.eE'):
			value = float(text)
		else:
			value = int(text)
		return CalcResult(type=type(value).__name__, value=value, error=None)
		
	def add(self, expr1, expr2):
		return self._combine(expr1, expr2, lambda x, y: x + y)
		
	def sub(self, expr1, expr2):
		return self._combine(expr1, expr2, lambda x, y: x - y)
		
	def mult(self, expr1, expr2):
		return self._combine(expr1, expr2, lambda x, y: x * y)
		
	def div(self, expr1, expr2):
		return self._combine(expr1, expr2, lambda x, y: x / y)


parser = Lark(calc_grammar, parser='lalr')
transformer = Calculate()

def main():
	while True:
		try:
			s = input('> ')
		except EOFError:
			break

		try:
			tree = parser.parse(s)
			print(tree.pretty())
			print(transformer.transform(tree))
		except Exception as exc:
			print(CalcResult(type=None, value=None, error=str(exc)))

if __name__ == '__main__':
	main()
