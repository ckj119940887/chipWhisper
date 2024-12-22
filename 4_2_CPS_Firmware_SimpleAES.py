import subprocess
import numpy as np
import time
import matplotlib.pyplot as plt

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

# device declaration
SCOPETYPE = 'OPENADC'
PLATFORM = 'CW308_SAM4S'
#PLATFORM = 'CW308_STM32F3'
CRYPTO_TARGET='TINYAES128C'
SS_VER='SS_VER_2_1'
TARGET_DIR='/home/kejun/git_dir/chipwhisperer'

# connect the target device
exec(open('generic_connect.py').read())

# define bash script
bash_script = f"""
PLATFORM={PLATFORM}
CRYPTO_TARGET={CRYPTO_TARGET}
SS_VER={SS_VER}
TARGET_DIR={TARGET_DIR}

echo "Platform: $PLATFORM"
echo "Crypto Target: $CRYPTO_TARGET"
echo "SS Version: $SS_VER"
echo "Target Directory: $TARGET_DIR"

cd $TARGET_DIR/hardware/victims/firmware/simpleserial-aes
make PLATFORM=$1 CRYPTO_TARGET=$2 SS_VER=$3 -j
"""

# enable the above environment variable in bash terminal
result = subprocess.run(['bash', '-c', bash_script], capture_output=True, text=True)

# output the result
print(result.stdout)

# execute the target program
cw.program_target(scope, prog, "{}/hardware/victims/firmware/simpleserial-aes/simpleserial-aes-{}.hex".format(TARGET_DIR, PLATFORM))

# randomly generate plaintext
ktp = cw.ktp.Basic()
trace_array = []
textin_array = []

key, text = ktp.next()

# target.simpleserial_write('k', key)
target.set_key(key)

# capture the power trace when input the plaintext
# the number of plaintext used
N = 200
print("Capturing traces\n")
for i in range(N):
    scope.arm()

    target.simpleserial_write('p', text)

    ret = scope.capture()
    if ret:
        print("Target timed out!")
        continue

    response = target.simpleserial_read('r', 16)

    trace_array.append(scope.get_last_trace())
    textin_array.append(text)

    key, text = ktp.next()

# compute the all 256 possible encrypted text
HW = []
for i in range(0,256):
    HW.append(calc_hamming_weight(i))

"""
破解过程如下
textin_array有1000个明文
trace_array有 1000行(对应于1000个明文)，5000列(5000个sample points)

trace_array的结构如下：
[
    [point_0, point_1, point_2, ...], # trace 0
    [point_0, point_1, point_2, ...], # trace 1
    [point_0, point_1, point_2, ...], # trace 2
    ...
]

hws的结构如下：hws的维度是1000行(对应于1000个明文)，1列(每次计算一个byte)
[
      [HW[aes_internal(plaintext0[0], key[0])], # trace 0
      [HW[aes_internal(plaintext1[0], key[0])], # trace 1
      [HW[aes_internal(plaintext2[0], key[0])], # trace 2
      ...
]

计算公式：
r = cov(trace_array, t_bar, hws, hws_bar) / (o_t * o_hws)
其中cov(trace_array, t_bar, hws, hws_bar) = \sigma(trace_array - t_bar)(hws - hws_bar)

这里假设我们有100个明文，每个trace的sample points是5000
那么np.shape(trace_array) = (100, 5000)
np.shape(t_bar) = (5000,) //在5000列上进行求平均值的过程

np.shape(hws) = (100,) //我们每次之破解一个byte，所以这里是针对100个明文的相同位置的byte进行破解
np.shape(hws_bar) = (1,) // 在列的方向上进行求平均 

\sigma(trace_array - t_bar)(hws - hws_bar) 这里的循环计数是从0 - 99(100)
当计数为0时，对应的是 (trace_array[0][0...4999] - t_bar[0...4999])(hws[0] - hws_bar)
(hws[0] - hws_bar)计算出来的是一个数
整个\sigma计算的结果是(5000,)

然后我们在此基础上选出最大值(绝对值)出现的位置，该位置就是key，比如位置是0x23，那么0x23就是对应的key byte
"""

def mean(X):
    return (np.sum(X, axis=0) / len(X))

def std_dev(X, X_bar):
    return np.sqrt(np.sum((X-X_bar)**2, axis=0))

def cov(X, X_bar, Y, Y_bar):
    return np.sum((X-X_bar)*(Y-Y_bar), axis=0)

t_bar = np.sum(trace_array, axis=0)/len(trace_array)
o_t = np.sqrt(np.sum((trace_array - t_bar)**2, axis=0))

cparefs = [0] * 16 #put your key byte guess correlations here
bestguess = [0] * 16 #put your key byte guesses here

for bnum in range(0, 16):
    maxcpa = [0] * 256
    for kguess in range(0, 256):
        # ###################
        # Add your code here
        # ###################
        hws = np.array([[HW[aes_internal(textin[bnum],kguess)] for textin in textin_array]]).transpose()

        hws_bar = mean(hws)
        o_hws = std_dev(hws, hws_bar)
        correlation = cov(trace_array, t_bar, hws, hws_bar)
        cpaoutput = correlation/(o_t*o_hws)
        maxcpa[kguess] = max(abs(cpaoutput))

    guess = np.argmax(maxcpa)
    bestguess[bnum] = guess
    cparefs[bnum] = hex(key[bnum])

print("Best Key Guess: ", end="")
for b in bestguess: print("%02x " % b, end="")
print("\n")

print("the real key is \n")
for k in key:
    print(hex(k))

# close the target device
scope.dis()
target.dis()
