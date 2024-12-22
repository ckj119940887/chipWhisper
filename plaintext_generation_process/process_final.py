import numpy as np
import matplotlib.pyplot as plt

def extract_blocks(filename):
    blocks = []
    current_block = []

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()

            if line == "//---":
                # 如果当前块有数据，保存到 blocks 列表中
                if current_block:
                    blocks.append(current_block)
                    current_block = []
            else:
                # 将行添加到当前块
                current_block.append(line)

        # 处理文件末尾可能没有 //--- 的情况
        if current_block:
            blocks.append(current_block)

    return blocks

def normalize_blocks(blocks):
    # 转换每个子列表中的字符串数据为整数
    blocks = [[int(item, 16) for item in block] for block in blocks]

    # 找到最短子列表的长度
    min_length = min(len(block) for block in blocks)

    # 剪裁每个子列表到最短长度
    normalized_blocks = [block[:min_length] for block in blocks]

    return normalized_blocks

# the sbox of AES encryption engine
sbox = [
    # 0    1    2    3    4    5    6    7    8    9    a    b    c    d    e    f
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76, # 0
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0, # 1
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15, # 2
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75, # 3
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84, # 4
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf, # 5
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8, # 6
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2, # 7
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73, # 8
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb, # 9
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79, # a
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08, # b
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a, # c
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e, # d
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf, # e
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16  # f
]

# compute the encrypted text according to the sbox
def aes_internal(inputdata, key):
    return sbox[inputdata ^ key]

# compute the hamming weight of the specified binary number
def calc_hamming_weight(n):
    return bin(n).count("1")

# 读入明文
def read_plaintexts(filename):
    plaintexts = []
    with open(filename, 'r') as file:
        for line in file:
            # 去掉行末的换行符，并按空格分隔
            hex_list = line.strip().split()
            # 将每个16进制字符串转换为整数
            int_list = [int(hex_str, 16) for hex_str in hex_list]
            plaintexts.append(int_list)
    return plaintexts

# 使用示例
plaintexts = read_plaintexts("plaintext.txt")
blocks = extract_blocks('extract.txt')

processed_blocks = normalize_blocks(blocks)
print(np.shape(processed_blocks))

# compute the all 256 possible encrypted text
HW = []
for i in range(0,256):
    HW.append(calc_hamming_weight(i))

key = [0xC9, 0x95, 0x55, 0x31, 0xA6, 0x50, 0xD1, 0x54, 0x7B, 0xD8, 0xC5, 0xAA, 0xA4, 0xA4, 0xBD, 0xAC]

# display
# 我们只关系第0个byte
bnum = 0
# 总共有9个group，分别是0-8
hw_groups = [[], [], [], [], [], [], [], [], []]
for tnum in range(len(processed_blocks)):
    hw_of_byte = HW[aes_internal(plaintexts[tnum][bnum], key[bnum])]
    # 根据第 bnum 个byte对应的hamming distance进行分组
    hw_groups[hw_of_byte].append(processed_blocks[tnum])


# 这里的求平均是在每个分组中进行的，每个分组有多条trace(每个trace有N个sample points)
# 假设 hw_groups[0] = [[1,2,3,4],[1,2,3,4]], 那么求出的平均值是 [1,2,3,4]
# 即在每个trace的对应分量上求平均
hw_averages = np.array([np.average(hw_groups[hw], axis=0) for hw in range(9)])

# 这里是对上面的每个分组又进行了一次平均值
# hw_averages[0] = [0...N_1], hw_averages[1] = [0...N_1], ... hw_averages[8] = [0...N_1],
# 这里还是对每个分组中的每个分量进行平均
avg_trace = np.average(hw_averages, axis=0)

plot_start = 0
plot_end = len(processed_blocks[0])

# 这里我们把每个trace中所有的sample points 都画出来
xrange = list(range(len(processed_blocks[0]))[plot_start:plot_end])

#sbox_loc = np.argmin(abs(hw_averages[0]-avg_trace))
sbox_loc=211

plt.figure(2)
plt.title("HW vs Voltage Measurement")
plt.plot(list(range(0, 9)), hw_averages[:,sbox_loc])
plt.xlabel("Hamming Weight of Intermediate Value")
plt.ylabel("Average Value of Measurement")
plt.show()

for i in range(0,9) :
    print(np.argmin(abs(hw_averages[i]-avg_trace)))
