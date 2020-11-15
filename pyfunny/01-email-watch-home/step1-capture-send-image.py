'''
author: juzicode
address: www.juzicode.com
公众号: 桔子code/juzicode
date: 2020.11.13
周期性采集图片，发送到邮箱
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


print('\n-----欢迎来到www.juzicode.com')
print('-----公众号: 桔子code/juzicode \n')   
#设置邮箱地址、密码
from_addr = input('输入发件人: ')
password = getpass.getpass('输入邮箱密码: ')
to_addr = from_addr  #自己给自己发送邮件
#设置163邮箱smtp服务器
smtp_server = 'smtp.163.com'  

#测试相机
try:
    cap = cv2.VideoCapture(0) #打开摄像头0
    ret, frame = cap.read()     #读取图像
    if ret is not True:
        cap.release()
        sys.exit(1)
    cv2.imwrite('capture.jpg', frame) #写入文件
    cap.release()
    print('生成图片ok')
except:
    print('相机测试失败')
    sys.exit(2)    

#测试网络连接性    
try:
    smtp = smtplib.SMTP(smtp_server, 25)#创建smtp服务实例
    smtp.login(from_addr, password)#登录
    smtp.quit()
except:
    print('登录邮箱失败')
    sys.exit(3)

#循环发送邮件    
while True:
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cv2.imwrite('capture.jpg', frame)
        cap.release()
        print('获取图像正常')
    except:
        print('获取图像失败')
        break
    try:
        print('构造邮件')
        message = MIMEMultipart()
        #设置邮件头
        message['Subject'] = Header('公众号[桔子code]：邮箱看家护院', 'utf-8').encode()
        name, addr = parseaddr('Jerry <%s>' % from_addr)
        message['From'] = formataddr((Header(name, 'utf-8').encode(), addr))
        name, addr = parseaddr('Tom <%s>' % to_addr)
        message['To'] = formataddr((Header(name, 'utf-8').encode(), addr))

        #读取图片
        image_data = None
        with open('capture.jpg','rb')  as pf:
            image_data = pf.read()
        #生成图片附件：
        imgpart = MIMEApplication(image_data)
        imgpart.add_header('Content-Disposition','attachment',filename='capture.jpg')
        message.attach(imgpart)
        #生成图片正文
        img  = MIMEImage(image_data)
        img.add_header('Content-ID','capture-1') #对应<img> src属性
        message.attach(img)
        
        #生成邮件正文
        mail_cont="""<table >
                    <tr><td> 关注微信公众号: [桔子code]，及时接收更好玩的Python</td></tr>
                    <tr><td><img src="cid:capture-1"></td> </tr>
                </table>"""   # <img> src属性通过Content-ID引用                
        text = MIMEText(mail_cont,"html","utf-8")    
        message.attach(text)
        
        print('连接并发送邮件')
        #创建smtp服务实例
        smtp = smtplib.SMTP(smtp_server, 25)
        smtp.set_debuglevel(0)
        #登录
        smtp.login(from_addr, password)
        #发送邮件
        smtp.sendmail(from_addr, [to_addr], message.as_string())
        smtp.quit()
    except:
        print('发生错误，再来')
     
    print('等待10分钟')
    for x in range(600):
        time.sleep(1)
        print(x,end=' ' )
        if x%60 == 0:
            print()