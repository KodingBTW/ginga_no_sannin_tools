set ROM="Ginga no Sannin (Japan).nes"

tileset_editor.py decompress -r %ROM% -f "main_fonts1.bin" -o "DF40" -s "119"
tileset_editor.py decompress -r %ROM% -f "main_fonts2.bin" -o "50C7" -s "410"
tileset_editor.py decompress -r %ROM% -f "title_screen.bin" -o "DB90" -s "3B0"
pause