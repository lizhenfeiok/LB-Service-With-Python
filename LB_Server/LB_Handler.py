# 服务器IP列表
import json,time,struct
import LB_Config
from LB_Log import log

cache_list = []
# 真实服务器IP
resultIP = None

class LB_Service():
    """client user 处理逻辑"""
    def update_data(self, dict_data,request_ip):
        # 1.获取 新的连接数 以便于更新 缓存列表中的 连接数量
        self.updata_num(dict_data,request_ip)
        # 2.取出最小连接数IP
        self.get_real_ip(request_ip)

    def updata_num(self, dict_data,request_ip):
        try:
            flag = True
            print('[lb-info]服务器client更新前的列表长度%s，数据：%s'%(str(len(cache_list)),str(cache_list)))
            if len(cache_list) == 0:
                log.info('!!!client:服务器连接数连接数列表更新!!!')
                log.info('[lb-info]服务器%s已被添加到列表!'%str(request_ip))
                dict_data['updateTime'] = str(int(time.time()))
                cache_list.append(dict_data)
            else:
                for i in cache_list:
                    if dict_data['ip'] == i['ip']:
                        if dict_data['connNum']=='' or dict_data['connNum'] is None:
                            log.info('!!!client:服务器连接数连接数列表更新!!!')
                            log.info('【lb-warn】服务器%s已被从列表删除!'%str(request_ip))
                            cache_list.remove(i)
                        else:
                            i['connNum'] = dict_data['connNum']
                            i['updateTime'] = str(int(time.time()))
                        flag = False
                if flag:
                    if dict_data['connNum'] is not None and dict_data['connNum']!='':
                        log.info('!!!client:服务器连接数连接数列表更新!!!')
                        log.info('[lb-info]服务器%s已被添加到列表!'%str(request_ip))
                        dict_data['updateTime'] = str(int(time.time()))
                        cache_list.append(dict_data)

            print('[lb-info]服务器client更新后的列表长度%s，数据：%s'%(str(len(cache_list)),str(cache_list)))
        except Exception as e:
            log.error('【lb-warn】服务器client更新缓存列表出错！[%s]'%str(e))

    #比较连接数，更新/获取真实ip
    def get_real_ip(self,request_ip):
        try:
            if len(cache_list)>0:
                # 2.取出最小连接数IP
                tmp = cache_list[0]['connNum']
                resultIP = cache_list[0]['ip']
                for i in cache_list:
                    a = i['connNum']
                    if int(a) < int(tmp):
                        resultIP = i['ip']
            else:
                resultIP = None
            return resultIP
        except Exception as e:
            log.error('【lb-warn】更新或获取最小连接数时出错！[%s]'%str(e))

    #user从缓存列表中获取realIP
    def user_getIp(self,request_ip):
        try:
            ip = None
            # 1.先取resultIP值
            if resultIP is not None:
                ip = resultIP
            # 2.若resultIP为None，则cache_list比较连接数取值
            elif len(cache_list) > 0:
                ip = self.get_real_ip(request_ip)
            return ip
        except Exception as e:
            log.error('【lb-warn】user从缓存数据列表中获取ip时出错！[%s]'%str(e))

    #处理user请求
    def hand_user_req(self,client_socket,request_ip,local_ip):
        realIp = ''
        try:
            log.info('[lb-info]当前连接数信息：%s'%str(cache_list))
             # 1.获取缓存列表ip
            realIp = self.user_getIp(request_ip)
            log.info("[lb-info]正常获取的返回值IP：%s" %str(realIp))

             # 2.返回服务器本机ip
            if realIp is None or realIp=='':
                log.error("【lb-warn】缓存数据列表空值！返回本机IP：%s" %str(local_ip))
                realIp = local_ip
             #3.读取配置文件ip
            if realIp is None or realIp=='':
                realIp = LB_Config.get_random_ip()
                log.error("【lb-warn】本机IP空值！返回配置文件随机IP：%s" %str(realIp))
        except Exception as e:
            # 兜底方案：读取配置文件ip，随机抽取返回
            realIp = LB_Config.get_random_ip()
            log.error("【lb-warn】异常配置文件获取的返回值IP：%s,[%s]" %(str(realIp),str(e)))
        finally:
            server_ip = bytes(realIp,encoding='utf-8')
            values = (868608,28,12,server_ip,8080)
            log.info("[lb-info]发送到客户端的数据：%s" %str(values))

            #包装为客户端C++可识别的二进制数据
            result = struct.pack("=i2h16si",*values)
            client_socket.send(result)

    #处理服务器发送请求
    def hand_client_req(self,data,request_ip):
        try:
            recv_data_str = data.decode('utf-8')
            print("[lb-info]接受的数据：%s" %str(recv_data_str))
            dict_data = json.loads(recv_data_str)
            self.update_data(dict_data,request_ip)
        except Exception as e:
            log.error("【lb-warn】server_client更新出错：[%s]" %str(e))

#定时删除无效连接
def clock_clear():
    while True:
        try:
            time.sleep(20)
            if len(cache_list)>0:
                print('<============================clock start==============================>')
                print('[lb-info]清理前的缓存列表长度%s,数据：%s'%(str(len(cache_list)),str(cache_list)))
                for item in cache_list:
                    #间隔超过20s视为无效连接
                    if (int(time.time())-int(item['updateTime'])) > 20:
                        log.info('!!!clock:服务器连接数连接数列表更新!!!')
                        log.error('【lb-warn】服务器%s已被从列表删除!'%str(item['ip']))
                        cache_list.remove(item)
                print('[lb-info]清理后的缓存列表长度%s,数据：%s'%(str(len(cache_list)),str(cache_list)))
        except Exception as e:
            log.error('【lb-warn】计时器清理无效连接时出错！[%s]'%str(e))
            log.error('【lb-warn】重新开启计时器...')
            clock_clear()






