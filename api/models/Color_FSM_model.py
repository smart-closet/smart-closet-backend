import cv2
import numpy as np
from sklearn.cluster import KMeans
#from colorthief import ColorThief
from scipy.spatial import distance
import colorsys
from fastapi import UploadFile
from dotenv import load_dotenv
from PIL import Image
load_dotenv()

import matplotlib.pyplot as plt

# img 是 numpy array


# 使用加權 RGB 來計算亮度
def calculate_brightness(color):
    return 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]

def extract_dominant_color(img):

    
    img = np.array(img)
    print(img.shape)
    
    # 如果圖像是 RGBA 格式（有透明通道）
    if img.shape[2] == 4:
        filtered_img = img[img[:, :, 3] == 255, :3]
        print(filtered_img)
 
    # 重塑圖像數據為一維數組 (每個像素的RGB值)
    pixels = filtered_img.reshape((-1, 3))

    # 用 kmeans 提取 5 個最常見的顏色
    kmeans = KMeans(n_clusters=5, random_state=42)
    kmeans.fit(pixels)

    # 取得最常見的五種顏色
    centers = kmeans.cluster_centers_
    # 將每個數據點用他的 centroid 編碼，看他屬於哪個 group
    labels = kmeans.labels_

    # 計算每個顏色的比例
    unique, counts = np.unique(labels, return_counts=True)

    # 將顏色按照出現順序排
    sorted_idx = np.argsort(counts)[::-1] #由次數大到小排編號
    sorted_colors = centers[sorted_idx].astype(int) 
    sorted_counts = counts[sorted_idx]

    total_counts = np.sum(sorted_counts)
    proportions = (sorted_counts / total_counts)
    #計算顏色的亮度
    brightness_values = np.array([calculate_brightness(color) for color in sorted_colors])
    
    print("check",sorted_colors )
    # 如果顏色比例大於50%就直接選他當主色
    dominant_color = None
    for i, proportion in enumerate(proportions):
        if proportion >= 0.4:
            dominant_color = sorted_colors[i]
            print(f"顏色比率大於 45% 的主色: {dominant_color}")
            return dominant_color
    
    # 如果是淺色的衣服且沒有超過50%的主色，則選擇比例大於 15% 且亮度最高的颜色
    valid_colors = sorted_colors[proportions > 0.15]
    valid_brightness = brightness_values[proportions > 0.15]

    if len(valid_brightness) > 0:
        brightest_color = valid_colors[np.argmax(valid_brightness)]
        print(f"比例大於15%且最亮的顏色: {brightest_color}")
        return brightest_color
    else:
        print("沒有符合條件的顏色。")
        return None
    
    
# 將 Hex 顏色轉換為 RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
def rgb_to_hsv(color_rgb):
    color_rgb = np.array([[color_rgb]], dtype=np.uint8)  # 转换为 OpenCV 格式
    color_hsv = cv2.cvtColor(color_rgb, cv2.COLOR_RGB2HSV)
    return color_hsv[0][0].astype(float)  # 转换为浮点型以避免溢出
    
def calculate_hsv_distance(color1_rgb, color2_rgb,threshold):
    hsv1 = colorsys.rgb_to_hsv(*[c / 255.0 for c in color1_rgb])
    hsv2 = colorsys.rgb_to_hsv(*[c / 255.0 for c in color2_rgb])
    hue_distance = min(abs(hsv1[0] - hsv2[0]), 360 - abs(hsv1[0] - hsv2[0])) #色相
    sat_distance = abs(hsv1[1] - hsv2[1]) #飽和度
    val_distance = abs(hsv1[2] - hsv2[2]) #明度
    
    if hsv1[2] < threshold and hsv2[2] < threshold:
        return np.sqrt(sat_distance ** 2 + val_distance ** 2)
  
    return np.sqrt((5 * hue_distance) ** 2 + sat_distance ** 2 + val_distance ** 2)


def find_closest_color_hsv(color, colors_list):
    distances = []
    for hex_color in colors_list:
        rgb_color = hex_to_rgb(hex_color)
        dist = calculate_hsv_distance(color, rgb_color,0.2)
        distances.append((hex_color, dist))
    
    # 按距離從小到大排序
    distances.sort(key=lambda x: x[1])
    
    # 返回最接近的三個顏色
    return distances[1][0]#[distances[i][0] for i in range(3)]

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def identify_color(image: Image.Image):
    color_list = ['#a16031', '#f69121', '#ffe760', '#90d5e1', 
                  '#fab16b', '#1b518c', '#d92131',  '#fdf3c8', 
                  '#98272e', '#7eafdc', '#b4cdd6', '#fef3c3', 
                  '#a78eb9', '#a16158',  '#947f62', '#bbd660', 
                  '#98c2c8', '#221815', '#98999e', '#71592e', 
                  '#c5c6ca',  '#fce5c8', '#fadcd1', '#043440', 
                  '#feea93', '#e8ebb7', '#4e3f1f', '#fac6a3',  
                  '#feffff', '#c6c6ca', '#222d4d', '#ffffff', 
                  '#868b6c', '#b1b2b5', '#cc95a2',  '#812754', 
                  '#c7af2f', '#fefffe', '#e6dae4', '#221916', 
                  '#e7dae4', '#94d4e1',  '#2a2422', '#86909c', 
                  '#d5c3c5', '#a3bbc4', '#fbc6a4', '#cbbcd9', 
                  '#362b49',  '#7a6487', '#4d331c', '#937f61', 
                  '#987f7e', '#d5e2e9', '#211816', '#c4bdc4',  
                  '#b1b2b6', '#55c4cf', '#36baa4', '#4e6e74', 
                  '#fdf4c5', '#436a8c', '#928039',  '#fffffe', 
                  '#74c494', '#440f18', '#7d5997', '#cbbdd8', 
                  '#49a5ae', '#da2131',  '#aeba9d', '#afc2ca', 
                  '#da2130', '#4e6838', '#d7c3c5', '#77767b', 
                  '#f38472',  '#f7b4ab', '#221816', '#423366', 
                  '#d2b3ae', '#0066b0', '#93cc9e', '#e2e1e1', 
                  '#134d8c', '#c1547e', '#085e39', '#0066af', 
                  '#fce830', '#0265ae', '#d6eae5',  '#d2c3a2', 
                  '#f7b4ad', '#d7e2e9', '#018491', '#862c28', 
                  '#fdeb92', '#460e19',  '#927d84', '#dae5e7', 
                  '#73c594', '#98282d', '#a0877d', '#c7e8ec', 
                  '#413366',  '#f5bbc5', '#fdf3c4', '#231815', 
                  '#124e8d', '#99272e', '#f7c88e']


    cloth_color =  extract_dominant_color(image)
    final = find_closest_color_hsv(cloth_color,color_list) #db 存的

    #如果是黑色的話
    if (cloth_color[0]<50 and cloth_color[1] <50 and cloth_color[2] <50 ):
        cloth_color = [0,0,0]
        final = '#221816'
    
    return (rgb_to_hex(cloth_color), final)