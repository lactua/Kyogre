import base64
from io import BytesIO
from random import choice, choices, randint
from string import ascii_letters, digits
from tokenize import TokenInfo, tokenize, untokenize
from zlib import compress


key_comp = ascii_letters + digits

def getRandomEncode(content):
    encodes = ['b85', 'b64', 'b32', 'b16']
    encode = choice(encodes)

    encoded_content = getattr(base64, encode+'encode')(content.encode()).decode()
    
    return encode, encoded_content

def editToken(token, **kwargs):
    parameters = {
        'type': token.type,
        'string': token.string,
        'start': token.start,
        'end': token.end,
        'line': token.line
    }
    
    parameters.update(kwargs)
    
    return TokenInfo(**parameters)

def obfuscate(code):
    code_encode, encoded_code = getRandomEncode(code)
    
    key = ''.join(choices(key_comp, k=len(encoded_code)))
    condition_var = ''.join(choices(key_comp, k=randint(10,15)))
    
    encrypted_code = '.'.join([oct(ord(x)+ord(y)).removeprefix('0o') for x,y in zip(encoded_code, key)])
    
    code = """globals()['{}']=eval('__builtins__.compile == compile == __import__("builtins").compile and __builtins__.compile.__module__ == "builtins" and __builtins__.compile.__name__ == "compile" and __builtins__.compile("x","<string>","exec").__class__.__name__=="code"');exec(compile(getattr(__import__('base64'),'{}decode')(''.join(['' if not globals()['{}'] else chr(int(x,8)-ord('{}'[i]))for i,x in enumerate('{}'.split('.'))if globals()['{}'] and globals()['{}']])),'<string>','exec'));eval("del {}")""".format(
        condition_var,
        code_encode,
        condition_var,
        key,
        encrypted_code,
        condition_var,
        condition_var,
        condition_var
    )
    
    tokens = list(tokenize(BytesIO(code.encode()).readline))
    
    copy = tokens.copy()
    for index, token in enumerate(copy):
        if token.type == 1 and hasattr(__builtins__, token.string):
            new_string = "getattr(__builtins__,'{}')".format(token.string)
            tokens[index] = editToken(token, string=new_string)
            
    code = untokenize(tokens).decode()
    tokens = list(tokenize(BytesIO(code.encode()).readline))
    
    copy = tokens.copy()
    for index, token in enumerate(copy):
        if token.type == 3:
            string = token.string.removeprefix("'").removesuffix("'")
            string_encode, encoded_string = getRandomEncode(string)
            compressed_string = compress(encoded_string.encode())
            new_string = "getattr(getattr(getattr(__builtins__,'__import__')('base64'),'{}decode')(getattr(getattr(__builtins__,'__import__')('zlib'),'decompress')({})),'decode')()".format(string_encode, compressed_string)
            tokens[index] = editToken(token, string=new_string)
            
    obfuscated_code = untokenize(tokens)
    compressed_code = compress(obfuscated_code)
    obfuscated_code = "getattr(__builtins__,'exec')(getattr(getattr(__builtins__,'__import__')('zlib'),'decompress')({}))".format(compressed_code)
    
    return obfuscated_code