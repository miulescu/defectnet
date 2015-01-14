#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      mihai
#
# Created:     14/11/2014
# Copyright:   (c) mihai 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import sys,errno
import serial, smtplib, time, struct
import threading
import datetime
import socket
from  bitstring import BitArray, BitStream, Bits
from collections import deque
from threading  import Thread
from threading import Timer
import urllib,urllib2
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import zipfile
import shutil as sh
from array import *


class Window():
    """
        cuprinde informatiile pentru fiecare variabila
    """
    pass


class AnEmailToSend():
    """
        clasa ce contine informatii despre sender, receiver si mesaj
        mesajul este doar defectul acum ex: stare_forta
        se creeaza doar atunci cand nu s-a reusit sa se transmita cand s-a descoperit defectul
        si se introduce in deque-ul emailAcc
    """
    def __init__(self,sender,receiver,message):
        self.sender = sender
        self.receiver = receiver
        self.message = message

    def sendMe(self, an_emailAcc):
        """
          incearca sa se  transmita ca email
        """
        try:
            server = connectEmail()
            server.sendmail(self.sender,self.receiver,self.message)
            server.quit()
        except Exception:
            an_emailAcc.append(self)

    def sendMeServerConnected(self,server, an_emailAcc):
	try:
	    server.sendmail(self.sender,self.receiver,self.message)
        except:
	    an_emailAcc.append(self)


class RepeatEvery(threading.Thread):
    """
        timer implementation in python
    """
    def __init__(self, interval, func, *args, **kwargs):
        threading.Thread.__init__(self)
        self.interval = interval  # seconds between calls
        self.func = func          # function to call
        self.args = args          # optional positional argument(s) for call
        self.kwargs = kwargs      # optional keyword argument(s) for call
        self.runable = True
    def run(self):
        while self.runable:
            self.func(*self.args, **self.kwargs)
            time.sleep(self.interval)
    def stop(self):
        self.runable = False


def massMail(an_emailAcc):
    """
        trimite mailuri cu toate elementele din deque
        se pune intr-un timer ce se repata la N minute
    """
    try:
        #print "inside massMail!!!!!!!!!!!!!!!!!!!"
        server =  connectEmail()
	okServer = True
    except  Exception:
        return
    while(len(an_emailAcc)>0):

        mail = an_emailAcc.pop()
	if okServer:
	    mail.sendMeServerConnected(server,anEmailAcc)
	else:
            mail.sendMe(an_emailAcc)


def sendEmail(mssg):

      """
        cand gaseste eroarea trimite email

      """
      try:
	from_addr = "lema.errors@gmail.com"
	#to_addr_list = ["mihai.miulescu@softronic.ro","marius.pancu@softronic.ro","adi.iordache@softronic.ro"]
	to_addr_list = ["mihai.miulescu@softronic.ro"]
	cc_addr_list = ["mmiulescu@yahoo.com"]
	subject = "defect lema 16 -- " + mssg + " timp real"
	
	message = mssg
	header = 'From: %s\n' % from_addr
	header += 'To: %s\n' % ','.join(to_addr_list)
	header += 'Cc:  %s\n' % ','.join(cc_addr_list)
	header += 'Subject: %s\n\n' % subject
	message = header + message
	
        # am presupus ca erorile nu apar asa de des si aceasta portiune nu se executa de foarte multe ori ea este oricum consumatoare de timp
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("lema.errors", "softronic!@#")
        #server.sendmail("lema.errors@gmail.com",["mihai.miulescu@softronic.ro", "marius.pancu@softronic.ro","adi.iordache@softronic.ro"], message )
	server.sendmail("lema.errors@gmail.com",["mihai.miulescu@softronic.ro"],message)
      except Exception:
        #print " nu se poate loga la server!!!"
        #print Exception

        mail = AnEmailToSend("lema.errors@gmail.com",["mihai.miulescu@softronic.ro", "marius.pancu@softronic.ro","adi.iordache@softronic.ro"], message)
        # baga  in coada de mesaje ce vor fi trasmise ulterior
        emailAcc.append(mail)

def in_array(val,arr):
    for i in arr:
        if i == val:
            return True
        else:
            return False

def isInt(number):
    if number % 1 == 0:
        return True

def deleteFileFromList(list,file):

    """
        dupa 2 minute va sterge file din list
    """
##    homeDir = os.environ['HOME']
####
##    archiDir = homeDir + '/arhive/'
##    errorsDir = homeDir + '/defecte'



##    currDirectory = os.path.dirname(os.path.abspath(__file__))
##    archiDir = currDirectory + '/arhive/'


    time.sleep(40)# doarme n secunde .. in timpul asta se scrie in  fisierul file de eroare

    file.flush()
    os.fsync(file.fileno())

    file.close()

    #print 'ok  din deletefileFromList'
    list.remove(file)
    createDefectArchiveZip(file)
    #os.remove(file)




def createArchiveZip(nameOfTheArchive):
    """
        arhiveaza un fisier
    """
##    homeDir = os.environ['HOME']
##
##    archiDir = homeDir + '/arhive/'
##    errorsDir = homeDir + '/defecte'
    #currDirectory = os.path.dirname(os.path.abspath(__file__))
##    #archiDir = currDirectory + '\\arhive\\' #windows
    #print currDirectory

##    archiDir = currDirectory + '/arhive/'
##    print archiDir
    try:
        z= zipfile.ZipFile(nameOfTheArchive + ".zip", "w",zipfile.ZIP_DEFLATED)
        z.write(nameOfTheArchive + ".dat")
        z.close()
    except Exception:
        print 'eroare crearea arhivei!'

##    src = str(currDirectory) +'\\' + nameOfTheArchive + ".zip" #windows
##
##    #src = str(currDirectory) +'/' + nameOfTheArchive + ".zip"
##
##
##
##    sh.copy(src,archiDir)
##
    pathofFile = os.getcwd() + "/" + nameOfTheArchive +".dat"
    pathtoArchive = os.getcwd() + "/" + nameOfTheArchive +".zip"



    pathOfArchive = os.getcwd() + "/arhive/"
    if os.path.isfile(pathOfArchive + nameOfTheArchive +".zip"):
        sh.copy(pathtoArchive, pathOfArchive + nameOfTheArchive + str(time.time()) + ".zip")
    else:
        sh.copy(pathtoArchive,pathOfArchive)

    os.remove(pathofFile)
    os.remove(pathtoArchive)
    #os.remove(nameOfTheArchive +  ".dat")
##    os.remove(nameOfTheArchive +  ".zip")

##    addressOfTheCurrentFile  = nameOfTheArchive + ".zip"
##    addressOfTheNewfile =  archiDir  + addressOfTheCurrentFile


    #os.system("cp " + pathofFile + pathOfArchive)

def createDefectArchiveZip(nameOfTheArchive):
    """
        arhiveaza un fisier
    """
    #print nameOfTheArchive


    z= zipfile.ZipFile(nameOfTheArchive.name[:-4] + ".zip", "w",zipfile.ZIP_DEFLATED)
    z.write(nameOfTheArchive.name)
    z.close()

    pathofFile = os.getcwd() + "/" + nameOfTheArchive.name
    pathtoArchive = os.getcwd() + "/" + nameOfTheArchive.name[:-4] +".zip"

    pathOfArchive = os.getcwd() + "/defecte/"
    #if os.path.isfile(pathOfArchive + nameOfTheArchive +".zip"):
     #   sh.copy(pathtoArchive, pathOfArchive + nameOfTheArchive.name[:-4] +str(time.time()) + ".zip")
    #else:
    sh.copy(pathtoArchive,pathOfArchive)

    os.remove(pathofFile)
    os.remove(pathtoArchive)



##    currDirectory = os.path.dirname(os.path.abspath(__file__))
##    #archiDir = currDirectory + '\\defecte\\' #windows
##    archiDir = currDirectory + '/defecte/'
##
##    #src = str(currDirectory) +'\\' + nameOfTheArchive.name + ".zip" #windows
##    src = str(currDirectory) +'/' + nameOfTheArchive.name + ".zip"
##    sh.copy(src,archiDir)
##
##
##    os.remove(nameOfTheArchive.name)
##    os.remove(nameOfTheArchive.name +  ".zip")




def connectEmail():
    """
        intoarce o conexiune la gmail
    """
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("lema.errors", "softronic!@#")
        return server
    except Exception:
        return

def printSomeText(text):
    print "some text from timer!" + text

def emtptDefectsTableTime(current_time):
    pass
    #pentru fiecaare valoare toate listele sterge acele elemnte mai mari cu 2 minute decat timpul curent

def appendWithMessage(d, p ):
    global emailAcc, end_time

    now = time.strftime("%X")
    a = now + "Star"
    d.append(p)
    lock.acquire()
    listD = list(d)

    if len(listD) == 2:
       # print   '{0} and {1}'.format(listD[1].D0KIzolareMT2, listD[0].D0KIzolareMT2)

        if listD[1].stare_forta =='f0' and  listD[0].stare_forta!='f0':

	    name_of_file  ="stare_forta_" + str(time.time()) +".dat"
            f = open(name_of_file, "wb+")

            #scriu din coada -3  in fisierul de defect deschis
            minus3Chunk = Bits().join(buffer_defects)
            Bits(minus3Chunk).tofile(f)

            list_of_defects_files_opened_for_writing.append(f)


            #start thread count 2 mins and delete the file above
            makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
            makeFile.start()

            message = "stare_forta"
            sendmail = threading.Thread(target=sendEmail, args=(message,))
            sendmail.start()

        if listD[1].D7KIzolareMT1 == '1' and listD[0].D7KIzolareMT1 == '0':

            name_of_file  ="D7KIzolareMT1_" + str(time.time()) +".dat"
            f = open(name_of_file, "wb+")

            #scriu din coada -3  in fisierul de defect deschis
            minus3Chunk = Bits().join(buffer_defects)
            Bits(minus3Chunk).tofile(f)

            list_of_defects_files_opened_for_writing.append(f)

            #start thread count 2 mins and delete the file above
            makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
            makeFile.start()

            message = "D7KIzolareMT1 -- s-a generat fisierul " + name_of_file
            sendmail = threading.Thread(target=sendEmail, args=(message,))
            sendmail.start()

        if listD[1].D0KIzolareMT2 == '1' and listD[0].D0KIzolareMT2 == '0':

            name_of_file  ="D0KIzolareMT2_" + str(time.time()) +".dat"
            f = open(name_of_file, "wb+")

            #scriu din coada -3  in fisierul de defect deschis
            minus3Chunk = Bits().join(buffer_defects)
            Bits(minus3Chunk).tofile(f)

            list_of_defects_files_opened_for_writing.append(f)

            #start thread count 2 mins and delete the file above
            makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
            makeFile.start()

            message = "D7KIzolareMT2"
            sendmail = threading.Thread(target=sendEmail, args=(message,))
            sendmail.start()

        if listD[1].D1KIzolareMT3 == '1' and listD[0].D1KIzolareMT3 == '0':
            name_of_file  ="D1KIzolareMT3_" + str(time.time()) +".dat"
            f = open(name_of_file, "wb+")

            #scriu din coada -3  in fisierul de defect deschis
            minus3Chunk = Bits().join(buffer_defects)
            Bits(minus3Chunk).tofile(f)

            list_of_defects_files_opened_for_writing.append(f)

            #start thread count 2 mins and delete the file above
            makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
            makeFile.start()

            message = "D1KIzolareMT3"
            sendmail = threading.Thread(target=sendEmail, args=(message,))
            sendmail.start()
        if listD[1].D7KIzolareMT4 == '1' and listD[0].D7KIzolareMT4 == '0':

            name_of_file  ="D7KIzolareMT4_" + str(time.time()) +".dat"
            f = open(name_of_file, "wb+")

            #scriu din coada -3  in fisierul de defect deschis
            minus3Chunk = Bits().join(buffer_defects)
            Bits(minus3Chunk).tofile(f)

            list_of_defects_files_opened_for_writing.append(f)

            #start thread count 2 mins and delete the file above
            makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
            makeFile.start()

            message = "D7KIzolareMT4"
            sendmail = threading.Thread(target=sendEmail, args=(message,))
            sendmail.start()

        if listD[1].D0KIzolareMT5 == '1' and listD[0].D0KIzolareMT5 == '0':
            name_of_file  ="D0KIzolareMT5_" + str(time.time()) +".dat"
            f = open(name_of_file, "wb+")

            #scriu din coada -3  in fisierul de defect deschis
            minus3Chunk = Bits().join(buffer_defects)
            Bits(minus3Chunk).tofile(f)

            list_of_defects_files_opened_for_writing.append(f)

            #start thread count 2 mins and delete the file above
            makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
            makeFile.start()

            message = "D0KIzolareMT5"
            sendmail = threading.Thread(target=sendEmail, args=(message,))
            sendmail.start()

        if listD[1].D1KIzolareMT6 == '1' and listD[0].D1KIzolareMT6 == '0':

            name_of_file  ="D1KIzolareMT6_" + str(time.time()) +".dat"
            f = open(name_of_file, "wb+")

            #scriu din coada -3  in fisierul de defect deschis
            minus3Chunk = Bits().join(buffer_defects)
            Bits(minus3Chunk).tofile(f)

            list_of_defects_files_opened_for_writing.append(f)

            #start thread count 2 mins and delete the file above
            makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
            makeFile.start()

            message = "D1KIzolareMT6"
            sendmail = threading.Thread(target=sendEmail, args=(message,))
            sendmail.start()

        if listD[1].RegimASC == '1' and listD[0].RegimASC == '0':

            name_of_file  ="RegimASC_" + str(time.time()) +".dat"
            f = open(name_of_file, "wb+")

            #scriu din coada -3  in fisierul de defect deschis
            minus3Chunk = Bits().join(buffer_defects)
            Bits(minus3Chunk).tofile(f)

            list_of_defects_files_opened_for_writing.append(f)

            #start thread count 2 mins and delete the file above
            makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
            makeFile.start()

            message = "RegimASC"
            sendmail = threading.Thread(target=sendEmail, args=(message,))
            sendmail.start()

        if listD[1].DebitRedusUleiTrafo == '1' and listD[0].DebitRedusUleiTrafo == '0':

            name_of_file  ="DebitRedusUleiTrafo_" + str(time.time()) +".dat"
            f = open(name_of_file, "wb+")

            #scriu din coada -3  in fisierul de defect deschis
            minus3Chunk = Bits().join(buffer_defects)
            Bits(minus3Chunk).tofile(f)

            list_of_defects_files_opened_for_writing.append(f)

            #start thread count 2 mins and delete the file above
            makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
            makeFile.start()

            message = "DebitRedusUleiTrafo"
            sendmail = threading.Thread(target=sendEmail, args=(message,))
            sendmail.start()

        if listD[1].AtentionareNivelRedusTrafo == '1' and listD[0].AtentionareNivelRedusTrafo== '0':

            name_of_file  ="AtentionareRedusUleiTrafo_" + str(time.time()) +".dat"
            f = open(name_of_file, "wb+")

            #scriu din coada -3  in fisierul de defect deschis
            minus3Chunk = Bits().join(buffer_defects)
            Bits(minus3Chunk).tofile(f)

            list_of_defects_files_opened_for_writing.append(f)

            #start thread count 2 mins and delete the file above
            makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
            makeFile.start()

            message = "AtentionareRedusUleiTrafo"
            sendmail = threading.Thread(target=sendEmail, args=(message,))
            sendmail.start()

        if listD[1].Stare_ceta_S1 == 'f0' and listD[0].Stare_ceta_S1 != 'f0':
            name_of_file  ="Stare_ceta_S1_" + str(time.time()) +".dat"
            f = open(name_of_file, "wb+")

            #scriu din coada -3  in fisierul de defect deschis
            minus3Chunk = Bits().join(buffer_defects)
            Bits(minus3Chunk).tofile(f)

            list_of_defects_files_opened_for_writing.append(f)

            #start thread count 2 mins and delete the file above
            makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
            makeFile.start()

            message = "Stare_ceta_S1"
            sendmail = threading.Thread(target=sendEmail, args=(message,))
            sendmail.start()

        if listD[1].Stare_ceta_S1 == 'e0' and listD[0].Stare_ceta_S1 != 'e0':
            if listD[1].S1_Cauza_Bloc_Soft !='01':
                name_of_file  ="Stare_ceta_S1_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Stare_ceta_S1"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()

        if listD[1].Stare_ceta_S2 == 'f0' and listD[0].Stare_ceta_S2 != 'f0':
            name_of_file  ="Stare_ceta_S2_" + str(time.time()) +".dat"
            f = open(name_of_file, "wb+")

            #scriu din coada -3  in fisierul de defect deschis
            minus3Chunk = Bits().join(buffer_defects)
            Bits(minus3Chunk).tofile(f)

            list_of_defects_files_opened_for_writing.append(f)

            #start thread count 2 mins and delete the file above
            makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
            makeFile.start()

            message = "Stare_ceta_S2"
            sendmail = threading.Thread(target=sendEmail, args=(message,))
            sendmail.start()

        if listD[1].Stare_ceta_S2 == 'e0' and listD[0].Stare_ceta_S2 != 'e0':
            if listD[1].S2_Cauza_Bloc_Soft !='01':
                name_of_file  ="Stare_ceta_S2_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Stare_ceta_S2"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()

        if listD[1].Stare_ceta_S3 == 'f0' and listD[0].Stare_ceta_S3 != 'f0':

            name_of_file  ="Stare_ceta_S3_" + str(time.time()) +".dat"
            f = open(name_of_file, "wb+")

            #scriu din coada -3  in fisierul de defect deschis
            minus3Chunk = Bits().join(buffer_defects)
            Bits(minus3Chunk).tofile(f)

            list_of_defects_files_opened_for_writing.append(f)

                #start thread count 2 mins and delete the file above
            makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
            makeFile.start()

            message = "Stare_ceta_S3"
            sendmail = threading.Thread(target=sendEmail, args=(message,))
            sendmail.start()

        if listD[1].Stare_ceta_S3 == 'e0' and listD[0].Stare_ceta_S3 != 'e0':
            if listD[1].S3_Cauza_Bloc_Soft !='01':
                name_of_file  ="Stare_ceta_S3_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Stare_ceta_S3"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()


        if listD[1].Stare_ceta_S4 == 'f0' and listD[0].Stare_ceta_S4 != 'f0':
                name_of_file  ="Stare_ceta_S4_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Stare_ceta_S4"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Stare_ceta_S4 == 'e0' and listD[0].Stare_ceta_S4 != 'e0':
            if listD[1].S4_Cauza_Bloc_Soft !='01':
                name_of_file  ="Stare_ceta_S4_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Stare_ceta_S4"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Stare_ceta_S5 == 'f0' and listD[0].Stare_ceta_S5 != 'f0':
                name_of_file  ="Stare_ceta_S5_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Stare_ceta_S5"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Stare_ceta_S5 == 'e0' and listD[0].Stare_ceta_S5 != 'e0':
            if listD[1].S5_Cauza_Bloc_Soft !='01':
                name_of_file  ="Stare_ceta_S5_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Stare_ceta_S5"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Stare_ceta_S6 == 'f0' and listD[0].Stare_ceta_S6 != 'f0':
                name_of_file  ="Stare_ceta_S6_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Stare_ceta_S6"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Stare_ceta_S6 == 'e0' and listD[0].Stare_ceta_S6 != 'e0':
            if listD[1].S6_Cauza_Bloc_Soft !='01':
                name_of_file  ="Stare_ceta_S6_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Stare_ceta_S6"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()

        if listD[1].UsolCompresor == '1' and listD[0].UsolCompresor== '0':
                name_of_file  ="Usol_compresor_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_compresor"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()

        if listD[1].Usol_Ventilator_Compresor == '1' and listD[0].Usol_Ventilator_Compresor== '0':
                name_of_file  ="Usol_Ventilator_Compresor_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Ventilator_Compresor"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_Pompa_Apa_S1  == '1' and listD[0].Usol_Pompa_Apa_S1 == '0':
                name_of_file  ="Usol_Pompa_Apa_S1_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Pompa_Apa_S1"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].S3_Cauza_Bloc_Soft == '1' and listD[0].S3_Cauza_Bloc_Soft== '0':
                name_of_file  ="S3_Cauza_Bloc_Soft_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "S3_Cauza_Bloc_Soft"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_Pompa_Apa_S1  == '1' and listD[0].Usol_Pompa_Apa_S1 == '0':
                name_of_file  ="Usol_Pompa_Apa_S1_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Pompa_Apa_S1"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_Pompa_Apa_S2  == '1' and listD[0].Usol_Pompa_Apa_S2 == '0':
                name_of_file  ="Usol_Pompa_Apa_S2_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Pompa_Apa_S2"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_Pompa_Apa_S3  == '1' and listD[0].Usol_Pompa_Apa_S3 == '0':
                name_of_file  ="Usol_Pompa_Apa_S3_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Pompa_Apa_S3"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_Pompa_Apa_S4  == '1' and listD[0].Usol_Pompa_Apa_S4 == '0':
                name_of_file  ="Usol_Pompa_Apa_S4_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Pompa_Apa_S4"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_Pompa_Apa_S5  == '1' and listD[0].Usol_Pompa_Apa_S5 == '0':
                name_of_file  ="Usol_Pompa_Apa_S5_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Pompa_Apa_S5"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_Pompa_Apa_S6  == '1' and listD[0].Usol_Pompa_Apa_S6 == '0':
                name_of_file  ="Usol_Pompa_Apa_S6_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Pompa_Apa_S6"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_RF1  == '1' and listD[0].Usol_RF1== '0':
                name_of_file  ="Usol_RF1_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_RF1"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_RF2  == '1' and listD[0].Usol_RF2 == '0':
                name_of_file  ="Usol_RF2_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_RF2"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_Trafo1  == '1' and listD[0].Usol_Trafo1 == '0':
                name_of_file  ="Usol_Trafo1_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Trafo1"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_Trafo2  == '1' and listD[0].Usol_Trafo2 == '0':
                name_of_file  ="Usol_Trafo2_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Trafo2"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_Trafo3  == '1' and listD[0].Usol_Trafo3 == '0':
                name_of_file  ="Usol_Trafo3_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Trafo3"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_Trafo4  == '1' and listD[0].Usol_Trafo4 == '0':
                name_of_file  ="Usol_Trafo4_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Trafo4"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_Pompa_Trafo  == '1' and listD[0].Usol_Pompa_Trafo == '0':
                name_of_file  ="Usol_Pompa_Trafo_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Pompa_Trafo"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_V1_S1   == '1' and listD[0].Usol_V1_S1  == '0':
                name_of_file  ="Usol_V1_S1_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_V1_S1"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_V1_S2   == '1' and listD[0].Usol_V1_S2  == '0':
                name_of_file  ="Usol_V1_S2_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_V1_S2"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_V1_S3   == '1' and listD[0].Usol_V1_S3  == '0':
                name_of_file  ="Usol_V1_S3_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_V1_S3"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_V1_S4   == '1' and listD[0].Usol_V1_S4  == '0':
                name_of_file  ="Usol_V1_S4_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_V1_S4"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_V1_S5   == '1' and listD[0].Usol_V1_S5  == '0':
                name_of_file  ="Usol_V1_S5_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_V1_S5"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_V1_S6   == '1' and listD[0].Usol_V1_S6  == '0':
                name_of_file  ="Usol_V1_S6_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_V1_S6"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_V2_S1   == '1' and listD[0].Usol_V2_S1  == '0':
                name_of_file  ="Usol_V2_S1_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_V2_S1"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_V2_S2   == '1' and listD[0].Usol_V2_S2  == '0':
                name_of_file  ="Usol_V2_S2_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_V2_S2"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_V2_S3   == '1' and listD[0].Usol_V2_S3  == '0':
                name_of_file  ="Usol_V2_S3_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_V2_S3"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_V2_S4   == '1' and listD[0].Usol_V2_S4  == '0':
                name_of_file  ="Usol_V2_S4_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_V2_S4"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_V2_S5   == '1' and listD[0].Usol_V2_S5  == '0':
                name_of_file  ="Usol_V2_S5_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_V2_S5"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_V2_S6   == '1' and listD[0].Usol_V2_S6  == '0':
                name_of_file  ="Usol_V2_S6_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_V2_S6"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Supratemperatura_Compresor  == '1' and listD[0].Supratemperatura_Compresor == '0':
                name_of_file  ="Supratemperatura_Compresor_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Supratemperatura_Compresor"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_VCS1   == '1' and listD[0].Usol_VCS1  == '0':
                name_of_file  ="Usol_VCS1_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_VCS1"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_VCS2  == '1' and listD[0].Usol_VCS2 == '0':
                name_of_file  ="Usol_VCS2_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_VCS2"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_VCS3  == '1' and listD[0].Usol_VCS3 == '0':
                name_of_file  ="Usol_VCS3_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_VCS3"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_Ible_S8  == '1' and listD[0].Usol_Ible_S8 == '0':
                name_of_file  ="Usol_Ible_S8_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Ible_S8"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_Clima  == '1' and listD[0].Usol_Clima == '0':
                name_of_file  ="Usol_Clima_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Clima"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_Trafo_Auxiliar  == '1' and listD[0].Usol_Trafo_Auxiliar == '0':
                name_of_file  ="Usol_Trafo_Auxiliar_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Trafo_Auxiliar"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_Ventilatie_SM1  == '1' and listD[0].Usol_Ventilatie_SM1 == '0':
                name_of_file  ="Usol_Ventilatie_SM1_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Ventilatie_SM1"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_Ventilatie_SM2  == '1' and listD[0].Usol_Ventilatie_SM2 == '0':
                name_of_file  ="Usol_Ventilatie_SM2_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Ventilatie_SM2"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if listD[1].Usol_Ible_ICSA  == '1' and listD[0].Usol_Ible_ICSA == '0':
                name_of_file  ="Usol_Ible_ICSA_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Usol_Ible_ICSA"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()
        if  not in_array(listD[1].Stare13,['00','30']) and in_array(listD[0].Stare13,['00','30']):
                name_of_file  ="Stare13_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Stare13"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()

        if  not in_array(listD[1].Stare45,['00','30']) and in_array(listD[0].Stare45,['00','30']):
                name_of_file  ="Stare45_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "Stare45"

                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()


        if listD[1].Stare_IBLE  == 'f0' and listD[0].Stare_IBLE != 'f0':
                name_of_file  ="StareIBLE_" + str(time.time()) +".dat"
                f = open(name_of_file, "wb+")

                #scriu din coada -3  in fisierul de defect deschis
                minus3Chunk = Bits().join(buffer_defects)
                Bits(minus3Chunk).tofile(f)

                list_of_defects_files_opened_for_writing.append(f)

                    #start thread count 2 mins and delete the file above
                makeFile = threading.Thread(target=deleteFileFromList, args=(list_of_defects_files_opened_for_writing,f))
                makeFile.start()

                message = "StareIBLE"
                sendmail = threading.Thread(target=sendEmail, args=(message,))
                sendmail.start()

    lock.release()

emailAcc = deque() # coada de emailuri netransmise ?? marime maxima?
start_time = 0
end_time = 0

list_of_defects_files_opened_for_writing = []

buffer_defects = deque(maxlen = 600) # 3 minute



def workMessage(chunk):
    start_time = time.time()
# your code

    print 'starting thread...', len(chunk)

    n = True
    i=0
    while n :

        b = chunk[i]
        value = struct.unpack('B', b)
        a = 'uint:8= ' + str(value[0])
        b = BitArray(a)
        #print b.hex
        if b.hex =='5a':
            #print 'ok'
            c = chunk[i+1:i+406]
            if convertToHex(c[-1]).hex == '5a':
                print 'ok frame'
        else:
            i = i+1
        if i > 18000:
            n = False




##    for i in range(len(chunk)):
##        b = chunk[i]
##        value = struct.unpack('B', b)
##        a = 'uint:8= ' + str(value[0])
##        b = BitArray(a)
##        print b.hex
##        if b.hex =='5a':
##            elapsed_time = time.time() - start_time
##
##            print 'ok......',  elapsed_time
	#ser.flushInput()


def convertToHex(octet):
     value = struct.unpack('B', octet)
     a = 'uint:8= ' + str(value[0])
     b = BitArray(a)
     return b

counter = 0
lock = threading.Lock()

ser = serial.Serial(
    #port='COM5',\
        port = '/dev/ttyAMA0',\
    baudrate=57600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=0)

connection = None

def reader():
    #global ser


    ser.flushInput()
    ser.flushOutput()
    b = bytearray()
    alist = []
    i = 0
    count = 1

    STAREIBLE = 0
    d = deque(maxlen=2) # coada de frameuri

    sender = "lema.errors@gmail.com"
    receiver= "mihai.miulescu@gmail.com"

    threadRepeting = RepeatEvery(1200, massMail, emailAcc)
    threadRepeting.start()

    #time.sleep(1)
    counter = 0
    frame_counter = 0
    #w = Window()
##    while True:
##        bytesToRead = ser.inWaiting()
##        print bytesToRead
##        a =   ser.read(bytesToRead)
##
##
##
##
##        #time.sleep(0.2)
####        data_waiting  = ser.inWaiting()
####        print data_waiting
##        c = ser.readinto(a)
##
##        b.append(a)
##        i = i+1
##
##    print b
    data = ""
    k = 0

    STAREIBLE = 0
    while True:
        try:
            #data = data + ser.read(1)       # read one, blocking
            #time.sleep(0.2)                   # give it time to put more in waiting
            #n = ser.inWaiting()


                         # look if there is more

            bytesToRead = ser.inWaiting()
            n = ser.read(bytesToRead)
            data = data + n
            if len(data)>25000:
                i = 0
                while n :
                    b = data[i]
                    value = struct.unpack('B', b)
                    a = 'uint:8= ' + str(value[0])
                    b = BitArray(a)
                #print b.hex
                    if b.hex =='5a':
                    #print 'ok'
                        i = i + 405
                        c = data[i-404:i+1]
                        s2 = Bits(bytes = c)
                        icsaData = Bits(bytes = c[2:66])
                        icolData = Bits(bytes = c[69:323])
                        ivmsData = Bits(bytes = c[327:360])
                        gpsData = Bits(bytes = c[364:385])
                        imtoData = Bits(bytes = c[389:404])
                        #c = data[i+1:i+406]
                        if convertToHex(c[-1]).hex == '5a' and Bits(bytes = c[0:3]).hex == '000040':
                            start = Bits(hex = '0xF5')
                            stop = Bits(hex = '0xF6')
                            stringhex = Bits().join(['0xF5', icolData, icsaData, ivmsData, gpsData, imtoData, '0xF6'])
		            		
                            #stringhex = Bits().join(['0xF5', s2, '0xF6'])
                            #f.write(stringhex.hex)
                            global start_time
                            start_time = time.time()

                            if isInt(counter / 9000.0): # 600 = un minut
                                #creez  un fisier chhunk si il deschid
                                name_of_chunk_file = "data" + str((counter//9000)) + ".dat"
                                current_chunk_file = open(name_of_chunk_file,"wb+")

                            previously_curent_file = "data" + str((counter//9000)-1)
                            if os.path.isfile( previously_curent_file + ".dat"): # adica am incheiat o arhiva si trecem la urmatoarea
                            #if os.path.isfile( "data" + str((counter//600)-1) + ".dat"):
                                #print "file exist"
                                appMess = threading.Thread(target=createArchiveZip, args=(previously_curent_file,))
                                appMess.start()
				appMess.join()

                            #scrie in /lucru as ussualy
			    try:
                                Bits(stringhex).tofile(current_chunk_file)
			    except:
				pass

                            #scrie in toate fisierele de erori deschise
                            for file in list_of_defects_files_opened_for_writing:
                                #print"++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++am scris in " + str(file)
                                try:
			            Bits(stringhex).tofile(file)
				except:
				    pass
                            #adauga in coada de arhiva -3
                            buffer_defects.append(Bits(stringhex))
                            if connection is not None:
                                #print Bits(stringhex)
                                try:
				    connection.sendall(c)
				except socket.error,e:
				    if isinstance(e.args,tuple):    
                                        print "errno is %d" % e[0]
					if e[0] == errno.EPIPE:
					    print "Remote Disconect"
					else:
					    pass
				    else:
					print "socket error",e
				    connection.close()
				    
				except IOError, e:
				    print 'Got Error', e
				    
				    

                            #Bits(stringhex).tofile(f)

                            counter = counter+1
                            #print 'counter1: ' , counter
                            start_time = time.time()

			    w = Window()
                            w.stare_forta = s2[856:864].hex
                            w.D7KIzolareMT1 = s2[632:640].bin[0]
                            w.D0KIzolareMT2 = s2[640:648].bin[7]
                            #print s2[0:1260].hex
                            w.D1KIzolareMT3 = s2[640:648].bin[6]
                            w.D7KIzolareMT4 = s2[664:672].bin[0]
                            w.D0KIzolareMT5 = s2[672:680].bin[7]
                            w.D1KIzolareMT6 = s2[672:680].bin[6]
                            w.RegimASC = s2[952:960].bin[4]
                            w.DebitRedusUleiTrafo = s2[928:936].bin[0]
                            w.AtentionareNivelRedusTrafo = s2[928:936].bin[1]
                            w.Cauza_Bloc_Soft_S1 = s2[1150:1158].hex
                            w.Cauza_Bloc_Soft_S2 = s2[1352:1360].hex
                            w.Cauza_Bloc_Soft_S3 = s2[1150:1158].hex
                            w.Cauza_Bloc_Soft_S4 = s2[1150:1158].hex
                            w.Cauza_Bloc_Soft_S5 = s2[1150:1158].hex
                            w.Cauza_Bloc_Soft_S6 = s2[1150:1158].hex
                            w.Stare_ceta_S1 = s2[984:992].hex
                            w.Stare_ceta_S2 = s2[1176:1184].hex
                            w.Stare_ceta_S3 = s2[1386:1494].hex
                            w.Stare_ceta_S4 = s2[1560:1568].hex
                            w.Stare_ceta_S5 = s2[1752:1800].hex
                            w.Stare_ceta_S6 = s2[1944:1952].hex
                            w.S1_Cauza_Bloc_Soft = s2[1160:1168].hex
                            w.S2_Cauza_Bloc_Soft = s2[1352:1360].hex
                            w.S3_Cauza_Bloc_Soft = s2[1544:1552].hex
                            w.S4_Cauza_Bloc_Soft = s2[1736:1744].hex
                            w.S5_Cauza_Bloc_Soft = s2[1928:1936].hex
                            w.S6_Cauza_Bloc_Soft = s2[2120:2128].hex
                            w.UsolCompresor = s2[144:152].bin[7]
                            w.Usol_Ventilator_Compresor = s2[144:152].bin[6]
                            w.Usol_Pompa_Apa_S1 = s2[144:152].bin[5]
                            w.Usol_Pompa_Apa_S2 = s2[144:152].bin[4]
                            w.Usol_Pompa_Apa_S3 = s2[144:152].bin[3]
                            w.Usol_Pompa_Apa_S4 = s2[144:152].bin[2]
                            w.Usol_Pompa_Apa_S5 = s2[144:152].bin[1]
                            w.Usol_Pompa_Apa_S6 = s2[144:152].bin[0]
                            w.Usol_RF1 = s2[152:160].bin[7]
                            w.Usol_RF2 = s2[152:160].bin[6]
                            w.Usol_Trafo1 = s2[152:160].bin[5]
                            w.Usol_Trafo2 = s2[152:160].bin[4]
                            w.Usol_Trafo3 = s2[152:160].bin[3]
                            w.Usol_Trafo4 = s2[152:160].bin[2]
                            w.Usol_Pompa_Trafo = s2[152:160].bin[1]
                            w.Usol_V1_S1 = s2[152:160].bin[0]
                            w.Usol_V1_S2 = s2[160:168].bin[7]
                            w.Usol_V1_S3 = s2[160:168].bin[6]
                            w.Usol_V1_S4 = s2[160:168].bin[5]
                            w.Usol_V1_S5 = s2[160:168].bin[4]
                            w.Usol_V1_S6 = s2[160:168].bin[3]
                            w.Usol_V2_S1 = s2[160:168].bin[2]
                            w.Usol_V2_S2 = s2[160:168].bin[1]
                            w.Usol_V2_S3 = s2[160:168].bin[0]
                            w.Usol_V2_S4 = s2[168:176].bin[7]
                            w.Usol_V2_S5 = s2[168:176].bin[6]
                            w.Usol_V2_S6 = s2[168:176].bin[5]
                            w.Supratemperatura_Compresor = s2[168:176].bin[2]
                            #if isInt(counter/10.0):
				#w.Usol_VCS1 = '1'
			    #else:
				#w.Usol_VCS1 = '0'

			    w.Usol_VCS1 = s2[200:208].bin[4]
                            w.Usol_VCS2 = s2[200:208].bin[3]
                            w.Usol_VCS3 = s2[200:208].bin[2]
                            w.Usol_Ible_S8 = s2[208:216].bin[7]
                            w.Usol_Clima = s2[208:216].bin[6]
                            w.Usol_Trafo_Auxiliar = s2[208:216].bin[5]
                            w.Usol_Ventilatie_SM1 = s2[208:216].bin[4]
                            w.Usol_Ventilatie_SM2 = s2[208:216].bin[3]
                            w.Usol_Ible_ICSA = s2[208:216].bin[1]
                            w.Stare13 = s2[32:40].hex
                            w.Stare45 = s2[40:48].hex
                            if s2[24:32].hex == '06':
                                 w.Stare_IBLE = s2[272:280].hex
                                 STAREIBLE = s2[272:280].hex
                            else:
                                w.Stare_IBLE = STAREIBLE



                            elapsed_time =  time.time() -start_time
                            #print 'timp trecut =========================  ' , elapsed_time
                            k = k+1
                            #print 'ok frame',k
                            #w.bigString = j
                            appMess = threading.Thread(target=appendWithMessage, args=(d,w))
                            appMess.start()
			    appMess.join()
                    else:
                        i = i+1

                    if i > 24595:
                        n = False
                        #print 'am iesit'

                #print data[26:90]
##                appMess = threading.Thread(target=workMessage, args=(data,))
##                appMess.start()
                data = ""







                #k = k+1
                #print 'threadul ', k
                #ser.flushInput()

##                 for i in range(len(data)):
##                    b = data[i]
##                    value = struct.unpack('B', b)
##                    a = 'uint:8= ' + str(value[0])
##                    b = BitArray(a)
##                    if b.hex =='5a':
##                        print 'ok'
##                 data = ""

                   # make sure you have the whole line and format

        except serial.SerialException:
            sys.stderr.write("Waiting for %s to be available" % (ser.name))
            sys.exit(1)
    ser.close()


def main():

    thread_read = threading.Thread(target= reader)
    thread_read.start()
    srv = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    srv.bind(('',7777))
    srv.listen(1)

    while(True):
        global connection
        try:
            connection,addr = srv.accept()
	except KeyboardInterrupt:
	    break
	except socket.error,msg:
	    sys.stderr.write('ERROR: %s\n' %msg)
          



if __name__ == '__main__':
    main()
