#!/usr/bin/env python
# coding: utf-8

# In[6]:


import os
import numpy as np
from astropy.io import fits
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import baseband
import baseband.vdif as vdif

# 读取VDIF文件中的数据体
def read_vdif_data_bodies(file_path):
    header_size = 32  # 头部大小
    payload_size = 1028 * 8 - 32  # 数据体大小
    data_bodies = []

    with open(file_path, 'rb') as fh:
        while True:
            fh.seek(header_size, 1)  # 跳过头部（32字节）
            data_body = fh.read(payload_size)
            if len(data_body) != payload_size:
                break
            data_bodies.append(data_body)

    return data_bodies

# 提取数据体中的第五个通道数据
def extract_channel_5(data_bodies):
    left_data = []
    right_data = []

    for data_body in data_bodies:
        data = np.frombuffer(data_body, dtype=np.int8)

        # 提取第 5 个通道的左旋和右旋数据
        channel_5_left = data[8::16]
        channel_5_right = data[9::16]

        left_data.append(channel_5_left)
        right_data.append(channel_5_right)

    return np.concatenate(left_data), np.concatenate(right_data)

# 对数据进行归一化和量化
def quantize_data(data):
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_reshaped = data.reshape(-1, 1)
    normalized_data = scaler.fit_transform(data_reshaped).astype(np.float32)  # 归一化并转换为float32
    return normalized_data.flatten()

# 读取VDIF文件头信息并生成SDFITS文件
def convert_vdif_to_sdfits(vdif_file, output_sdfits_file):
    # 打开VDIF文件并读取头信息
    with vdif.open(vdif_file, 'rs') as fh:
        header = fh.header0

        vdif_header = {
            'seconds': header['seconds'],
            'legacy_mode': int(header['legacy_mode']),
            'invalid': int(header['invalid_data']),
            'frame': header['frame_nr'],
            'epoch': header['ref_epoch'],
            'frame_length': header['frame_length'],
            'nchan': header['lg2_nchan'],
            'version': header['vdif_version'],
            'station_id': header['station_id'],
            'thread_id': header['thread_id'],
            'nbits': header['bits_per_sample'],
            'is_complex': int(header['complex_data']),
            'extended1': getattr(header, 'extended1', 0),
            'extended2': getattr(header, 'extended2', 0),
            'extended3': getattr(header, 'extended3', 0),
            'extended4': getattr(header, 'extended4', 0)
        }

    # 基础参考纪元是2000年1月1日0时 (J2000.0)
    reference_epoch = datetime(2000, 1, 1, 0, 0, 0)
    # 使用精确的月份增加来计算epoch开始时间
    months_since_2000 = vdif_header['epoch'] * 6
    years_since_2000 = months_since_2000 // 12
    months_remainder = months_since_2000 % 12
    epoch_start_time = reference_epoch.replace(year=reference_epoch.year + years_since_2000)
    epoch_start_time = epoch_start_time.replace(month=epoch_start_time.month + months_remainder)
    # 加上从epoch开始的秒数
    observation_time = epoch_start_time + timedelta(seconds=vdif_header['seconds'])
    # 计算从当天午夜开始的秒数
    midnight_of_observation = datetime(observation_time.year, observation_time.month, observation_time.day)
    seconds_since_midnight = (observation_time - midnight_of_observation).total_seconds()
    # 使用date_obs存储SDFITS所需要的TIME格式
    date_obs = seconds_since_midnight

    # 读取VDIF文件中的所有数据体
    data_bodies = read_vdif_data_bodies(vdif_file)

    # 提取第五个通道的数据
    left_data, right_data = extract_channel_5(data_bodies)

    # 输出数据的统计信息
    print(f"左旋数据的总个数：{len(left_data)}")
    print(f"右旋数据的总个数：{len(right_data)}")

    # 量化数据
    left_data_quantized = quantize_data(left_data)
    right_data_quantized = quantize_data(right_data)

    # 保存量化数据到文件
    left_data_file = '/Users/buoluo/Desktop/channel_5_left_quantized.dat'
    right_data_file = '/Users/buoluo/Desktop/channel_5_right_quantized.dat'

    left_data_quantized.tofile(left_data_file)
    right_data_quantized.tofile(right_data_file)

    # 打印前十条量化后的左旋和右旋数据
    print("\n量化左旋数据的前十条记录：")
    print(left_data_quantized[:10])

    print("\n量化右旋数据的前十条记录：")
    print(right_data_quantized[:10])

    # 定义列
    cols = [
        fits.Column(name='DRA', format='E', unit='arcsec', array=np.zeros(len(left_data_quantized), dtype='float32')),  # VDIF没有提供相对赤经差异，数据需更改
        fits.Column(name='DDEC', format='E', unit='arcsec', array=np.zeros(len(right_data_quantized), dtype='float32')),  # VDIF没有提供相对赤纬差异，数据需更改
        fits.Column(name='LP', format='E', unit='K', array=left_data_quantized),  # 左旋偏振温度
        fits.Column(name='RP', format='E', unit='K', array=right_data_quantized)  # 右旋偏振温度
    ]
    coldefs = fits.ColDefs(cols)
    bin_table_hdu = fits.BinTableHDU.from_columns(coldefs)

    # 创建FITS主HDU
    primary_hdu = fits.PrimaryHDU()
    primary_header = primary_hdu.header
    primary_header['EXTEND'] = True
    primary_header['OBSER'] = ''
    primary_header['SOURCE'] = 'B0329+54'  # 观测对象名称
    primary_header['FREQ'] = ''
    primary_header['BANDWID'] = ''
    primary_header['TCAL'] = ''
    primary_header['RA'] = ''
    primary_header['DEC'] = ''
    primary_header['DATATYPE'] = ''
    primary_header['AZ'] = ''
    primary_header['EL'] = ''
    primary_header['LTSYS'] = ''
    primary_header['RTSYS'] = ''
    primary_header['TIME'] = date_obs

    # 创建HDU列表并写入文件
    hdul = fits.HDUList([primary_hdu, bin_table_hdu])
    hdul.writeto(output_sdfits_file, overwrite=True)

    # 打印主头文件的信息
    print("Primary HDU Header:")
    print(repr(hdul[0].header))

    # 打印二进制表头文件的信息
    print("\nBinary Table HDU Header:")
    print(repr(hdul[1].header))

    # 读取生成的SDFITS文件并打印前十条数据
    with fits.open(output_sdfits_file) as hdul:
        data = hdul[1].data
        print("\nSDFITS文件中的前十条数据：")
        print(data[:10])

# 示例文件路径
vdif_file = '/Users/buoluo/Desktop/NO058_B0329_0.dat'
output_sdfits_file = '/Users/buoluo/Desktop/output_sdfits_from_vdif.fits'

# 转换VDIF文件为SDFITS文件
convert_vdif_to_sdfits(vdif_file, output_sdfits_file)

print(f"SDFITS文件已生成：{output_sdfits_file}")

