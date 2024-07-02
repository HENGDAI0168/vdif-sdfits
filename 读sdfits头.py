from astropy.io import fits


def read_sdfits_header(fits_file):
    # 打开FITS文件
    with fits.open(fits_file) as hdul:
        # 打印主HDU的头信息
        print("Primary HDU Header:")
        print(repr(hdul[0].header))

        # 如果存在其他HDUs，遍历并打印它们的头信息
        if len(hdul) > 1:
            for i in range(1, len(hdul)):
                print(f"\nHeader for HDU {i}:")
                print(repr(hdul[i].header))


# 替换下面的路径为你的SDFITS文件路径
fits_file_path = '/Users/buoluo/Desktop/RNP_0_A.fits'
read_sdfits_header(fits_file_path)