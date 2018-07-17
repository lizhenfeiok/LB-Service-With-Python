import socket,threading,struct
from LB_Handler import LB_Service, clock_clear
from LB_Config import server_port
from LB_Log import log

#线程方法
def threadings(client_socket, request_ip,local_ip):
    try:
        data = client_socket.recv(4096)
        identity_tuple = struct.unpack("i", data[:4]) #buf是从网络接收的字节流
        identity = int(identity_tuple[0])

        service = LB_Service()
        #客户端连接
        if identity == 868608:
            log.info('<**********************real_user:'+str(request_ip)+'********************>')
            service.hand_user_req(client_socket,request_ip,local_ip)
            log.info('<******************************************************************************>')
        #服务器发送数据：
        else:
            print('<-----------------server_client:'+str(request_ip)+'-------------------->')
            service.hand_client_req(data,request_ip)
    except Exception as e:
        log.info('【lb-warn】接收数据|判断身份|建立service时出错![%s]'%str(e))
    finally:
        client_socket.close()

#开启lb-server服务
def server_start():
    #获取服务器本机ip
    local_ip = socket.gethostbyname(socket.gethostname())
    log.info( "[lb-info][%s]LB server start..."%str((local_ip,7100)))

    #建立lbserver端服务
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',server_port))
    s.listen(128)

    while True:
        client_socket,addr = s.accept()
        try:
            t = threading.Thread(target=threadings, args=(client_socket,addr,local_ip))
            t.start()

        except Exception as e:
            log.info('【lb-warn】连接有误![%s][%s]'%(str(addr),str(e)))
            log.info('【lb-warn】重新建立LB服务...')
            server_start()


#1.开启计时器
threading.Thread(target=clock_clear).start()

#2.开启lb-server服务
server_start()
















