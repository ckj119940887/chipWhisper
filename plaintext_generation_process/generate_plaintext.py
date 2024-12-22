import os

# 生成5000个AES128明文
def generate_aes128_plaintexts(num_plaintexts):
    plaintexts = []
    for _ in range(num_plaintexts):
        # 生成16字节的随机数据
        plaintext = os.urandom(16)
        # 将16字节的明文转换为16进制表示的列表
        hex_list = [f'0x{byte:02X}' for byte in plaintext]
        plaintexts.append(hex_list)
    return plaintexts

# 保存明文以方便后续的python读入并处理
def save_plaintexts_to_file(plaintexts, filename):
    with open(filename, 'w') as file:
        for hex_list in plaintexts:
            # 将16进制列表转换为以空格分隔的字符串
            hex_str = ' '.join(hex_list)
            # 写入文件，每个明文占一行
            file.write(hex_str + '\n')

# 保存明文到文件按照指定格式
def save_plaintexts_to_C(plaintexts, filename):
    with open(filename, 'w') as f:
        f.write(f"unsigned char plaintext[{len(plaintexts)}][16] = {{\n")
        for i, plaintext in enumerate(plaintexts):
            # 每行最多8个字节，拆分为两行
            hex_str = ', '.join(plaintext[:8]) + ',\n      ' + ', '.join(plaintext[8:])
            if i < len(plaintexts) - 1:
                f.write(f"    {{ {hex_str} }},\n")
            else:
                f.write(f"    {{ {hex_str} }}\n")
        f.write("};\n")

# 生成5000个AES128明文
plaintexts = generate_aes128_plaintexts(50)

#
save_plaintexts_to_file(plaintexts, 'plaintext.txt')

# 保存到C头文件
save_plaintexts_to_C(plaintexts, 'aes128_plaintexts.h')