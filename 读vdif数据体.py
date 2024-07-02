import numpy as np
vdif_file = '/Users/buoluo/Desktop/NO058_B0329_0.dat'
def read_first_vdif_data_body(file_path):
    header_size = 32  # 头部大小
    payload_size = 1028 * 8 - 32  # 数据体大小
    with open(file_path, 'rb') as fh:
        fh.seek(header_size)  # 跳过头部（32字节）
        # 读取数据体（1028 * 8 - 32 字节）
        data_body = fh.read(payload_size)
        if len(data_body) != payload_size:
            print(f"未能读取到完整的数据体，读取到的字节数: {len(data_body)}")
            return None
        return data_body

# 读取VDIF文件中的第一个数据体
first_data_body = read_first_vdif_data_body(vdif_file)
np.set_printoptions(threshold=np.inf)

if first_data_body:
    first_body = np.frombuffer(first_data_body, dtype=np.int8)  # 将数据转换为int8类型
    min_value = np.min(first_body)
    max_value = np.max(first_body)
    print(f"数据体1（总字节数）：{len(first_body)}")
    print(f"数据体1（所有字节）：{first_body}")
    print(f"数据体1的范围：最小值={min_value}, 最大值={max_value}")
else:
    print("未读取到完整的数据体。")