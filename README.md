# Verbosity v2

Verbosity, but actually usable

This version of Verbosity aims to preserve the obscene length of Verbosity programs, while improving a number of things about the language. This rewrite and update has expanded the capabilities of Verbosity, as well as how easy it is to read/write a program. For example, the [Hello, World program](https://en.wikipedia.org/wiki/%22Hello,_World!%22_program) of Verbosity v1 was a horrible 444 bytes long:

    Include<Integer>
    Include<MetaFunctions>
    Include<Output>
    Include<String>

    Integer:DefineVariable<one; 1>
    Output:DefineVariable<STDOUT; 0>
    String:DefineVariable<string; "Hello, World!">

    String:RedefineVariable<string; String:RemoveCharactersFromStart<string; one>>
    String:RedefineVariable<string; String:TakeFirstCharacters<string; one>>

    Output:DisplayAsText<STDOUT; string>

    DefineMain<> [
        MetaFunctions:ExecuteScript<MetaFunctions@FILE>
    ]
    
However, the standard Hello, World program in version 2 is only 159 bytes:

    IncludeTypePackage<OutputSystem>
    IncludeTypePackage<StringArray>

    output = OutputSystem:NewOutput<DEFAULT>

    OutputSystem:DisplayAsText<output; "Hello, World!">
    
which is significantly more readable than the previous program.
