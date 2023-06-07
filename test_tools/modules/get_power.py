import zipfile
import subprocess
import os
import re

from commandExec import execute

def get_charge_cpu():
    output = subprocess.check_output('adb shell dumpsys batterystats | grep -A 15 "Estimated power use"', shell = True).decode('utf-8')
    # 使用正则表达式匹配 CPU 值
    matches = re.findall(r"cpu:\s+(\d+\.\d+)", output)
    # 提取 CPU 值
    cpu_value = float(matches[0])
    return cpu_value




def get_charge_count():
    out = execute('dumpsys battery')
    a = out.split('\n')
    return  a[6][18:]

def get_power2():
    output = subprocess.check_output('adb shell dumpsys batterystats | grep -A 15 "since last charge"', shell = True)
    try:            
        a = str(output)[2:].split('\\n')
        for i in a:
            if 'Total run time' in i:
                run_time = i.split(' ')[5:7]
            if 'Discharge' in i:
                discharge = i.split(' ')[3]
    except:
        print(output)

    print(run_time, discharge)
    return run_time, discharge

def get_power_by_batterystats():
    output = subprocess.check_output('adb shell dumpsys batterystats | grep "Computed drain:" ', shell = True)
    a = str(output).split(' ')[8][:-1]
    return a


def get_power(new_file_name):
    os.system('adb bugreport')

    # 获取当前目录下所有文件的列表
    file_list = os.listdir()

    # 遍历所有文件
    for file_name in file_list:
        # 如果文件名以"blue"开头
        if file_name.startswith("bugreport"):
            # 构造新的文件名，以"red"开头，保留原始扩展名
            # 重命名文件
            os.rename(file_name, new_file_name)
            # 打印重命名后的文件名

    zip_file_path = new_file_name
    txt_folder_path = "tests/power/temp"

    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        # 遍历压缩包中的文件
        for file_info in zip_ref.infolist():
            # 如果文件名以".txt"结尾
            if file_info.filename.startswith('bugreport-blueline'):
                # 解压出文件
                zip_ref.extract(file_info, txt_folder_path)
                # 打印解压出文件的路径
                file_path = os.path.join(txt_folder_path, file_info.filename)
                output = subprocess.check_output('cat {} | grep -A 15 "since last charge"'.format(file_path), shell = True)
                
                a = str(output)[2:].split('\\n')
                for i in a:
                    if 'Total run time' in i:
                        run_time = i.split(' ')[5:7]
                    if 'Discharge' in i:
                        discharge = i.split(' ')[3]

                os.remove(file_path)
                print(run_time, discharge)
                return run_time, discharge
