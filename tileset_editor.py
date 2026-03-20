## Ginga no Sannin - Tileset editor
## RLE

import argparse
import sys
import os

class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print(f"\nError: {message}\n")
        self.show_help()
        sys.exit(1)

    def print_help(self):
        self.show_help()

    @staticmethod
    def show_help():
        print("+----------------------------------------------------")
        print("| Ginga no Sannin - NES Tileset editor by koda v0.1")
        print("+----------------------------------------------------")
        print("| Usage:")
        print("|   extract      Extract from ROM")
        print("|   insert       Insert to ROM")
        print("|   help         Show this message.")
        print("+----------------------------------------------------")
        print("| decompress:")
        print("|  -r <path>     Path to the ROM file")
        print("|  -f <path>     Output file")
        print("|  -o <hex>      Start offset")
        print("|  -s <hex>      Block size")
        print("|")
        print("| compress:")
        print("|  -f <path>     File to compress")
        print("|  -c <path>     Compressed file")
        print("+----------------------------------------------------")
        sys.exit(1)

def decompress(data):
    i = 0
    output = bytearray()

    repeat_count = 0
    repeat_value = 0
    literal_count = 0

    while i < len(data):
        if literal_count > 0:
            if i >= len(data):
                break
            output.append(data[i])
            i += 1
            literal_count -= 1
            continue

        if repeat_count > 0:
            output.append(repeat_value)
            repeat_count -= 1
            continue

        if i >= len(data):
            break

        byte = data[i]
        i += 1

##        if byte == 0xFF:
##            break

        # LITERAL
        if byte < 0x80:
            literal_count = byte

        # RLE
        else:
            repeat_count = byte & 0x7F

            if i >= len(data):
                break

            repeat_value = data[i]
            i += 1

    return output

def compress(data):
    i = 0
    output = bytearray()

    literal_buffer = bytearray()

    def flush_literals():
        nonlocal literal_buffer
        if literal_buffer:
            length = len(literal_buffer)
            output.append(length)
            output.extend(literal_buffer)
            literal_buffer = bytearray()

    while i < len(data):
        run_value = data[i]
        run_length = 1

        j = i + 1
        while j < len(data) and data[j] == run_value and run_length < 0x7F:
            run_length += 1
            j += 1

        if run_length >= 4:
            flush_literals()

            output.append(0x80 | run_length)
            output.append(run_value)

            i += run_length
        else:
            literal_buffer.append(run_value)

            if len(literal_buffer) == 0x7F:
                flush_literals()

            i += 1

    flush_literals()

    return output

def hexdump(data, label, width=16):
    print(f"\n[{label}] ({len(data)} bytes)")
    for i in range(0, len(data), width):
        chunk = data[i:i + width]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        print(f"{i:04X}: {hex_part}")
     
def read_rom(rom_file, addr, size):
    with open(rom_file, 'rb') as f:
        f.seek(addr)
        data = f.read(size)
        return data

def export_data(out_file, data):
    with open(out_file, 'wb') as f:
        f.write(data)
        return len(data)

def import_data(file):
    with open(file, "rb") as f:
        data = f.read()
    return data, len(data)

def write_rom(rom_file, data, addr, original_size, fill, fill_value, file_name):
    if len(data) > original_size:
        excess = len(data) - original_size
        print(f"Error: file {file_name}, {excess} bytes exceed input size.")
        sys.exit(1)
    else:
        free_space = original_size - len(data)
        filled_data = data
        if fill:
            filled_data = data + bytes([fill_value]) * free_space

        with open(rom_file, "r+b") as f:
            f.seek(addr)
            f.write(filled_data)
    return free_space

def main():
    parser = CustomArgumentParser(add_help=False)
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Extract command
    extract_parser = subparsers.add_parser('decompress')
    extract_parser.add_argument('-r', '--rom', required=True)
    extract_parser.add_argument('-f', '--out-file', required=True)
    extract_parser.add_argument('-o', '--start-offset', required=True, type=lambda x: int(x, 16))
    extract_parser.add_argument('-s', '--size', required=True, type=lambda x: int(x, 16))

    # Insert command
    insert_parser = subparsers.add_parser('compress')
    insert_parser.add_argument('-r', '--rom', required=True)
    insert_parser.add_argument('-f', '--in-file', required=True)
    insert_parser.add_argument('-o', '--start-offset', required=True, type=lambda x: int(x, 16))
    insert_parser.add_argument('-s', '--size', type=lambda x: int(x, 16))
    insert_parser.add_argument('--fill', nargs='?', default=None, const='FF', type=lambda x: int(x, 16) if x else 0xFF)

    help_parser = subparsers.add_parser('help')
    
    args = parser.parse_args()
    
    if args.command == 'decompress':
        if not os.path.exists(args.rom):
            print(f"Error: ROM file '{args.rom}' not found.\n")
            sys.exit(1)
        # Read Data
        data = read_rom(args.rom, args.start_offset, args.size)
        # Decompress
        decompress_tileset = decompress(data)
        # DEBUG
        #hexdump(decompress_tileset, "Tileset")
        # Export
        tileset_data_length = export_data(args.out_file, decompress_tileset)
        print(f"Extracted {tileset_data_length} bytes from {args.rom}\n")

    elif args.command == 'compress':
        if not os.path.exists(args.rom):
            print(f"Error: ROM file '{args.rom}' not found.\n")
            sys.exit(1)
        if not os.path.exists(args.in_file):
            print(f"Error: Input file '{args.in_file}' not found.\n")
            sys.exit(1)
        if args.fill is not None and args.size is None:
            sys.exit(1)
        fill = args.fill is not None
        fill_value = args.fill if args.fill is not None else 0
        # Read Bin
        data_tileset, decompressed_data_length = import_data(args.in_file)
        # Convert to planar
        compress_tileset = compress(data_tileset)
        compress_tileset_length = len(compress_tileset)
        #DEBBUG
        #hexdump(compress_tileset, "Compress Tileset")
        # Write ROM
        free_space = write_rom(args.rom, compress_tileset, args.start_offset, args.size, fill, fill_value, args.in_file)
        ratio = compress_tileset_length / decompressed_data_length
        print(f"Decompress: {decompressed_data_length} bytes, Compress: {compress_tileset_length} bytes, Ratio: {ratio:.8f}.")
        # Summary
        print(f"Inserted {args.in_file} to {args.rom}.")
        if args.size is not None:
            if fill:
                print(f"Data size: {compress_tileset_length} bytes, Free space: {free_space} bytes, filled with 0x{fill_value:02X}.\n")
            else:
                print(f"Data size: {compress_tileset_length} bytes, Free space: {free_space} bytes.\n")
        else:
            print(f"Data size: {compress_tileset_length} bytes.\n")
     
    else:
        show_help()
        
if __name__ == "__main__":
    main()
    
