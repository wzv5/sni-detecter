# coding=utf-8

# by garson blog garnote.top
import sys
import getopt
import threadpool
import time
import threading
from detect import *

rin = 'task.txt'
output = 'replace'
timeout = 2
parallels = 20
hostname = 'github.com'
mod = True
ips = []
passip = []

times = 0
n = 0
lock = threading.Lock()


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:o:t:p:n:h', [
                                   'in', 'out', 'timeout', 'parallels', 'hostname'])
    except getopt.GetoptError as err:
        usage()
        print(err)
        sys.exit('parameter error')
    global rin, output, timeout, parallels, ips, mod, hostname
    for o, a in opts:
        if o in ('-i', '--in'):
            rin = a
        elif o in ('-o', '--out'):
            output = a
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o in ('-t', '--timeout'):
            timeout = int(a)
        elif o in ('-n', '--hostname'):
            hostname = a
        elif o in ('-p', '--parallels'):
            parallels = int(a)
    file_obj = open(rin)
    try:
        txt = file_obj.read()
        ips = gen_ip(txt)
        print('读入了' + str(len(ips)) + '个ip')
    finally:
        file_obj.close()


if __name__ == '__main__':
    main()


def worker(ip, t, m, h):
    global times, n, passip
    ret = detect(ip, t, h)
    with lock:
        if ret:
            passip.append(ip)
            printx('√   '+ip, 1)
        times += 1
        printx()


def printx(text='', type=0):
    global times, n
    p = int((float(times)/n)*30)
    t1 = '##############################'  # 30
    t2 = '                              '  # 30
    if type == 1:
        sys.stdout.write(
            '                                                      \r')
        sys.stdout.flush()
        print(text)
    else:
        sys.stdout.write('[' + t1[0:p] + t2[0:30-p] + ']' + '\r')
        sys.stdout.flush()


def print_result():
    global times, passip, output
    print ('√   finish  ' + '本次扫描了 ' + str(times) +
           ' 个ip,'+'SNI_IP有 ' + str(len(passip)) + ' 个。')
    if len(passip) > 0:
        if output == 'replace':
            output = time.strftime(
                'PassIp_%Y%m%d_%H%M%S.txt', time.localtime(time.time()))
        f = open(output, 'w')
        try:
            for v in passip:
                f.writelines(v+'\n')
        finally:
            f.close()
            print('bye,文件已写出到'+output)
    print("按Enter退出")
    raw_input()


pool = threadpool.ThreadPool(parallels)
requests = []
n = len(ips)
for a in ips:
    c = [a, timeout, mod, hostname]
    var = [(c, None)]
    requests += threadpool.makeRequests(worker, var)
[pool.putRequest(req) for req in requests]
print('Working')
printx()
pool.wait()
print_result()
