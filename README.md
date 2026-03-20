This tools allow you to extract assets from Ginga no Sannin

## Compression

Tileset compression it's a RLE

```
Literal Block:
0XXXXXXX --> Lenght(0-127)
copy next N bytes are copied directly

RLE Block
1XXXXXXX ---> Lenght (0-127)
1RRRRRRR [VV]
VV repeated N times
```
## Usage

Synopsis:
```
For Decompress:
Tileset_editor.py decompress -r <ROM> -f <OutputFile> -o <Offset> -s "Size"

For Compress:
Tileset_editor.py compress -r <ROM> -f <OutputFile> -o <Offset> -s "Size" [--fill <fillByte>]
```

## Frecuency Answer Questions

### Can I use this tool in my personal project?

Of course, there's no need to ask. Feel free to use it in your project. I only ask that you mention me as contributor.

