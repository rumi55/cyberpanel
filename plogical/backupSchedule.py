import thread
import pexpect
import CyberCPLogFileWriter as logging
import subprocess
import shlex
from shutil import rmtree
import os
import requests
import json
import time
from backupUtilities import backupUtilities

class backupSchedule:


    @staticmethod
    def createBackup(virtualHost, ipAddress,writeToFile):
        try:

            writeToFile.writelines("["+time.strftime("%I-%M-%S-%a-%b-%Y")+"]"+" Preparing to create backup for: "+virtualHost+"\n")
            writeToFile.writelines("[" + time.strftime(
                "%I-%M-%S-%a-%b-%Y") + "]" + " Backup started for: " + virtualHost + "\n")

            finalData = json.dumps({'websiteToBeBacked': virtualHost})
            r = requests.post("http://localhost:5003/backup/submitBackupCreation", data=finalData)
            data = json.loads(r.text)
            backupPath = data['tempStorage']


            while (1):
                r = requests.post("http://localhost:5003/backup/backupStatus", data= finalData)
                time.sleep(2)
                data = json.loads(r.text)

                if data['status'] == 0:
                    break

            writeToFile.writelines("[" + time.strftime(
                "%I-%M-%S-%a-%b-%Y") + "]" + " Backup created for:" + virtualHost + "\n")

            writeToFile.writelines("[" + time.strftime(
                "%I-%M-%S-%a-%b-%Y") + "]" + " Preparing to send backup for: " + virtualHost +" to "+ipAddress+ "\n")
            writeToFile.flush()

            backupSchedule.sendBackup(backupPath+".tar.gz", ipAddress,writeToFile)

            writeToFile.writelines("[" + time.strftime(
                "%I-%M-%S-%a-%b-%Y") + "]" + "  Backup for: " + virtualHost + " is sent to " + ipAddress + "\n")

            writeToFile.writelines("\n")
            writeToFile.writelines("\n")

            writeToFile.writelines("#####################################")

            writeToFile.writelines("\n")
            writeToFile.writelines("\n")

        except BaseException,msg:
            logging.CyberCPLogFileWriter.writeToFile(str(msg) + " [startBackup]")



    @staticmethod
    def sendBackup(backupPath,IPAddress,writeToFile):
        try:
            command ='rsync -avz -e "ssh  -i /root/.ssh/cyberpanel" '+ backupPath+ ' root@'+IPAddress+':/home/backup/'+time.strftime("%a-%b")+"/"

            subprocess.call(shlex.split(command),stdout=writeToFile)

        except BaseException,msg:
            logging.CyberCPLogFileWriter.writeToFile(str(msg) + " [startBackup]")

    @staticmethod
    def prepare():
        try:
            path = "/usr/local/CyberCP/backup/"
            destinations = path + "destinations"

            backupLogPath = "/usr/local/lscp/logs/backup_log."+time.strftime("%I-%M-%S-%a-%b-%Y")



            writeToFile = open(backupLogPath,"a")

            writeToFile.writelines("#################################################\n")
            writeToFile.writelines("      Backup log for: " +time.strftime("%I-%M-%S-%a-%b-%Y")+"\n")
            writeToFile.writelines("#################################################\n")

            writeToFile.writelines("\n")
            writeToFile.writelines("\n")

            ipAddress = open(destinations,'r').readlines()[0].strip("\n")



            if backupUtilities.checkIfHostIsUp(ipAddress) == 1:
                if backupUtilities.checkConnection(ipAddress) != 1:
                    writeToFile.writelines("[" + time.strftime(
                        "%I-%M-%S-%a-%b-%Y") + "]" + " Connection to:" + ipAddress+" Failed, please resetup this destination from CyberPanel, aborting." + "\n")
                    return 0
                else:
                    pass
            else:
                writeToFile.writelines("[" + time.strftime(
                    "%I-%M-%S-%a-%b-%Y") + "]" + " Host:" + ipAddress + " is down, aborting." + "\n")
                return 0

            for virtualHost in os.listdir("/home"):
                backupSchedule.createBackup(virtualHost,ipAddress,writeToFile)

        except BaseException,msg:
            logging.CyberCPLogFileWriter.writeToFile(str(msg) + " [startBackup]")


backupSchedule.prepare()