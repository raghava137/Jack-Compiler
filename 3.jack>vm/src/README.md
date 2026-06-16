# DA2304 Assignment 3

## Running the compiler

Pass a .jack file directly:

```
python JackCompiler.py Conv.jack
python JackCompiler.py Main.jack
```

Or pass a folder containing .jack files and it compiles all of them.

Each run produces four files: a token XML (ConvT.xml), a parse tree XML (Conv.xml), and the VM output (Conv.vm), same pattern for Main.

## Pipeline

Feed Conv.vm and Main.vm into the Assignment 2 VM translator to get Hack assembly, then run on the CPU emulator.

## File breakdown

JackTokenizer.py strips comments and whitespace, then walks the source character by character to produce typed tokens. Also writes the T.xml file.

SymbolTable.py tracks two scopes, class-level and subroutine-level, with separate counters per kind.

VMWriter.py thin wrapper that writes VM instructions to a file.

CompilationEngine.py recursive descent parser over the token list. Builds XML as it goes and emits VM instructions at the right points.

JackCompiler.py entry point, wires the above together.

## Filter

Sobel-Y edge detection kernel used:
-1 -2 -1
 0  0  0
 1  2  1

stride = 1
