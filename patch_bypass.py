import os

def create_unlocked_binary(input_file, output_file):
    with open(input_file, "rb") as f:
        data = bytearray(f.read())

    # 1. NOP out the curl error check branch at 0x9a5db4 (file offset 0x9ac9c4)
    patch_offset1 = 0x6c10 + 0x9a5db4
    if data[patch_offset1:patch_offset1+4] == bytes.fromhex("21010054"):
        data[patch_offset1:patch_offset1+4] = bytes.fromhex("1f2003d5")
        print(f"[+] NOPed curl error check branch at {hex(patch_offset1)}!")

    # 2. NOP out the JSON auth fail branch at 0x9a5e30 (file offset 0x9aca40)
    patch_offset2 = 0x6c10 + 0x9a5e30
    print(f"Bytes at {hex(patch_offset2)}: {data[patch_offset2:patch_offset2+4].hex()}")
    if data[patch_offset2:patch_offset2+4] == bytes.fromhex("a0020036"):
        data[patch_offset2:patch_offset2+4] = bytes.fromhex("1f2003d5")
        print(f"[+] NOPed JSON auth failure branch at {hex(patch_offset2)}!")

    # 3. Patch Server URL to Render URL
    target_url = b'https://spacex.emerite.store/api/v1/software/'
    new_url = b'https://fluto.onrender.com/api/v1/software/'
    pos = data.find(target_url)
    if pos != -1:
        replacement = new_url.ljust(len(target_url), b'\x00')
        data[pos:pos+len(target_url)] = replacement
        print(f"[+] Patched Server URL at offset {hex(pos)}!")

    with open(output_file, "wb") as f:
        f.write(data)

    print(f"==================================================")
    print(f" UNLOCKED BINARY CREATED SUCCESSFULLY!")
    print(f" Output File: {output_file}")
    print(f"==================================================")

if __name__ == "__main__":
    input_file = r"C:\Users\aliso\Downloads\FluoriteStreamer-V1 (1).sh"
    output_file = r"C:\Users\aliso\Downloads\FluoriteStreamer_Unlocked.sh"
    create_unlocked_binary(input_file, output_file)
