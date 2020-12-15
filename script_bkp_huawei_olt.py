# Thanks to _Foundations of Python Network Programming_  
# for the following code:  
import os  
import sys
import time
import getopt
import ipaddress
import datetime
import telnetlib  
from ftplib import FTP 

#Função que mostra como usar a aplicação
def printUsage():
    print ("python3 script_bkp_dmos.py -f hosts.csv\n")

#Função que valida se o parâmetro passado é realmente um IPv4 
def validateIP(ip):
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return False
    else:
        return True
 
#Essa Função abre o arquivo (.csv) em modo de leitura e adiciona todas a linhas na variável linhas
def importFile(file):
    try:
        arq = open(file,'r') #abre o arquivo em modo de leitura
    except OSError: # em caso de erro finaliza a execução do script
        print ('Erro ao abrir arquivo')
        sys.exit()
    else:
        linhas = arq.readlines() # aqui lê as linhas
        arq.close()
        return linhas

#função principal do script
def backupHost(file,user,password):
    
    arquivo = importFile(file) # chama a Função para abrir e ler o arquivo
    totalHosts = len(arquivo)
    print("Total de Hosts que sera feito BKP: {0}".format(totalHosts)) #conta quantas linhas tem o arquivo
    print ("-----------------------------------------------------------")

    for linha in arquivo: #passa linha por linha, ou seja, host por host do arquivo e executa os comandos abaixo
        piece = linha.split(';')
        if validateIP(piece[0]): #chama Função para validar o ip
            host = piece[0]
        else:
            print ('IP {0} invalido'.format(piece[0]))
            sys.exit()
        file_path = piece[1].rstrip() # segunda parte caminho que ira dentro do servidor FTP

        print("Host: {0}".format(host))
        print("file_path FTP: {0}".format(file_path))
        
        try:
            tn = telnetlib.Telnet(host,23,30)
        except Exception as e:
            print ('1') #valor enviado ao index.php, que por sua vez printa erro ao usuário.
            quit()

        #faz login no host
        tn.read_until(b"User name:")
        tn.write(user.encode('utf-8') + b"\n") 
        time.sleep(.2)
        tn.read_until(b"password:") 
        tn.write(password.encode('utf-8') + b"\n") 
        time.sleep(3)

        tn.write(b"enable\n")
        time.sleep(.3)
        tn.write(b"config\n")
        time.sleep(.3)
        tn.write(b"display current-configuration | no-more\n\n")
        time.sleep(10) #tempo grande pois olts com muitas onus demoram bastante pra retornar todas as informacoes
        tn.write(b"\nfimdocomando\n")
        return_lineid = tn.read_until('fimdocomando'.encode('utf-8'),3).decode('utf-8')
        data_return = return_lineid.splitlines()

        #Fecha a conexao com a host
        tn.write("quit\n".encode('utf-8'))
        time.sleep(.3)
        tn.write("quit\n".encode('utf-8'))
        time.sleep(.3)
        tn.write('y'.encode('utf-8') + "\n".encode('utf-8'))
        time.sleep(.3)
        tn.close()

        date = datetime.datetime.today()

        #cria o nome do arquivo txt com o padrao IPHost+DD-MM-AAA.txt, EX: "99.99.99.99_24-11-2020.txt"
        file_name = host+"_"+str(date.day)+"-"+str(date.month)+"-"+str(date.year)+".txt"

        #grava linha por linha o retorno do comando "show running-config | nomore", e a cada linha da um enter
        text_file = open(file_name, "wt")
        for linha in data_return: #Caso ele não encontre nada, retorna Failure
            n = text_file.write(str(linha))
            n = text_file.write('\n')
        text_file.close()

        #abre conexão com o servidor FTP e envia o arquivo dentro do File_path indicado
        ftp = FTP('99.99.99.99')  
        ftp.login('user_ftp','Pass_FTP')
        ftp.encoding = "utf-8"  
        file_send = file_name  
        with open(file_send, "rb") as file:
            ftp.storbinary(f"STOR {file_path}/{file_send}", file)
            print("Enviado ao servidor FTP o arquivo: {0}".format(file_send))
        ftp.quit()


def main(argv):

    if sys.version_info[0] < 3:
        raise Exception("Necessario Python 3 ou versao mais recente.")

    start_time = time.time()

    user = 'nomedeusuario'
    password = 'senha_acesso_olt'


    try:               
        opts, args = getopt.getopt(argv,"f:hd",["file=","help","debug"])
    except getopt.GetoptError:
        printUsage()
        sys.exit(2)
 
    if not opts:
        printUsage()
        sys.exit()
    #Laço para chegar e validar cada argumento passado
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            printUsage()
            sys.exit()
        elif opt in ("-d", "--debug"):
            debug = True
        elif opt in ("-f", "--file"):
            if os.path.isfile(arg): #checa se o nome ou diretório do arquivo passado realmente existe
                file = arg
            else:
                print ('File unknown')
                sys.exit()

    print("Arquivo de Hosts que sera feito BKP: {0}".format(file))

    backupHost(file,user,password)

    print("Fim do script! \nTempo levado: %s segundos" % (time.time() - start_time))

if __name__ == "__main__":
    main(sys.argv[1:])