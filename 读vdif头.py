import os
import baseband
import baseband.vdif as vdif

# 指定VDIF文件的路径
vdif_file = '/Users/buoluo/Desktop/NO058_B0329_0.dat'

# 每个数据块的大小 (包括头部和数据体)
block_size_bits = 1028 * 8 * 8  # 每个块的大小是1028字节，转换为位

# 获取文件的总大小（字节）
file_size_bytes = os.path.getsize(vdif_file)
file_size_bits = file_size_bytes * 8  # 转换为位

# 计算总数据块数
total_blocks = file_size_bits // block_size_bits

print(f"总头个数：{total_blocks}")

# 读取并显示第一个头的信息
with vdif.open(vdif_file, 'rs') as fh:
    header = fh.header0

    # 显示第一个头信息
    print(f"seconds = {header['seconds']}")
    print(f"legacy_mode = {int(header['legacy_mode'])}")
    print(f"invalid = {int(header['invalid_data'])}")
    print(f"frame = {header['frame_nr']}")
    print(f"epoch = {header['ref_epoch']}")
    print(f"frame_length = {header['frame_length']}")
    print(f"nchan = {header['lg2_nchan']}")
    print(f"version = {header['vdif_version']}")
    print(f"station_id = {header['station_id']}")
    print(f"thread_id = {header['thread_id']}")
    print(f"nbits = {header['bits_per_sample']}")
    print(f"is_complex = {int(header['complex_data'])}")

    # 扩展头文件信息
    extended_keys = ['extended1', 'extended2', 'extended3', 'extended4']
    for key in extended_keys:
        # 检查并获取扩展字段的值，如果不存在则赋值为0
        value = header.get(key, 0)
        print(f"{key} = {value}")