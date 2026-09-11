import os

def create_perfect_bypass_v3(input_file, output_file):
    with open(input_file, "rb") as f:
        data = bytearray(f.read())

    # Jump directly to Auth Success Setup & Menu Jump at 0x9a5e74
    # File offset = 0x6c10 + 0x9a5db4 = 0x9ac9c4
    patch_offset = 0x6c10 + 0x9a5db4
    original_bytes = data[patch_offset:patch_offset+4]
    
    print(f"Original instruction bytes at {hex(patch_offset)}: {original_bytes.hex()}")
    
    # Replace with b #0x9a5e74 (opcode 30000014)
    jump_success_bytes = bytes.fromhex("30000014")
    data[patch_offset:patch_offset+4] = jump_success_bytes
    print(f"[+] Successfully inserted direct jump to Menu Loader at {hex(patch_offset)}!")

    # Patch Server URL to Render URL
    target_url = b'https://spacex.emerite.store/api/v1/software/'
    new_url = b'https://fluto.onrender.com/api/v1/software/'
    pos = data.find(target_url)
    if pos != -1:
        replacement = new_url.ljust(len(target_url), b'\x00')
        data[pos:pos+len(target_url)] = replacement
        print(f"[+] Successfully patched Server URL at offset {hex(pos)}!")

    with open(output_file, "wb") as f:
        f.write(data)

    print(f"==================================================")
    print(f" V3 BYPASS BINARY CREATED SUCCESSFULLY!")
    print(f" Output File: {output_file}")
    print(f"==================================================")

if __name__ == "__main__":
    input_file = r"C:\Users\aliso\Downloads\FluoriteStreamer-V1 (1).sh"
    output_file = r"C:\Users\aliso\Downloads\FluoriteStreamer_Unlocked_V3.sh"
    create_perfect_bypass_v3(input_file, output_file)
