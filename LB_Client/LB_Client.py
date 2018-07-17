
import socket,time,json
from urllib import request
import LB_Config
from LB_Log import log

#访问tomcat获取连接数
def request_tomcat(local_ip):
    """获取tomcat 的连接数量"""
    dict_data = {}
    connect_num = ''
    try:
        tomcat_url = 'http://'+local_ip+':8080/snspro/getConnNumber'
        print("[lb-info]服务器client访问tomcat目标地址：%s"%str(tomcat_url))
        connect_num = request.urlopen(tomcat_url)
        connect_num=connect_num.read().decode()
        print('[lb-info]获取到的用户连接数：%s'%str(connect_num))
    except Exception as e:
        log.error('【lb-warn】访问tomcat出错![%s]'%str(e))
    dict_data['ip']=local_ip
    dict_data['connNum']=connect_num
    dict_data["identity"]="client"
    return dict_data

#建立socket连接
def buildSocket(request_ip):

    while True:
        time.sleep(10)
         #处理 ip 连接数量
        client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client_socket.connect((LB_Config.server_ip,LB_Config.server_port))

        print('<---------------------[%s]-------------------------->'%str(request_ip))
        print("[lb-info]服务器client发送的目标地址：ip[%s],port[%s]"%(str(LB_Config.server_ip),str(LB_Config.server_port)))
        dict_data_new = request_tomcat(request_ip)
        json_data = json.dumps(dict_data_new)
        print("[lb-info]服务器client发送数据：%s"%str(dict_data_new))
        client_socket.send(json_data.encode())
        client_socket.close()

#LB客户端发送
def client_send():
    #获取服务器本机ip
    local_ip = socket.gethostbyname(socket.gethostname())
    log.info( "[lb-info=%s]LB client start..."%str(local_ip))

    try:
         buildSocket(local_ip)
    except  Exception as e:
         log.error('【lb-warn】服务器client端连接出错![%s]'%str(e))
         log.error('【lb-warn】重新连接发送...')
         client_send()


#开始发送
client_send()






