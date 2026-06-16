# Jack-Compiler

A multi-stage compiler toolchain built as part of the Nand2Tetris project, translating high-level **Jack** source code all the way down to **binary machine code**, through three sequential stages.

## Pipeline Overview

```
Jack (.jack) → VM (.vm) → Assembly (.asm) → Binary (.hack)
```

## Project Structure

### `1.Asm>binary`
Contains a Python script (in `src`) that translates Hack **assembly (.asm)** files into **binary (.hack)** machine code, the final stage executable by the Hack hardware platform.

### `2.vm>asm`
Contains a Python script (in `src`) that translates **VM (.vm)** code into Hack **assembly (.asm)** code, implementing the VM specification (stack operations, memory segments, branching, and function calls).

### `3.jack>vm`
Contains a Python script (in `src`) that compiles **Jack (.jack)** source files into **VM (.vm)** code, handling lexical analysis, parsing, and code generation for the Jack language.

## Usage

Each stage can be run independently, taking the output of the previous stage as input:

1. Compile Jack source to VM code using the script in `3.jack>vm/src`
2. Translate VM code to Hack assembly using the script in `2.vm>asm/src`
3. Assemble Hack assembly into binary using the script in `1.Asm>binary/src`

## About

This project follows the **Nand2Tetris** course structure, building a complete compiler and translator chain from a high-level object-based language down to machine code that can run on the Hack computer architecture.
