from tqdm import tqdm
import csv
import glob
import os
import pathlib
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
import cv2
import numpy as np


def write_csv(Angle_csv, moving_log):
    with open(Angle_csv, 'w', newline='') as f:
        Angle_writer = csv.writer(f, delimiter=',')
        row_head = ['FolderIdx', 'PathInRaw']
        Angle_writer.writerow(row_head)

        for line in moving_log:
            Angle_writer.writerow(line)

    print("Done")


def checking_file(AnglePath, Anglename):
    color_spaces = ['b.jpg', 'g.jpg', 'r.jpg']
    firm = ['p.jpg']
    xxml = ['x.xml']
    current_dir = os.path.join(os.getcwd(), Anglename)
    moving_list = []
    Idx = 0

    for i in range(len(AnglePath)):
        filename = AnglePath[i] + '\\' + "*.*"
        files = glob.glob(filename)

        if len(files) >= 3:
            bgr_box = []

            sample_dir = os.path.join(current_dir, str(Idx))
            for file in files:
                suffix = os.path.split(file)[1].split(os.path.split(AnglePath[i])[1])[1]
                if suffix == ".jpg":  # 保留 #打開確定非灰階 #類型一
                    color_img = cv2.imread(file)
                    color_img = np.transpose(color_img, [2, 0, 1])

                    if (color_img[0] == color_img[1]).all() == False:
                        if (color_img[1] == color_img[2]).all() == False:
                            try:
                                if not os.path.isdir(sample_dir):
                                    os.makedirs(sample_dir)
                                    dest_file = os.path.join(sample_dir, os.path.basename(file))
                                    shutil.copy(file, dest_file)

                                else:
                                    dest_file = os.path.join(sample_dir, os.path.basename(file))
                                    shutil.copy(file, dest_file)

                            except Exception as e:
                                print(e)


                elif suffix in firm:  # 廠商圖firm
                    if not os.path.isdir(sample_dir):
                        dest_file = os.path.join(sample_dir, os.path.basename(file))
                        firm_source, firm_dst = file, dest_file  #彩圖不存在, 先保存資料

                    else:
                        dest_file = os.path.join(sample_dir, os.path.basename(file))
                        shutil.copy(file, dest_file)  # 彩圖存在, copy
                        firm_dst = dest_file

                elif suffix in color_spaces:  # 保留 #確定bgr存在 #類型二
                    bgr_box.append(file)
                    if len(bgr_box) == 3:
                        for bgr in bgr_box:
                            try:
                                if not os.path.isdir(sample_dir):
                                    os.makedirs(sample_dir)
                                    dest_file = os.path.join(sample_dir, os.path.split(bgr)[1])
                                    shutil.copy(bgr, dest_file)
                                    if os.path.exists(firm_dst) is False:  # 沒有彩圖
                                        shutil.copy(firm_source, firm_dst)  # firm的暫存檔

                                else:
                                    dest_file = os.path.join(sample_dir, os.path.split(bgr)[1])
                                    shutil.copy(bgr, dest_file)
                                    if os.path.exists(firm_dst) is False:  # 沒有彩圖
                                        shutil.copy(firm_source, firm_dst)  # firm的暫存檔

                            except Exception as e:
                                print(e)

                elif suffix in xxml:  # 必定存在資料, 最後處理
                    if not os.path.isdir(sample_dir):
                        continue

                    else:
                        dest_file = os.path.join(sample_dir, os.path.basename(file))
                        shutil.copy(file, dest_file)
                        jpg_path = os.path.split(file)[0]
                        records = Idx, Path(jpg_path).relative_to(pathlib.Path.cwd())
                        if records not in moving_list:
                            moving_list.append(records)
                            Idx += 1


    return moving_list


def find_xml(path):  # 保存紀錄xml
    UltraWide = []  # 廣角
    Wide = []  # 局部
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith("x.xml"):
                os.chdir(root)
                tree = ET.parse(file)
                rootNode = tree.getroot()
                Color_type = ["Color", "Color_BGR", "Color_BGR_B", "Color_BGR_G", "Color_BGR_R"]  # 只看彩色
                try:
                    nodeSetting = rootNode.find('SLO').find('Scan').find('SLOSetting')
                    if nodeSetting.text in Color_type:
                        LaserBlue = rootNode.find('SLO').find('Scan').find('LaserPowerBlue').text
                        LaserGreen = rootNode.find('SLO').find('Scan').find('LaserPowerGreen').text
                        LaserRed = rootNode.find('SLO').find('Scan').find('LaserPowerRed').text
                        if LaserBlue and LaserGreen and LaserRed != "0":
                            SLOAngle = rootNode.find('SLO').find('Scan').find('SLOAngle').text
                            if float(SLOAngle) >= 110.0:
                                if root not in UltraWide:
                                    UltraWide.append(root)

                            elif float(SLOAngle) < 110.0:
                                if root not in Wide:
                                    Wide.append(root)

                except Exception as e:
                    print(e, ": ", file)

    return UltraWide, Wide


myRoot = os.getcwd()
UltraWide, Wide = find_xml(myRoot)

os.chdir(myRoot)
UltraWide_log = checking_file(UltraWide, "dataset_ultrawide")
Wide_log = checking_file(Wide, "dataset_smallAngle")

csv_file_ultra = os.path.join(os.path.join(os.getcwd(), "dataset_ultrawide"), "dataset_ultrawide.csv")
csv_file_wide = os.path.join(os.path.join(os.getcwd(), "dataset_smallAngle"), "dataset_smallAngle.csv")

write_csv(csv_file_ultra, UltraWide_log)
write_csv(csv_file_wide, Wide_log)
print("Done \(OvO)/")
