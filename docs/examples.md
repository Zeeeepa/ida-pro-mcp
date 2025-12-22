# Examples

This document provides examples of how to use IDA Pro MCP for various reverse engineering tasks.

## Basic Analysis

### Getting Information About a Binary

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>get_metadata</tool_name>
<arguments></arguments>
</use_mcp_tool>
```

Example output:
```json
{
  "module": "crackme.exe",
  "path": "C:\\Users\\user\\Desktop\\crackme.exe",
  "architecture": "x86_64",
  "compiler": "Visual C++",
  "base_address": "0x140000000",
  "entry_point": "0x140001000"
}
```

### Listing Functions

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>list_functions</tool_name>
<arguments>
{
  "offset": 0,
  "count": 5
}
</arguments>
</use_mcp_tool>
```

Example output:
```json
[
  {
    "address": "0x140001000",
    "name": "main",
    "size": 128
  },
  {
    "address": "0x140001080",
    "name": "sub_140001080",
    "size": 64
  },
  {
    "address": "0x1400010C0",
    "name": "sub_1400010C0",
    "size": 96
  },
  {
    "address": "0x140001120",
    "name": "sub_140001120",
    "size": 48
  },
  {
    "address": "0x140001150",
    "name": "sub_140001150",
    "size": 80
  }
]
```

### Decompiling a Function

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>decompile_function</tool_name>
<arguments>
{
  "address": "0x140001000"
}
</arguments>
</use_mcp_tool>
```

Example output:
```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  char v4[256]; // [rsp+20h] [rbp-118h] BYREF

  printf("Enter password: ");
  scanf("%s", v4);
  if ( check_password(v4) )
    puts("Correct password!");
  else
    puts("Wrong password!");
  return 0;
}
```

## Enhancing Code Readability

### Renaming Functions

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>rename_function</tool_name>
<arguments>
{
  "function_address": "0x1400010C0",
  "new_name": "check_password"
}
</arguments>
</use_mcp_tool>
```

### Setting Function Prototypes

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>set_function_prototype</tool_name>
<arguments>
{
  "function_address": "0x1400010C0",
  "prototype": "bool check_password(const char *password)"
}
</arguments>
</use_mcp_tool>
```

### Renaming Local Variables

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>rename_local_variable</tool_name>
<arguments>
{
  "function_address": "0x140001000",
  "old_name": "v4",
  "new_name": "password_buffer"
}
</arguments>
</use_mcp_tool>
```

### Setting Variable Types

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>set_local_variable_type</tool_name>
<arguments>
{
  "function_address": "0x140001000",
  "variable_name": "password_buffer",
  "new_type": "char[256]"
}
</arguments>
</use_mcp_tool>
```

### Adding Comments

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>set_comment</tool_name>
<arguments>
{
  "address": "0x140001020",
  "comment": "This is where the password is read from the user"
}
</arguments>
</use_mcp_tool>
```

## Advanced Analysis

### Defining Custom Types

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>declare_c_type</tool_name>
<arguments>
{
  "c_declaration": "struct user_data { char username[32]; char password[32]; int access_level; };"
}
</arguments>
</use_mcp_tool>
```

### Finding Cross-References

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>get_xrefs_to</tool_name>
<arguments>
{
  "address": "0x1400010C0"
}
</arguments>
</use_mcp_tool>
```

Example output:
```json
[
  {
    "from": "0x140001030",
    "to": "0x1400010C0",
    "type": "call"
  }
]
```

### Converting Numbers

```
<use_mcp_tool>
<server_name>github.com/mrexodia/ida-pro-mcp</server_name>
<tool_name>convert_number</tool_name>
<arguments>
{
  "text": "0x41424344",
  "size": 32
}
</arguments>
</use_mcp_tool>
```

Example output:
```json
{
  "decimal": "1094861636",
  "hex": "0x41424344",
  "binary": "01000001010000100100001101000100",
  "ascii": "ABCD",
  "signed": "1094861636"
}
```

## Complete Analysis Example

Here's a complete example of analyzing a simple crackme:

1. **Get metadata about the binary**:
   ```
   <use_mcp_tool>
   <server_name>github.com/mrexodia/ida-pro-mcp</server_name>
   <tool_name>get_metadata</tool_name>
   <arguments></arguments>
   </use_mcp_tool>
   ```

2. **List the functions**:
   ```
   <use_mcp_tool>
   <server_name>github.com/mrexodia/ida-pro-mcp</server_name>
   <tool_name>list_functions</tool_name>
   <arguments>
   {
     "offset": 0,
     "count": 10
   }
   </arguments>
   </use_mcp_tool>
   ```

3. **Decompile the main function**:
   ```
   <use_mcp_tool>
   <server_name>github.com/mrexodia/ida-pro-mcp</server_name>
   <tool_name>decompile_function</tool_name>
   <arguments>
   {
     "address": "0x140001000"
   }
   </arguments>
   </use_mcp_tool>
   ```

4. **Rename the password checking function**:
   ```
   <use_mcp_tool>
   <server_name>github.com/mrexodia/ida-pro-mcp</server_name>
   <tool_name>rename_function</tool_name>
   <arguments>
   {
     "function_address": "0x1400010C0",
     "new_name": "check_password"
   }
   </arguments>
   </use_mcp_tool>
   ```

5. **Set the function prototype**:
   ```
   <use_mcp_tool>
   <server_name>github.com/mrexodia/ida-pro-mcp</server_name>
   <tool_name>set_function_prototype</tool_name>
   <arguments>
   {
     "function_address": "0x1400010C0",
     "prototype": "bool check_password(const char *password)"
   }
   </arguments>
   </use_mcp_tool>
   ```

6. **Decompile the password checking function**:
   ```
   <use_mcp_tool>
   <server_name>github.com/mrexodia/ida-pro-mcp</server_name>
   <tool_name>decompile_function</tool_name>
   <arguments>
   {
     "address": "0x1400010C0"
   }
   </arguments>
   </use_mcp_tool>
   ```

7. **Add comments to explain the algorithm**:
   ```
   <use_mcp_tool>
   <server_name>github.com/mrexodia/ida-pro-mcp</server_name>
   <tool_name>set_comment</tool_name>
   <arguments>
   {
     "address": "0x1400010D0",
     "comment": "XOR each character with 0x42 and compare with hardcoded values"
   }
   </arguments>
   </use_mcp_tool>
   ```

8. **Rename local variables for clarity**:
   ```
   <use_mcp_tool>
   <server_name>github.com/mrexodia/ida-pro-mcp</server_name>
   <tool_name>rename_local_variable</tool_name>
   <arguments>
   {
     "function_address": "0x1400010C0",
     "old_name": "v2",
     "new_name": "password_length"
   }
   </arguments>
   </use_mcp_tool>
   ```

9. **Analyze the algorithm and determine the password**:
   ```
   <use_mcp_tool>
   <server_name>github.com/mrexodia/ida-pro-mcp</server_name>
   <tool_name>convert_number</tool_name>
   <arguments>
   {
     "text": "0x73",
     "size": 8
   }
   </arguments>
   </use_mcp_tool>
   ```

10. **Document your findings**:
    ```
    The password is "secret123". The algorithm XORs each character with 0x42 and compares the result with hardcoded values.
    ```
