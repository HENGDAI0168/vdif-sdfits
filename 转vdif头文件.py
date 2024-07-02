from astropy.io import fits
import numpy as np
from datetime import datetime, timedelta

# VDIF头信息
vdif_header = {
    'seconds': 68133904,
    'legacy_mode': 0,
    'invalid': 0,
    'frame': 0,
    'epoch': 44,
    'frame_length': 1028,
    'nchan': 4,
    'version': 0,
    'station_id': 0,
    'thread_id': 0,
    'nbits': 7,
    'is_complex': 0,
    'extended1': 0,
    'extended2': 0,
    'extended3': 0,
    'extended4': 0
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

# 创建FITS主HDU
primary_hdu = fits.PrimaryHDU()
primary_header = primary_hdu.header
primary_header['EXTEND'] = ''
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

# 创建数据列，初始化数组大小为0（数据需按实际更改）
data = {
    'DRA': np.zeros(0, dtype='float32'),  # VDIF没有提供相对赤经差异，数据需更改
    'DDEC': np.zeros(0, dtype='float32'),  # VDIF没有提供相对赤纬差异，数据需更改
    'LP': np.random.uniform(low=0, high=0, size=0).astype('float32'),  # 左旋偏振温度，数据需更改
    'RP': np.random.uniform(low=0, high=0, size=0).astype('float32')  # 右旋偏振温度，数据需更改
}

# 定义列
cols = [
    fits.Column(name='DRA', format='E', unit='arcsec', array=data['DRA']),#赤经偏差
    fits.Column(name='DDEC', format='E', unit='arcsec', array=data['DDEC']),#赤纬偏差
    fits.Column(name='LP', format='E', unit='K', array=data['LP']),#左旋
    fits.Column(name='RP', format='E', unit='K', array=data['RP'])#右旋
]
coldefs = fits.ColDefs(cols)
bin_table_hdu = fits.BinTableHDU.from_columns(coldefs)

# 创建HDU列表并写入文件
hdul = fits.HDUList([primary_hdu, bin_table_hdu])
hdul.writeto('output_sdfits_from_vdif.fits', overwrite=True)

# 打印主头文件的信息
print("Primary HDU Header:")
print(repr(hdul[0].header))

# 打印二进制表头文件的信息
print("\nBinary Table HDU Header:")
print(repr(hdul[1].header))

