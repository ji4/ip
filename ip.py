##!/usr/bin/python
## coding=UTF-8
import os
from os import listdir
from os.path import isfile, join
from myDict import *

path = "/root/Desktop/shared_folder/0604_XXXX_Android"

#如果像Web有多種儲值方式不要都命名Money開頭，不然都會像Gaming一樣算同一個，也不要有斜線和空白
fileNames = ['FbLogin', 'GoogleLogin', 'GuestLogin',
             'FbPersonal', 'GooglePersonal', 'GuestPersonal',
             'Gaming',
             'Money']

filter = "'ip.src >= 192.168.137.2 && ip.src <= 192.168.137.255 && not ((ip.dst >= 192.168.0.0 && ip.dst <= 192.168.255.255) || (ip.dst >= 224.0.0.0 && ip.dst <= 239.255.255.255) || (ip.dst >= 10.0.0.0 && ip.dst <= 10.255.255.255) || ip.dst == 255.255.255.255) && not icmp.type == 3'"

fileNameIndex = 0
dstIpIndex = 1
outputDir = 'output'
categoryDir = 'ipFiles'
outputDirPath = path + '/' + outputDir

def pcapToTxt():
    pcapFiles = [f for f in listdir(path) if isfile(join(path, f))]
    os.system('mkdir ' + outputDirPath)
    os.system('mkdir ' + outputDirPath + '/' + categoryDir)
    for file in pcapFiles:
        os.system('tshark -r ' + path + '/' + file 
                  + ' -Y ' + filter 
                  + ' -T fields -e ip.src -e ip.dst'
                  + ' | sort -u'
                  + ' > ' + outputDirPath +'/' + categoryDir + '/' + file + '.txt')
        print "outputting file: " + file + ".txt"

def listAllIps():
    categoryPath = outputDirPath + '/' + categoryDir
    ipFiles = [f for f in listdir(categoryPath) if isfile(join(categoryPath, f))]
    for file in ipFiles:
        with open(categoryPath + '/' + file, "r") as categoryFile:
            categoryIps = categoryFile.read()
            print 'file: ' + file + '\n' + categoryIps
        for lineIp in categoryIps.split('\n'):
            with open(outputDirPath + '/category_ip_unsorted', "a") as fCategory_ip:
                if(len(lineIp) > 0):
                    fCategory_ip.write(file.split('.')[fileNameIndex] + '\t' + lineIp.split('\t')[dstIpIndex] + '\n')
def sortByCategory():
    with open(outputDirPath + '/category_ip_unsorted', 'r') as fOldCategory_ip, open(outputDirPath + '/category_ip_sorted', 'a+') as fNewCategory_ip:
        categoryIps = fOldCategory_ip.read()
        categoryIpSet = set()
        for fileName in fileNames:
            for line in categoryIps.strip().split('\n'):
                ip = line.split('\t')[dstIpIndex]
                appendLine = fileName + '\t' + ip
                if line.startswith(fileName) and appendLine not in categoryIpSet:
                    isp, country = searchISP_Country(ip)
                    if not isp.startswith('MICROSOFT-CORP'):
                        if country != '#N/A':
                            fNewCategory_ip.write(appendLine + '\t' + isp + '\t' + allcn[country] +'('+ country + ')\n')
                        categoryIpSet.add(appendLine)
                    else: print 'Filtered an IP from MS. IP: '+ip
    os.system('rm ' + outputDirPath + '/category_ip_unsorted')

def searchISP_Country(ip):
    cmd = "whois -h whois.cymru.com \" -v %s\"" % ip
    res = os.popen(cmd).read()
    if(len(res) > 0):
        res = res.split("\n")[1]
        data = res.split('|')
        cn = data[3].strip()
        isp = data[6].strip()

        if cn in allcn.keys(): #filter NA
            if "," in isp:
                isp = isp.split(',')[0]
            else: isp = ''
            print "%s\t%s\t%s(%s)" % (ip, isp, allcn[cn], cn)
            return (isp, cn)
    
    saveToLog(ip)
    return ('#N/A','#N/A') 

def saveToLog(ip):
    print "Found unknown cn or ip: " + ip + ", log saved to unknown_ip.txt"
    with open(outputDirPath + '/unknown_ip', 'a+') as fLog:
        fLog.write(ip + "\n")

if __name__ == "__main__":
    pcapToTxt()
    listAllIps()
    sortByCategory()
