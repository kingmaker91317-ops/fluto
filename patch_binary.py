import sys
import os

def patch_binary(input_file, new_url, output_file=None):
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return False

    with open(input_file, 'rb') as f:
        data = bytearray(f.read())

    target_url = b'https://spacex.emerite.store/api/v1/software/'
    target_len = len(target_url)  # 45 bytes

    pos = data.find(target_url)
    if pos == -1:
        print("Error: Target URL not found in binary.")
        return False

    new_url_bytes = new_url.encode('utf-8')
    if len(new_url_bytes) > target_len:
        print(f"Error: New URL is too long! Max length allowed: {target_len} chars.")
        return False

    replacement = new_url_bytes.ljust(target_len, b'\x00')
    data[pos:pos+target_len] = replacement

    if output_file is None:
        output_file = input_file.replace(".sh", "_Patched.sh")

    with open(output_file, 'wb') as f:
        f.write(data)

    print(f"==================================================")
    print(f" SUCCESS! Binary Patched Successfully.")
    print(f" Input Binary: {input_file}")
    print(f" Output Binary: {output_file}")
    print(f" New Server URL: {new_url}")
    print(f"==================================================")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python patch_binary.py <NEW_RENDER_SERVER_URL> [OUTPUT_FILE]")
        print("Example: python patch_binary.py https://my-fluorite-server.onrender.com/api/v1/software/")
    else:
        input_file = r"C:\Users\aliso\Downloads\FluoriteStreamer-V1 (1).sh"
        patch_binary(input_file, sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
