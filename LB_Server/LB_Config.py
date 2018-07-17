import random,configparser

from LB_Log import log

"""通过 配置文件路径 r 文件 将随机的真实ip返回"""
conf_path = '/etc/sns/sns-oracle.conf'
# conf_path = 'config.ini'
server_ip = ''
server_port = 0000
real_ip_list = []

#获取随机服务器ip
def get_random_ip():
    return random.choice(real_ip_list)


try:
    #配置文件
    cf = configparser.ConfigParser()
    cf.read(conf_path)  # 文件路径
    b=random.randint(1,5)
    real_ips_str = cf.get("lbserver",'serverip')  # 获取指定section 的option值
    real_ip_list = real_ips_str.split(',')

    server_ip = cf.get("lbserver",'lbip')
    server_port = int(cf.get("lbserver",'lbport'))
except Exception as e:
    log.info('【lb-warn】读取配置文件时出错！[%s]'%str(e))







