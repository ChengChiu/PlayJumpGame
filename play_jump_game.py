"""
使用方法：
1.打开模拟器，运行微信，进入跳一跳
2.开始新一局，进入等待起跳的界面。（确保可以看到小人）
3.运行此脚本，看到提示"鼠标移动到左上角"，将鼠标移动到游戏区域的左上角，保持1秒。
    看到提示"鼠标移动到右下角"，将鼠标移动到游戏区域的右下角，保持1秒。
4.脚本开始自动玩游戏
"""

import win32api
import win32con
from ctypes import *
import time
import random

from PIL import ImageGrab

"""
请调整rate值。
rate为按压时间的放大倍率，1为不变，大于1为放大，小于1为缩小。

调整方法：
    小人跳得过远就改小一些，反之则改近一些
    精确度越高越好，建议从小数点后一位开始调，精确到小数点后三位
"""
rate = 1.236


class POINT(Structure):
    _fields_ = [("x", c_ulong), ("y", c_ulong)]


def get_mouse_point():
    """
    获取鼠标位置
    :return: dict，鼠标横纵坐标
    """
    po = POINT()
    windll.user32.GetCursorPos(byref(po))
    return int(po.x), int(po.y)


def mouse_move(x, y):
    """
    移动鼠标位置
    :param x: int, 目的横坐标
    :param y: int, 目的纵坐标
    :return: None
    """
    windll.user32.SetCursorPos(x, y)


def mouse_click(x=None, y=None):
    """
    模拟鼠标点击
    :param x: int, 鼠标点击位置横坐标
    :param y: int, 鼠标点击位置纵坐标
    :return: None
    """
    if not x is None and not y is None:
        mouse_move(x, y)
        time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def mouse_pclick(x=None, y=None, press_time=0.0):
    """
    模拟式长按鼠标
    :param x: int, 鼠标点击位置横坐标
    :param y: int, 鼠标点击位置纵坐标
    :param press_time: float, 点击时间，单位秒
    :return: None
    """
    if not x is None and not y is None:
        mouse_move(x, y)
        time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(press_time)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def get_static_mouse_point():
    """
    获取鼠标稳定的位置
    :return: dict，鼠标横纵坐标
    """
    last = get_mouse_point()
    while True:
        time.sleep(0.5)
        current = get_mouse_point()
        if last == current:
            return current
        last = current


def grab(x1, y1, x2, y2):
    """
    以点(x1,y1)为左上角，以点(x2,y2)为右下角截图
    :param x1: int, 左上角横坐标
    :param y1: int, 左上角纵坐标
    :param x2: int, 右下角横坐标
    :param y2: int, 右下角纵坐标
    :return: ImageGrab对象, 截图
    """
    im = ImageGrab.grab((x1, y1, x2, y2))
    return im


def get_role_x(im):
    """
    获得角色的x轴位置
    :param im: ImageGrab对象，截图
    :return: int，角色x轴位置
    """
    pix = im.load()
    width = im.size[0]
    height = im.size[1]
    sum = 0
    count = 0
    for y in range(height):
        for x in range(width):
            r, g, b = pix[x, y]
            if 54 <= r <= 56 and 59 <= g <= 61 and 101 <= b <= 103:
                sum += x
                count += 1
        if count > 0:
            return int(sum / count)
    return 0


def get_start_x(im, middle_x, end_x, no_turn=True):
    """
    获得起跳位置
    :param im: ImageGrab对象，截图
    :param middle_x: int，对称轴位置
    :param end_x: int，落点位置
    :param no_turn: bool，是否转弯
    :return: int，起跳位置
    """
    if no_turn:
        return get_role_x(im)
    else:
        if end_x > middle_x:
            return middle_x - (end_x - middle_x)
        else:
            return middle_x + (middle_x - end_x)


def get_end_x(im, middle_x, jump_right=True):
    """
    获得落点位置
    :param im: ImageGrab对象，截图
    :param middle_x: int，对称轴位置
    :param jump_right: bool，是否是向右跳的
    :return: int，落点位置
    """
    pix = im.load()
    width = im.size[0]
    height = im.size[1]

    if jump_right:
        for y in range(height):
            avgR, avgG, avgB = pix[0, y]
            sum = 0
            count = 0
            for x in range(middle_x + 10, width):
                r, g, b = pix[x, y]
                if abs(r - avgR) > 20 or abs(g - avgG) > 20 or abs(b - avgB) > 20:
                    sum += x
                    count += 1
            if count > 0:
                return int(sum / count)
    else:
        for y in range(height):
            avgR, avgG, avgB = pix[0, y]
            sum = 0
            count = 0
            for x in range(middle_x - 10):
                r, g, b = pix[x, y]
                if abs(r - avgR) > 20 or abs(g - avgG) > 20 or abs(b - avgB) > 20:
                    sum += x
                    count += 1
            if count > 0:
                return int(sum / count)
    return 0


def is_special(im, end_x):
    """
    判断是否为特殊方块
    :param im: ImageGrab对象，截图
    :param end_x: int，落点位置
    :return: bool，是否为特殊方块
    """
    pix = im.load()
    width = im.size[0]
    height = im.size[1]

    for y in range(height):
        r, g, b = pix[end_x + 5, y]
        if r == 244 and g == 138 and b == 39:
            return True
        r, g, b = pix[end_x, y]
        if r == 239 and g == 118 and b == 119:
            return True
    return False


if __name__ == '__main__':
    """
    获取截图区域
    """
    print("鼠标移动到左上角")
    time.sleep(1)
    upleft = get_static_mouse_point()
    print("OK")
    time.sleep(0.5)
    print("鼠标移动到右下角")
    time.sleep(1)
    downright = get_static_mouse_point()
    print("OK")

    jump_right = True

    # 计算对称轴位置
    im = grab(upleft[0], upleft[1], downright[0], downright[1])
    start_x = get_role_x(im)
    end_x = get_end_x(im, jump_right)
    middle_x = int((start_x + end_x) / 2)

    while True:
        # 截图
        im = grab(upleft[0], upleft[1], downright[0], downright[1])

        # 获取落点位置
        time.sleep(0.2)
        last_jump_right = jump_right
        jump_right = get_role_x(im) < middle_x
        end_x = get_end_x(im, middle_x, jump_right)

        # 获取起跳点位置
        time.sleep(0.2)
        start_x = get_start_x(im, middle_x, end_x, jump_right == last_jump_right)

        # 判断落点是否为特殊方块
        time.sleep(0.2)
        special_flag = is_special(im, end_x)

        # 模拟点击
        press_time = abs(start_x - end_x) / 400.0
        press_time *= rate
        p = get_mouse_point()
        mouse_pclick(downright[0] - int(random.uniform(10, 50)), downright[1] - int(random.uniform(10, 50)), press_time)
        mouse_move(p[0], p[1])

        # 如果是特殊方块，等待两秒
        if special_flag:
            time.sleep(2)
        time.sleep(1.5)

