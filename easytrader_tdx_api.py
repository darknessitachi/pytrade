# -*- coding:utf-8 -*-
import easytrader,time,datetime,os
import os
import subprocess
import tempfile
import time
import traceback
import win32api
import win32gui
from io import StringIO

import pandas as pd
import pyperclip
import win32com.client
import win32con
from PIL import ImageGrab

from easytrader import helpers
from easytrader.log import log

from winguiauto import (dumpWindow, dumpWindows, getWindowText,getParentWindow,activeWindow,
                        getWindowStyle,getListViewInfo, setEditText, clickWindow,getDictViewInfo,
                        click, closePopupWindows, findTopWindow,findSubWindow,
                        select_combobox,getEditText,get_combobox_id,get_valid_combobo_ids,
                        maxFocusWindow, minWindow, getTableData, sendKeyEvent)

# coding=utf-8
#import logging
#from .log import log
"""
from .gftrader import GFTrader
from .joinquant_follower import JoinQuantFollower
from .ricequant_follower import RiceQuantFollower


from .xq_follower import XueQiuFollower
from .xqtrader import XueQiuTrader
from .yhtrader import YHTrader
from .xczqtrader import XCZQTrader
"""
from easytrader.yh_clienttrader import YHClientTrader

import win32gui,win32con,win32api,struct
from winguiauto import (dumpWindow, dumpWindows,clickButton)
from easytrader_config0 import (HD,VA,LI,LOGIN_WINDOW_LEN,TRADE_WINDOW_LEN)


def int_code_to_stock_symbol(code):
    """
    code, int type
    """
    return '0'*(6-len(str(code)))+str(code)

def get_exist_hwnd(hwnd,wantedtext='',wantedclass='',exact_text=True):
    windows = dumpWindows(hwnd)
    print('exist_windows=',windows)
    wanted_hwnd = -1
    for window in windows:
        child_hwnd, window_text, window_class = window
        cond = True
        if wantedtext:
            cond = window_text==wantedtext
            if not exact_text:#包含即可
                cond = wantedtext in window_text
            if wantedclass:
                cond = cond and (window_class==wantedclass)
            else:
                pass
        else:
            if wantedclass:
                cond = window_class==wantedclass
            else:
                return -2
        if not exact_text and wantedtext:#包含即可
            cond = wantedtext in window_text
        
        if cond:
            wanted_hwnd = child_hwnd
            break
        else:
            pass
    return wanted_hwnd

    
        
class myYHClientTrader(YHClientTrader):
    enable_trade = False
    acc_id = '36005'
    yh_tdx_hwnd = 0 
    trade_hwnd = 0
    
    
    """
    
    def __init__(self):
        self.Title = '网上股票交易系统5.0'
        self.acc_id = self.update_acc_id()
    """  
    def is_enable_trade(self,is_trade=True):
        self.enable_trade = is_trade
        
    def set_title(self,title='网上股票交易系统5.0'):
        self.Title = title
        
        
    def prepare(self, config_path=None, user=None, password=None, exe_path='C:\中国银河证券双子星3.2\Binarystar.exe'):
        """
        登陆银河客户端
        :param config_path: 银河登陆配置文件，跟参数登陆方式二选一
        :param user: 银河账号
        :param password: 银河明文密码
        :param exe_path: 银河客户端路径
        :return:
        """
        if config_path is not None:
            account = helpers.file2dict(config_path)
            user = account['user']
            password = account['password']
        
        self.login(user, password, exe_path)
        
    
    
    def login(self, user, password, exe_path):
        #self.trade_main_hwnd = win32gui.FindWindow(0, self.Title)  # 交易窗口
        #print('trade_main_hwnd=',self.trade_main_hwnd)
        print('has_main_window=',self._has_main_window())
        print('_has_login_window=',self._has_login_window())
        if self._has_main_window():
            self._get_handles()
            log.info('检测到交易客户端已启动，连接完毕')
            return
        if not self._has_login_window():
            if not os.path.exists(exe_path):
                raise FileNotFoundError('在　{} 未找到应用程序，请用 exe_path 指定应用程序目录'.format(exe_path))
            subprocess.Popen(exe_path)
        # 检测登陆窗口
        for _ in range(30):
            print('_has_login_window1=',self._has_login_window())
            if self._has_login_window():
                break
            time.sleep(1)
        else:
            raise Exception('启动客户端失败，无法检测到登陆窗口')
        log.info('成功检测到客户端登陆窗口')
        #self._get_handles()

        # 登陆
        self._set_trade_mode()
        time.sleep(2)
        self._set_login_name(user)
        self._set_login_password(password)
        """
        for _ in range(10):
            self._set_login_verify_code()
            self._click_login_button()
            time.sleep(3)
            if not self._has_login_window():
                break
            #self._click_login_verify_code()
        """

        for i in range(100):
            print('i=',i)
            print('self._has_main_window=',self._has_main_window())
            if self._has_main_window():
                #self._get_handles()
                print('login the trade system')
                break
            self._set_login_verify_code()
            time.sleep(1)
            self._click_login_button()
            time.sleep(1)
        else:
            raise Exception('启动交易客户端失败')
        log.info('客户端登陆成功')
        
    def _set_trade_mode0(self):
        input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x016E)#0x4f4d)
        win32gui.SendMessage(input_hwnd, win32con.BM_CLICK, None, None)
    
    def _set_trade_mode(self):
        self._click_trade_only()

    def _set_login_name(self, user):
        time.sleep(0.5)
        input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x00EA)#0x5523)
        win32gui.SendMessage(input_hwnd, win32con.WM_SETTEXT, None, user)

    def _set_login_password(self, password):
        time.sleep(0.5)
        input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x00EC)#0x5534)
        #input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x00ED)#0x5534)  验证码
        win32gui.SendMessage(input_hwnd, win32con.WM_SETTEXT, None, password)
    
    def _grab_verify_code(self):
        verify_code_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x0170)#0x4c8)#0x80BA)#0x56ba)
        self._set_foreground_window(self.login_hwnd)
        time.sleep(1)
        rect = win32gui.GetWindowRect(verify_code_hwnd)
        print('rect=',rect)
        rect = (rect[0],rect[1],rect[2]+30,rect[3])
        print('rect1=',rect)
        return ImageGrab.grab(rect)
    
    def _set_login_verify_code(self):
        verify_code_image = self._grab_verify_code()
        image_path = tempfile.mktemp() + '.jpg'
        print('image_path=',image_path)
        verify_code_image.save(image_path)
        result = helpers.recognize_verify_code(image_path, 'yh_client')
        print('result=',result)
        time.sleep(0.2)
        self._input_login_verify_code(result)
        time.sleep(0.4)
    
    def _click_login_button(self):
        time.sleep(1)
        input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x1)
        #win32gui.SendMessage(input_hwnd, win32con.BM_CLICK, None, None)
        rect = win32gui.GetWindowRect(input_hwnd)
        self._mouse_click(rect[0] + 5, rect[1]+5)
        time.sleep(1)
        #tanchu_hwnd = win32gui.FindWindow(0, '关闭')# '消息标题:关于对证件有效期缺失的个人账户采取限制措施的公告')  # 交易窗口
        #tanchu_hwnd = findTopWindow()
        """
        tanchu_hwnd = 0
        print('tanchu_hwnd=',tanchu_hwnd)
        windows = dumpWindows(0)
        print('windows=',windows)
        for window in windows:
            #print(window)
            child_hwnd, window_text, window_class = window
            if '关闭' == window_text:
                tanchu_hwnd = child_hwnd
                break
        """
        #tanchu_hwnd0 = win32gui.FindWindow(0, '消息标题:关于对证件有效期缺失的个人账户采取限制措施的公告')  # 交易窗口
        title = '消息标题'
        tanchu_hwnd0 = get_exist_hwnd(hwnd=0,wantedtext=title,exact_text=False)
        print('tanchu_hwnd0=',tanchu_hwnd0)
        #closePopupWindows(tanchu_hwnd0, wantedText=None, wantedClass=None)
        time.sleep(0.5)
        #tanchu_hwnd = get_exist_hwnd(hwnd=tanchu_hwnd0, wantedtext='关闭',wantedclass='#32770')
        #print('tanchu_hwnd=',tanchu_hwnd)
        #time.sleep(0.5)
        if tanchu_hwnd0>0:
            click(tanchu_hwnd0)
            win32gui.SendMessage(tanchu_hwnd0, win32con.WM_CLOSE, None, None)
            time.sleep(0.2)
            #rect = win32gui.GetWindowRect(tanchu_hwnd)
            #self._mouse_click(rect[0] + 5, rect[1]+5)
    
    def _click_login_verify_code(self):
        input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x80BA)#0x56ba)
        rect = win32gui.GetWindowRect(input_hwnd)
        self._mouse_click(rect[0] + 5, rect[1] -2)
    
    def _click_trade_only(self):
        input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x016E)
        rect = win32gui.GetWindowRect(input_hwnd)
        self._mouse_click(rect[0] + 20, rect[1]+10)
    
    def _input_login_verify_code(self, code):
        input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x00ED)# 0x56b9)
        win32gui.SendMessage(input_hwnd, win32con.WM_SETTEXT, None, code)
        
    def _close_login_window(self, code):
        input_hwnd = win32gui.GetDlgItem(self.login_hwnd, 0x016F)# close window
        win32gui.SendMessage(input_hwnd, win32con.WM_SETTEXT, None, code)
    
    def _get_handles(self):
        return 
        
    def _get_handles0(self):
        trade_main_hwnd = win32gui.FindWindow(0, self.Title)  # 交易窗口
        print('trade_main_hwnd=',trade_main_hwnd)
        operate_frame_hwnd = win32gui.GetDlgItem(trade_main_hwnd, 59648)  # 操作窗口框架
        operate_frame_afx_hwnd = win32gui.GetDlgItem(operate_frame_hwnd, 59648)  # 操作窗口框架
        hexin_hwnd = win32gui.GetDlgItem(operate_frame_afx_hwnd, 129)
        scroll_hwnd = win32gui.GetDlgItem(hexin_hwnd, 200)  # 左部折叠菜单控件
        tree_view_hwnd = win32gui.GetDlgItem(scroll_hwnd, 129)  # 左部折叠菜单控件

        # 获取委托窗口所有控件句柄
        win32api.PostMessage(tree_view_hwnd, win32con.WM_KEYDOWN, win32con.VK_F1, 0)
        time.sleep(0.5)

        # 买入相关
        entrust_window_hwnd = win32gui.GetDlgItem(operate_frame_hwnd, 59649)  # 委托窗口框架
        self.buy_stock_code_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1032)  # 买入代码输入框
        self.buy_price_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1033)  # 买入价格输入框
        self.buy_amount_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1034)  # 买入数量输入框
        self.buy_btn_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1006)  # 买入确认按钮
        self.refresh_entrust_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 32790)  # 刷新持仓按钮
        entrust_frame_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1047)  # 持仓显示框架
        entrust_sub_frame_hwnd = win32gui.GetDlgItem(entrust_frame_hwnd, 200)  # 持仓显示框架
        self.position_list_hwnd = win32gui.GetDlgItem(entrust_sub_frame_hwnd, 1047)  # 持仓列表
        win32api.PostMessage(tree_view_hwnd, win32con.WM_KEYDOWN, win32con.VK_F2, 0)
        time.sleep(0.5)

        # 卖出相关
        sell_entrust_frame_hwnd = win32gui.GetDlgItem(operate_frame_hwnd, 59649)  # 委托窗口框架
        self.sell_stock_code_hwnd = win32gui.GetDlgItem(sell_entrust_frame_hwnd, 1032)  # 卖出代码输入框
        self.sell_price_hwnd = win32gui.GetDlgItem(sell_entrust_frame_hwnd, 1033)  # 卖出价格输入框
        self.sell_amount_hwnd = win32gui.GetDlgItem(sell_entrust_frame_hwnd, 1034)  # 卖出数量输入框
        self.sell_btn_hwnd = win32gui.GetDlgItem(sell_entrust_frame_hwnd, 1006)  # 卖出确认按钮

        # 撤单窗口
        win32api.PostMessage(tree_view_hwnd, win32con.WM_KEYDOWN, win32con.VK_F3, 0)
        time.sleep(0.5)
        cancel_entrust_window_hwnd = win32gui.GetDlgItem(operate_frame_hwnd, 59649)  # 撤单窗口框架
        self.cancel_stock_code_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 3348)  # 卖出代码输入框
        self.cancel_query_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 3349)  # 查询代码按钮
        self.cancel_buy_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 30002)  # 撤买
        self.cancel_sell_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 30003)  # 撤卖

        chexin_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 1047)
        chexin_sub_hwnd = win32gui.GetDlgItem(chexin_hwnd, 200)
        self.entrust_list_hwnd = win32gui.GetDlgItem(chexin_sub_hwnd, 1047)  # 委托列表
        
    def _has_login_window(self):
        """
        for title in [' - 广州电信', ' - 广州电信 - 广州电信',' - 北京电信', ' - 北京电信 - 北京电信']:
            self.login_hwnd = win32gui.FindWindow(None, title)
            if self.login_hwnd != 0:
                return True
        """
        self.login_hwnd = win32gui.FindWindow(None, self.Title)
        return self.login_hwnd!=0
            
    def _has_main_window0(self):
        try:
            self._get_handles()
        except:
            return False
        return True
    
    def _has_main_window1(self):
        title = '通达信网上交易V6'
        trade_hwnd = win32gui.FindWindow(None, title)
        print('trade_hwnd=',trade_hwnd)
        if trade_hwnd:
            windows = dumpWindows(trade_hwnd)
            print('window_len=',len(windows))
            return len(windows)>17
        else:
            return False
        
    def _has_main_window(self):
        title = '中国银河证券海王星V2'
        #trade_hwnd0 = win32gui.FindWindow(None, title)
        yh_tdx_hwnd = get_exist_hwnd(hwnd=0,wantedtext=title,exact_text=False)
        #trade_hwnd = win32gui.FindWindow(None, title)
        print('yh_tdx_hwnd=',yh_tdx_hwnd)
        #LOGIN_WINDOW_LEN = 38
        #TRADE_WINDOW_LEN = 7
        #TRADE_WINDOW_LEN1 = -5
        if yh_tdx_hwnd>0:
            windows = dumpWindow(yh_tdx_hwnd)
            print('window_len=',len(windows))
            self.yh_tdx_hwnd = yh_tdx_hwnd
            return (len(windows)== TRADE_WINDOW_LEN)# or (len(windows)==TRADE_WINDOW_LEN1)
        else:
            return False
        
    def _has_yh_trade_window(self):
        if self.yh_tdx_hwnd>0:
            windows = dumpWindow(self.yh_tdx_hwnd)
            print('_has_trade_windows=', windows)
            yh_tdx_hwnd = get_exist_hwnd(hwnd=self.yh_tdx_hwnd,wantedtext=None,wantedclass='Afx:5bc0000:3:10003:900010:10027',exact_text=True)
            print('yh_trade_window=',yh_tdx_hwnd)
            if yh_tdx_hwnd>0:
                self.yh_tdx_hwnd = yh_tdx_hwnd
                return True 
            else:
                return False
        else:
            return False
    
    def close_window(self,hwnd):#, extra):
        if hwnd and win32gui.IsWindowVisible(hwnd):
            #if 'Chrome' in win32gui.GetWindowText(hwnd):
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        
        return
        
    def get_add_acc_handles(self):
        #trade_main_hwnd = win32gui.FindWindow(0, self.Title)  # 交易窗口
        #operate_frame_hwnd = win32gui.GetDlgItem(trade_main_hwnd, 59648)  # 操作窗口框架
        tool_menu_hwnd = win32gui.GetDlgItem(self.trade_main_hwnd, 59392)  # 工具栏窗口框架
        tool_menu_hwnd_sub = dumpWindow(tool_menu_hwnd)
        add_acc_hwnd = win32gui.GetDlgItem(tool_menu_hwnd_sub[0][0], 1691)  # 工具栏添加账户按钮
        
        clickButton(add_acc_hwnd)
        new_add_acc_login_hwnd = win32gui.FindWindow(0, '用户登录')  # 交易窗口
        print('new_add_acc_login_hwnd=',new_add_acc_login_hwnd)
        return add_acc_hwnd
        """
        operate_frame_afx_hwnd = win32gui.GetDlgItem(operate_frame_hwnd, 59648)  # 操作窗口框架
        hexin_hwnd = win32gui.GetDlgItem(operate_frame_afx_hwnd, 129)
        scroll_hwnd = win32gui.GetDlgItem(hexin_hwnd, 200)  # 左部折叠菜单控件
        tree_view_hwnd = win32gui.GetDlgItem(scroll_hwnd, 129)  # 左部折叠菜单控件

        # 获取委托窗口所有控件句柄
        win32api.PostMessage(tree_view_hwnd, win32con.WM_KEYDOWN, win32con.VK_F1, 0)
        time.sleep(0.5)

        # 买入相关
        entrust_window_hwnd = win32gui.GetDlgItem(operate_frame_hwnd, 59649)  # 委托窗口框架
        self.buy_stock_code_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1032)  # 买入代码输入框
        self.buy_price_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1033)  # 买入价格输入框
        self.buy_amount_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1034)  # 买入数量输入框
        self.buy_btn_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1006)  # 买入确认按钮
        self.refresh_entrust_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 32790)  # 刷新持仓按钮
        entrust_frame_hwnd = win32gui.GetDlgItem(entrust_window_hwnd, 1047)  # 持仓显示框架
        entrust_sub_frame_hwnd = win32gui.GetDlgItem(entrust_frame_hwnd, 200)  # 持仓显示框架
        self.position_list_hwnd = win32gui.GetDlgItem(entrust_sub_frame_hwnd, 1047)  # 持仓列表
        win32api.PostMessage(tree_view_hwnd, win32con.WM_KEYDOWN, win32con.VK_F2, 0)
        time.sleep(0.5)

        # 卖出相关
        sell_entrust_frame_hwnd = win32gui.GetDlgItem(operate_frame_hwnd, 59649)  # 委托窗口框架
        self.sell_stock_code_hwnd = win32gui.GetDlgItem(sell_entrust_frame_hwnd, 1032)  # 卖出代码输入框
        self.sell_price_hwnd = win32gui.GetDlgItem(sell_entrust_frame_hwnd, 1033)  # 卖出价格输入框
        self.sell_amount_hwnd = win32gui.GetDlgItem(sell_entrust_frame_hwnd, 1034)  # 卖出数量输入框
        self.sell_btn_hwnd = win32gui.GetDlgItem(sell_entrust_frame_hwnd, 1006)  # 卖出确认按钮

        # 撤单窗口
        win32api.PostMessage(tree_view_hwnd, win32con.WM_KEYDOWN, win32con.VK_F3, 0)
        time.sleep(0.5)
        cancel_entrust_window_hwnd = win32gui.GetDlgItem(operate_frame_hwnd, 59649)  # 撤单窗口框架
        self.cancel_stock_code_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 3348)  # 卖出代码输入框
        self.cancel_query_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 3349)  # 查询代码按钮
        self.cancel_buy_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 30002)  # 撤买
        self.cancel_sell_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 30003)  # 撤卖

        chexin_hwnd = win32gui.GetDlgItem(cancel_entrust_window_hwnd, 1047)
        chexin_sub_hwnd = win32gui.GetDlgItem(chexin_hwnd, 200)
        self.entrust_list_hwnd = win32gui.GetDlgItem(chexin_sub_hwnd, 1047)  # 委托列表
        """
        
    def logout(self):
        #trade_main_hwnd = win32gui.FindWindow(0, self.Title)  # 交易窗口
        self.close_window(self.trade_main_hwnd)
        print('exit trade windows')
        return 
    
    def is_right_acc(self,acc_id):
        wantedtext = VA[LI[0]]['A1']
        if acc_id==LI[0]:
            pass
        elif acc_id==LI[1]:
            wantedtext = VA[LI[1]]['A1']
        else:
            return False
        hnwd = get_exist_hwnd(self.trade_main_hwnd, wantedtext)
        return hnwd>0
    
    def get_acc_id(self):
        valid_acc_ids = LI
        acc_id = 0
        for acc_id in valid_acc_ids:
            if self.is_right_acc(acc_id):
                return acc_id
            else:
                pass
        return acc_id
    
    def update_acc_id(self):
        self.acc_id = self.get_acc_id()
    
    def change_acc(self):
        trade_main_hwnd = win32gui.FindWindow(0, self.Title)  # 交易窗口
        #is_acc = self.is_acc_36005()
        #acc_id = self.update_acc_id()
        #acc_dict = {'36005':'331600036005','38736':'331600038736'}
        #changed = False
        pre_acc_id = self.acc_id
        if trade_main_hwnd and self.acc_id:
            self.logout()
            if pre_acc_id==LI[0]:
                #changed = True
                print('Will change to ACC: ',LI[1])
                self.prepare(user=HD + LI[1], password=VA[LI[1]]['A2'])  
                #self.acc_id = LI[1]
            elif pre_acc_id==LI[1]:
                #changed = True
                print('Will change to ACC: ',LI[0])
                self.prepare(user=HD + LI[0], password=VA[LI[0]]['A2'])
                #self.acc_id = LI[0]  
            else:
                pass
        self.update_acc_id()
        return pre_acc_id!=self.acc_id
    
    def get_all_position(self):
        pos_dict = dict()
        pos_dict[self.get_acc_id()] = self.get_my_position()
        self.change_acc()
        pos_dict[self.get_acc_id()] = self.get_my_position()
        return pos_dict
    
    
    def get_my_position(self):
        #单账户
        print('111')
        pos_dict = {}
        my_pos = {}
        for stock in self.position:
            stock_code = int_code_to_stock_symbol(stock['证券代码'])
            stock['证券代码'] = stock_code
            pos_dict[stock_code] = stock
        #my_pos[self.get_acc_id()] = pos_dict 
        return pos_dict
    
    def get_my_all_position(self):
        #多账户
        print('222')
        #print(self.position)
        my_pos = self.get_all_position()
        pos = {}
        for acc_id in list(my_pos.keys()):
            pos_dict = {}
            for stock in my_pos[acc_id]:
                stock_code = int_code_to_stock_symbol(stock['证券代码'])
                stock['证券代码'] = stock_code
                pos_dict[stock_code] = stock
            print('pos_dict=',pos_dict)
            pos[acc_id] = pos_dict
        return pos
                
            
    
    def is_holding_stock(self,acc_id,stock):
        if self.acc_id==acc_id:
            pass
        else:
            self.change_acc()
        this_acc_positon = self.position
        print('this_acc_positon=',this_acc_positon)
        for pos in this_acc_positon:
            code = pos['证券代码']
            symbol = int_code_to_stock_symbol(code)
            if stock==symbol:
                return True
        return False
    
    def _order_stock(self,stock_code, price, amount,direct='S'):
        is_send_order = False
        if direct=='S' and self.enable_trade:
            is_send_order = self.sell(stock_code, price, amount)
        elif direct=='B' and self.enable_trade:
            is_send_order = self.buy(stock_code, price, amount)
        else:
            pass
        time.sleep(10)
        closePopupWindows(self.trade_main_hwnd)
        return is_send_order
    
    
    
    def get_absolute_order_price(self,stock_code,direct='S'):
        last_close = 10
        return
    
    def order_acc_stock(self,stock_code, price, amount,acc_id=LI[0],direct='S',
                        is_absolute_order=False,limit_price=None):
        """
        For single account
        """
        if is_absolute_order and limit_price: #跌停价卖，涨停价买
                price = limit_price
        if acc_id and acc_id==self.acc_id:
            pass
        else:
            self.change_acc()
        return self._order_stock(stock_code, price, amount,direct)
    
    def get_available_money(self):
        available_money = 0
        return available_money
    
    def exchange_stocks(self,acc_id,position, replaced_stock,replaced_stock_price, target_stock,
                         target_stock_price,sell_then_buy=True,exchange_rate=1.0,absolute_order=False):
        
        if self.is_holding_stock(acc_id, replaced_stock):
            pass
        else:
            print('There is not stock %s in this account %s ' % (replaced_stock,acc_id))
            return False
        available_money = self.get_available_money()
        sleep_seconds = 1
        print(position[acc_id][replaced_stock]['可用余额'])
        replaced_stock_amount = int((position[acc_id][replaced_stock]['可用余额'] * exchange_rate//100) * 100)
        target_stock_amount = int((replaced_stock_amount*replaced_stock_price/target_stock_price//100)*100)
        if sell_then_buy and replaced_stock_amount>100 and target_stock_amount>100:#先卖后买
            print('Plan to sell %s %s, and then buy %s %s' % (replaced_stock_amount,replaced_stock,target_stock_amount,target_stock))
            sell_replace_stock = self.order_acc_stock(replaced_stock, replaced_stock_price, 
                    replaced_stock_amount, acc_id, direct='S', is_absolute_order=absolute_order, limit_price=None)
            time.sleep(sleep_seconds)
            if sell_replace_stock:
                buy_target_stock = self.order_acc_stock(target_stock, target_stock_price, 
                    target_stock_amount, acc_id, direct='B', is_absolute_order=absolute_order, limit_price=None)
                print('Completed exchange order: sell then buy')
                return buy_target_stock
            else:
                return False
        elif not sell_then_buy and replaced_stock_amount>100 and target_stock_amount>100: #先买后卖
            print('Plan to buy %s %s, and then sell %s %s' % (target_stock_amount,target_stock,replaced_stock_amount,replaced_stock))
            if available_money>target_stock_amount*target_stock_price:
                buy_target_stock = self.order_acc_stock(target_stock, target_stock_price, 
                    target_stock_amount, acc_id, direct='B', is_absolute_order=absolute_order, limit_price=None)
                time.sleep(sleep_seconds)
                if buy_target_stock:
                    sell_replace_stock = self.order_acc_stock(replaced_stock, replaced_stock_price, 
                    replaced_stock_amount, acc_id, direct='S', is_absolute_order=absolute_order, limit_price=None)
                    print('Completed exchange order: sell then buy')
                    return replaced_stock
            else:
                return False
        else:
            print('Try to exchange stock, but failed ')
            return False
    
    def get_stock_exit_datas(self,position):
        return
    
    def get_stock_buy_datas(self,position,avaiable_money):
        return
    
    def order_acc_stocks(self,stock_order_datas,direct='S'):
        """
        For multi-account
        
        stock_order_datas = {'12345':[
        [stock_code, price, amount,direction,is_absolute_order,topest_price,lowest_price],],
        '12346':[[stock_code, price, amount,direction,is_absolute_order,topest_price,lowest_price],]}
        """
        def get_stock_order_price(stock):
            #stock=[stock_code, price, amount,direction,is_absolute_order,topest_price,lowest_price]
            direction =stock[3]
            is_absolute_order = stock[4]
            price = stock[1]
            if is_absolute_order and direction=='B':
                price = stock[5]
            elif is_absolute_order and direction=='S':
                price = stock[6]
            else:
                pass
            return price,direction
        order_num = 0
        if self.enable_trade:
            pass
        else:
            return order_num
        acc_ids = list(stock_order_datas.keys())
        valid_acc_ids = list(set(LI).intersection(set(acc_ids)))
        if len(valid_acc_ids)==1:
            if self.is_right_acc(valid_acc_ids[0]):
                pass
            else:
                self.change_acc()
            for stock in stock_order_datas[valid_acc_ids[0]]:
                price,direct = get_stock_order_price(stock)
                self._order_stock(stock[0], price, stock[2],direct)
                order_num = order_num + 1
        elif len(valid_acc_ids)==2:
            this_acc_id = self.get_acc_id()
            for stock in stock_order_datas[this_acc_id]:
                price,direct = get_stock_order_price(stock)
                self._order_stock(stock[0], price, stock[2],direct)
                order_num = order_num + 1
            valid_acc_ids.pop(valid_acc_ids.index(this_acc_id))
            second_acc_id = valid_acc_ids[0]
            self.change_acc()
            for stock1 in stock_order_datas[second_acc_id]:
                price,direct = get_stock_order_price(stock)
                self._order_stock(stock1[0], price, stock1[2],direct)
                order_num = order_num + 1
        else:
            order_num = -1
        return order_num
    
class Orderdatas():
    def __init__(self,position_datas= {},potential_buy_stocks=[]):
        self.pos = position_datas
        self.order_datas = {}
        self.potentials = potential_buy_stocks
        self.exit_enable = False
        self.buy_enable = False
    """
    all position: {'38736': [{'可用余额': 50, '买入冻结': 0, '当前持仓': 50, '证券名称': '四维图新', '股份余额': 50, '交易市场': '深Ａ', '参考市价': 19.74, '参考成本价': -42.32, '盈亏比例(%)': 0.0, '证券代码': 2405, '卖出冻结': 0, '参考盈亏': 3103.02, '参考市值': 987.0, '股东代码': '0148358729'}, {'可用余额': 0, '买入冻结': 0, '当前持仓': 600, '证券名称': '岭南园林', '股份余额': 600, '交易市场': '深Ａ', '参考市价': 28.41, '参考成本价': 28.34, '盈亏比例(%)': 0.247, '证券代码': 2717, '卖出冻结': 0, '参考盈亏': 42.0, '参考市值': 17046.0, '股东代码': '0148358729'}, {'可用余额': 1600, '买入冻结': 0, '当前持仓': 1600, '证券名称': '朗源股份', '股份余额': 1600, '交易市场': '深Ａ', '参考市价': 8.26, '参考成本价': 8.402999999999999, '盈亏比例(%)': -1.703, '证券代码': 300175, '卖出冻结': 0, '参考盈亏': -229.0, '参考市值': 13216.0, '股东代码': '0148358729'}, {'可用余额': 0, '买入冻结': 0, '当前持仓': 3000, '证券名称': '健康元', '股份余额': 3000, '交易市场': '沪Ａ', '参考市价': 9.18, '参考成本价': 10.869000000000002, '盈亏比例(%)': -15.54, '证券代码': 600380, '卖出冻结': 0, '参考盈亏': -5067.16, '参考市值': 27540.0, '股东代码': 'A355519785'}, {'可用余额': 0, '买入冻结': 0, '当前持仓': 400, '证券名称': '恒生电子', '股份余额': 400, '交易市场': '沪Ａ', '参考市价': 45.57, '参考成本价': 62.231, '盈亏比例(%)': -26.772, '证券代码': 600570, '卖出冻结': 0, '参考盈亏': -6664.26, '参考市值': 18228.0, '股东代码': 'A355519785'}, {'可用余额': 600, '买入冻结': 0, '当前持仓': 1700, '证券名称': '邦宝益智', '股份余额': 1700, '交易市场': '沪Ａ', '参考市价': 21.59, '参考成本价': 31.996, '盈亏比例(%)': -32.524, '证券代码': 603398, '卖出冻结': 0, '参考盈亏': -17691.01, '参考市值': 36703.0, '股东代码': 'A355519785'}],
     '36005': [{'可用余额': 0, '买入冻结': 0, '当前持仓': 900, '证券名称': '京山轻机', '股份余额': 900, '交易市场': '深Ａ', '参考市价': 13.28, '参考成本价': 16.24, '盈亏比例(%)': -18.227, '证券代码': 821, '卖出冻结': 0, '参考盈亏': -2664.0, '参考市值': 11952.0, '股东代码': '0130010635'}, {'可用余额': 0, '买入冻结': 0, '当前持仓': 1100, '证券名称': '中科新材', '股份余额': 1100, '交易市场': '深Ａ', '参考市价': 16.94, '参考成本价': 18.64, '盈亏比例(%)': -9.12, '证券代码': 2290, '卖出冻结': 0, '参考盈亏': -1870.0, '参考市值': 18634.0, '股东代码': '0130010635'}, {'可用余额': 200, '买入冻结': 0, '当前持仓': 200, '证券名称': '八菱科技', '股份余额': 200, '交易市场': '深Ａ', '参考市价': 28.19, '参考成本价': 29.125, '盈亏比例(%)': -3.21, '证券代码': 2592, '卖出冻结': 0, '参考盈亏': -187.0, '参考市值': 5638.0, '股东代码': '0130010635'}, {'可用余额': 0, '买入冻结': 0, '当前持仓': 400, '证券名称': '索菱股份', '股份余额': 400, '交易市场': '深Ａ', '参考市价': 33.18, '参考成本价': 33.2, '盈亏比例(%)': -0.06, '证券代码': 2766, '卖出冻结': 0, '参考盈亏': -8.0, '参考市值': 13272.0, '股东代码': '0130010635'}, {'可用余额': 1300, '买入冻结': 0, '当前持仓': 1300, '证券名称': '朗玛信息', '股份余额': 1300, '交易市场': '深Ａ', '参考市价': 27.75, '参考成本价': 27.838, '盈亏比例(%)': -0.318, '证券代码': 300288, '卖出冻结': 0, '参考盈亏': -115.0, '参考市值': 36075.0, '股东代码': '0130010635'}, {'可用余额': 300, '买入冻结': 0, '当前持仓': 300, '证券名称': '天和防务', '股份余额': 300, '交易市场': '深Ａ', '参考市价': 25.29, '参考成本价': 26.789, '盈亏比例(%)': -5.596, '证券代码': 300397, '卖出冻结': 0, '参考盈亏': -449.73, '参考市值': 7587.0, '股��代码': '0130010635'}, {'可用余额': 0, '买入冻结': 0, '当前持仓': 1900, '证券名称': '暴风集团', '股份余额': 1900, '交易市场': '深Ａ', '参考市价': 24.16, '参考成本价': 23.926, '盈亏比例(%)': 0.976, '证券代码': 300431, '卖出冻结': 0, '参考盈亏': 443.69, '参考市值': 45904.0, '股东代码': '0130010635'}, {'可用余额': 43, '买入冻结': 0, '当前持仓': 43, '证券名称': '美康生物', '股份余额': 43, '交易市场': '深Ａ', '参考市价': 21.73, '参考成本价': 17.24, '盈亏比例(%)': 26.046, '证券代码': 300439, '卖出冻结': 0, '参考盈亏': 193.08, '参考市值': 934.39, '股东代码': '0130010635'}, {'可用余额': 1200, '买入冻结': 0, '当前持仓': 1200, '证券名称': '乐心医疗', '股份余额': 1200, '交易市场': '深Ａ', '参考市价': 28.6, '参考成本价': 28.346, '盈亏比例(%)': 0.898, '证券代码': 300562, '卖出冻结': 0, '参考盈亏': 305.3, '参考市值': 34320.0, '股东代码': '0130010635'}, {'可用余额': 0, '买入冻结': 0, '当前持仓': 2400, '证券名称': '浙江龙盛', '股份余额': 2400, '交易市场': '沪Ａ', '参考市价': 9.56, '参考成本价': 9.654, '盈亏比例(%)': -0.977, '证券代码': 600352, '卖出冻结': 0, '参考盈亏': -226.46, '参考市值': 22944.0, '股东代码': 'A732980330'}, {'可用余额': 60, '买入冻结': 0, '当前持仓': 1460, '证券名称': '南京银行', '股份余额': 1460, '交易市场': '沪Ａ', '参考市价': 11.2, '参考成本价': 9.486, '盈亏比例(%)': 18.067, '证券代码': 601009, '卖出冻结': 0, '参考盈亏': 2502.28, '参考市值': 16352.0, '股东代码': 'A732980330'}]}    
    """
    
    def set_exit(self,is_exit):
        self.exit_enable = exit
        
    def set_buy(self,is_buy):
        self.buy_enable = is_buy
        
    
    def update_position(self,position_datas):
        self.pos = position_datas
        return    
    
    def update_potential_stocks(self,potential_buy_stocks):
        self.potentials = potential_buy_stocks
        return    
    
    def update_order_datas(self,order_datas):
        """
        stock_order_datas = {'12345':[
        [stock_code, price, amount,direction,is_absolute_order,topest_price,lowest_price],],
        '12346':[[stock_code, price, amount,direction,is_absolute_order,topest_price,lowest_price],]}
        """
        if self.order_datas:
            existing_acc_ids = list(self.order_datas.keys())
            these_acc_ids = list(order_datas.keys())
            for acc_id in these_acc_ids:
                if acc_id in existing_acc_ids:
                    self.order_datas[acc_id] = self.order_datas[acc_id] + order_datas[acc_id]
                else:
                    self.order_datas[acc_id] = order_datas[acc_id]
        else:
            self.order_datas = exit_datas
        return
    
    def delete_order_datas(self,delete_orders):
        if self.order_datas:
            existing_acc_ids = list(self.order_datas.keys())
            these_acc_ids = list(delete_orders.keys())
            for acc_id in these_acc_ids:
                if acc_id in existing_acc_ids:
                    self.order_datas[acc_id] = list(set(self.order_datas[acc_id]).difference(set(order_datas[acc_id])))
                else:
                    pass
        else:
            pass
        return
    
    def get_stock_exit_datas(self,position):
        exit_datas = {}
        if self.exit_enable:
            pass
        else:
            return exit_datas
        #to get exit datas
        if exit_datas:
            self.update_order_datas(order_datas=exit_datas)
        return
    
    def get_stock_buy_datas(self,position,avaiable_money):
        buy_datas = {}
        if self.exit_enable:
            pass
        else:
            return buy_datas
        #To get but datas
        if buy_datas:
            self.update_order_datas(order_datas=buy_datas)
        return buy_datas
    
    def position_change(self,acc_id):
        return
    
    def position_optimize(self):
        return
    
class Order():
    def __init__(self):
        self.acc = '36005'
        self.stock = '300588'
        self.price = 0.0
        self.amount = 100
        self.direct = 'S'
        self.status = 0   #0-100, 100 will order all
        

class Orderdata():
    def __init__(self):
        self.orderdatas = {}        
           
def use(broker, debug=True, **kwargs):
    """用于生成特定的券商对象
    :param broker:券商名支持 ['yh', 'YH', '银河'] ['gf', 'GF', '广发']
    :param debug: 控制 debug 日志的显示, 默认为 True
    :param initial_assets: [雪球参数] 控制雪球初始资金，默认为一百万
    :return the class of trader

    Usage::

        >>> import easytrader
        >>> user = easytrader.use('xq')
        >>> user.prepare('xq.json')
    """
    if not debug:
        log.setLevel(logging.INFO)
    if broker.lower() in ['yh', '银河']:
        return YHTrader(debug=debug)
    elif broker.lower() in ['yh_client', '银河客户端']:
        return myYHClientTrader()
    else:
        pass



