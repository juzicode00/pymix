'''
author: juzicode
address: www.juzicode.com
公众号: 桔子code/juzicode
date: 2020.11.13
周期性采集图像，比较本次图片和上次图像差异，如果存在差异，发送到邮箱
不再发送附件，全部在正文显示图像

'''

import time,os,sys
from email.header import Header
from email.utils import parseaddr, formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from cv2 import *
import cv2
import getpass
import smtplib
import shutil
import numpy as np
from threading import Timer


#设置163邮箱smtp服务器
smtp_server = 'smtp.163.com'  
#图像差异门限，经验值设置
diff_threash=8.0
#图像文件名称
image_fn_now = 'capture_now.jpg'
image_fn_old = 'capture_old.jpg'
#定时器时长，每3600s也发送一次邮件
timeout= 3600 

def test_connet(smtp_server,from_addr,password):
    '''
    测试网络连接性    
    '''
    try:
        smtp = smtplib.SMTP(smtp_server, 25)#创建smtp服务实例
        smtp.login(from_addr, password)#登录
        smtp.quit()
        print('网络连接正常')   
    except:
        print('网络连接异常，退出')
        return False
        
    return True

def test_camera(cam_index,image_now):
    '''
    测试相机
    '''
    try:
        cap = cv2.VideoCapture(cam_index) #打开摄像头0
        ret, frame = cap.read()     #读取图像
        if ret is not True:
            cap.release()
            print('从相机获取图像错误')
            return False
        cv2.imwrite(image_now, frame) #写入文件
        print('相机测试正常')
    except:
        print('相机测试失败，退出')
        return False  
        
    return cap

def gen_mail(from_addr,to_addr,image_now,image_old):
    '''
    构造邮件
    '''
    message = MIMEMultipart()
    #设置邮件头
    message['Subject'] = Header('公众号[桔子code]：邮箱看家护院', 'utf-8').encode()
    name, addr = parseaddr('Jerry <%s>' % from_addr)
    message['From'] = formataddr((Header(name, 'utf-8').encode(), addr))
    name, addr = parseaddr('Tom <%s>' % to_addr)
    message['To'] = formataddr((Header(name, 'utf-8').encode(), addr))

    #生成邮件
    print('读取图像文件')
    image_data_now = None
    image_data_old = None    #上一次图像
    with open(image_now,'rb')  as pf:
        image_data_now = pf.read()
    with open(image_old,'rb')  as pf:
        image_data_old = pf.read()     
        
    print('生成邮件正文')
    img_now  = MIMEImage(image_data_now)
    img_now.add_header('Content-ID','capture_now') #对应<img> src属性
    message.attach(img_now)
    
    img_old  = MIMEImage(image_data_old)
    img_old.add_header('Content-ID','capture_old') #对应<img> src属性
    message.attach(img_old)    
    #生成邮件正文
    mail_cont="""<table >
                <tr><td> 关注微信公众号: [桔子code]，及时接收更好玩的Python</td></tr>
                <tr><td><img src="cid:capture_now"></td> </tr>
                <tr><td><img src="cid:capture_old"></td> </tr>
            </table>"""   # <img> src属性通过Content-ID引用                
    text = MIMEText(mail_cont,"html","utf-8")    
    message.attach(text)

    return message
        
def send_mail(smtp_server,from_addr,password,to_addr,message):
    '''
    发送邮件
    '''
    try:        
        #创建smtp服务实例
        smtp = smtplib.SMTP(smtp_server, 25)
        smtp.set_debuglevel(0)
        #登录
        smtp.login(from_addr, password)
        #发送邮件
        smtp.sendmail(from_addr, [to_addr], message.as_string())
        smtp.quit()
    except:
        print('发送邮件发生错误')
        return False
    return True
    
def thread_timeout():
    '''
    定时器任务，do nothing
    '''
    print('定时时间到')
    
if __name__== '__main__':
    print('\n-----欢迎来到www.juzicode.com')
    print('-----公众号: 桔子code/juzicode \n')   
    #设置邮箱地址、密码
    from_addr = input('输入发件人: ')
    password = getpass.getpass('输入邮箱密码: ')
    to_addr = from_addr  #自己给自己发送邮件
    
    #测试网络连接性
    if test_connet(smtp_server,from_addr,password) is not True:
        sys.exit(1)
        
    #测试相机
    cap = test_camera(0,image_fn_now) 
    if cap is False or cap is None:
        sys.exit(2)

    #启动一个定时线程
    thread_t1 = Timer(timeout,thread_timeout)
    thread_t1.start()
    
    #循环检测   
    while True:
        time.sleep(3)
        #保存上一次获取的图像
        try:
            shutil.copy(image_fn_now,image_fn_old)
        except:
            print('拷贝图像文件错误')
            continue
        frame_old = imread(image_fn_old)    
        
        #抓取本次图像
        try:
            ret, frame = cap.read()
            print('获取图像正常')
        except:
            print('获取图像失败')
            continue
        
        #比较图像差异，用mean计算平均值，小于阈值认为画面无变化，继续下一次检测
        difference = cv2.subtract(frame, frame_old)
        cv2.imshow('diff',difference)
        cv2.waitKey(1)
        ave = np.mean(difference)
        #cv2.imshow('old',frame_old)
        #cv2.imshow('now',frame)
        print('2幅图像差异值:',ave)
        if ave > diff_threash or thread_t1.is_alive() is not True:      
            if ave > diff_threash:
                print('画面发生变化，发送前后2幅图像')
                
            if thread_t1.is_alive() is not True:
                thread_t1 = Timer(timeout,thread_timeout)
                thread_t1.start()
                print('定时器时间到，发送前后2幅图像')
                        
            cv2.imwrite(image_fn_now, frame)#发生了变化，记录本次拍摄的图像           
            print('构造邮件')
            message = gen_mail(from_addr,to_addr,image_fn_now,image_fn_old)           
            print('连接并发送邮件')            
            send_mail(smtp_server,from_addr,password,to_addr,message)
            
