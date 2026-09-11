import struct

file_path = r"C:\Users\aliso\Downloads\FluoriteStreamer-V1 (1).sh"
with open(file_path, "rb") as f:
    data = f.read()

e_shoff = struct.unpack("<Q", data[40:48])[0]
e_shentsize = struct.unpack("<H", data[58:60])[0]
e_shnum = struct.unpack("<H", data[60:62])[0]
e_shstrndx = struct.unpack("<H", data[62:64])[0]

shstr_off = struct.unpack("<Q", data[e_shoff + e_shstrndx * e_shentsize + 24 : e_shoff + e_shstrndx * e_shentsize + 32])[0]

print("=== ELF SECTIONS ===")
for i in range(e_shnum):
    off = e_shoff + i * e_shentsize
    sh_name_idx, sh_type, sh_flags, sh_addr, sh_offset, sh_size = struct.unpack("<IIQQQQ", data[off:off+40])
    
    name_end = data.find(b"\x00", shstr_off + sh_name_idx)
    sec_name = data[shstr_off + sh_name_idx:name_end].decode("latin-1", errors="ignore")
    
    print(f"[{i:2d}] {sec_name:<20} type={hex(sh_type):<8} off={hex(sh_offset):<8} addr={hex(sh_addr):<8} size={hex(sh_size)}")
