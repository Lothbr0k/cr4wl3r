#! /usr/bin/env python 
# -*- coding: utf-8 -*-

""" 
                    +---------------------------+
                    |  Crawler by Lothbr0k  	|
                    |  con scanner de puertos   |
                    +---------------------------+
            
     ===============================================================================
     Librerias que vamos a emplear a priori si necesitamos mas iremos añadiendolas

     sys       -->  proporciona aceso a variables y a funciones utilizadas o 
                    mantenidas  por el intérprete
    ----------------------------------------------------------------------------
     re          -->    se emplea para el manejo de expresiones regulares
    ----------------------------------------------------------------------------
     os       -->  se emplea para operaciones generales del sistema
    ----------------------------------------------------------------------------
     time     -->  proporciona diversas funciones relacionadas con el tiempo
    ----------------------------------------------------------------------------
     socket   -->  se emplea para usar sockets
    ----------------------------------------------------------------------------
     getopt   -->    análisis de las opciones de línea de comandos cuya API se 
                    ha diseñado para ser familiar para los usuarios de UNIX
    ----------------------------------------------------------------------------
     datetime -->    contiene funciones y clases para trabajar con fechas y horas
    ----------------------------------------------------------------------------
     urllib2  -->  interacción con URLs
    ----------------------------------------------------------------------------
     urlparse -->  divide la URL en componentes
    ----------------------------------------------------------------------------
     httplib  -->  igual que urlib2 pero podemos manejar codigos de error
    ----------------------------------------------------------------------------
     copy     -->  duplicar objetos
    ----------------------------------------------------------------------------
"""


import sys
import re       
import os
import time
import socket
import getopt
import datetime     
import urllib2
import urlparse
import httplib
import copy
from multiprocessing import Process


"""
    =========================
           Clase Crawler
    =========================
"""

class Crawler:
      
    # informacion de uso y ayuda:
    def uso(self):
    
        vernum='1.0.1'
        
        print "+-----------------------------------------------------+"
        print "|             "+ sys.argv[0] + " Version "+ vernum +"                |"
        print "+-----------------------------------------------------+"
        print 
        print "\nUso: %s <opciones>" % sys.argv[0]
        print "Opciones:"
        print "  -h, --help              Muestra este mensaje de ayuda"
        print "  -u, --url               URL para iniciar el rastreo"
        print "  -w, --write             Guarda el rastreo en un fichero local"
        print "  -L, --log-format        Genera log of the requests in CLF"
        print "  -l, --crawl-limit       Numero maximo de links a rastrear"
        print "  -d, --download          Descarga archivos de forma interactiva"
        print "  -p, --PortScanner       Escanea puertos"
		print "				 2-5 -> rango 2 3 4 y 5"
		print "				  2  -> puerto 2"
		print "				 2,5 -> puertos 2 y 5"
        print
        print "Ejemplo: python crawler.py -u http://www.prueba.com -w -p 22"
        print
        sys.exit(1)
        
    # comprueba si la url está bien formateada
    def url_check(self,url):

        try:
        
            #la funcion urlparse.urlparse() separara la url en 4 partes : scheme, netloc, path y query
            url_parsed = urlparse.urlparse(url)
            
            # scheme seria 'http' y netloc seria 'www.prueba.com'
            if url_parsed.scheme and url_parsed.netloc:
                return True
            else:
                return False

        except Exception as inst:
            print ' Excepcion en el metodo url_check'
            return -1
    
    """
         1. Imprime un texto en la salida estándar
         2. Escribir un texto en el archivo dado.
    
         No devuelve ningun valor.      
    """
    def printout(self,input_text,output_file):
    
        try:
            print input_text 
            if output_file:
                try:
                    output_file.write(input_text+'\n')
                except:
                    print ' No guarda los datos' 
    
        except Exception as inst:
            print ' Excepcion en printout'        
            return -1 
    
    """
        Este metodo privado genera una salida common log format que es el estandar de una petición HTTP 
        No devuelve nada.
    """ 
    def __log_line(self, request, response_code, response_size, log_file):

        try:
            try:
                if response_size == -1:
                    content_size = '-'
                else:
                    content_size = str(response_size)
                    
                local_hostname = socket.gethostname()
                local_user = os.getenv('USER')
                timestamp = time.strftime('%e/%b/%Y:%X %z').strip()
                method = request.get_method()
                protocol = 'HTTP/1.1'    # Esta es la versión del protocolo que utiliza urllib2
                user_agent = request.get_header('User-agent')
                url = request.get_full_url()
                
                # COMMON LOG FORMAT
                log_file.write(local_hostname+' '+'-'+' '+local_user+' '+'['+timestamp+']'+' '+'"'+method+' '+url+' '+protocol+'"'+' '+str(response_code)+' '+content_size+' "-" "'+user_agent+'"\n')
    
            except:
                print 'La siguiente peticion no se registra: {0}'.format(request.get_full_url())
    
        except Exception as inst:
            print ' Excepcion en log_line()'
            return -1 

    
    """
        Este metodo privado realiza una petición HTTP de la URL dada con la libreria urllib2. 
        devuelve 2 valores: [peticion,respuesta]
    """
    def __get_url(self,url):

        # Tiempo de respuesta
        tResponses = []

        starttime=0
        endtime=0

        try:
            try:
                starttime= time.time()
				
                request = urllib2.Request(url)
		
                request.add_header('User-Agent','Mozilla/4.0 (compatible;MSIE 5.5; Windows NT 5.0)')

                # Primero hacemos una petición head para ver el tipo de url a rastrear
                request.get_method = lambda : 'HEAD'
               
                opener_web = urllib2.build_opener()

                response = opener_web.open(request)

                # Si se trata de un archivo, no obtenemos el contenido
                if 'text/html' not in response.headers.typeheader:
                    opener_web.close()
                    
                    endtime= time.time()
                    tResponses.append(endtime-starttime)

                    return [request,response]
                
                request.get_method = lambda : 'GET'
               
                opener_web = urllib2.build_opener()

                response = opener_web.open(request)

                opener_web.close()

                endtime= time.time()
                tResponses.append(endtime-starttime)

                return [request,response]
            
            except urllib2.HTTPError,error_code:
                return [request,error_code.getcode()]
            except urllib2.URLError,error_code:
                error = error_code.args[0]
                return [request,error[0]]
            
            except socket.error,error_code:
                error = error_code.args[0]
                try:
                    error = error[0]
                except:
                    pass
                return [request,error]
                
        except KeyboardInterrupt:
            try:
                print '\t Pulse una tecla para continuar' 
                raw_input()
                return ["",1]
            except KeyboardInterrupt:
                return ["",0]
            except Exception as inst:
                print ' Excepcion en el crawl'       
                return -1    
    """
        En este metodo se emplea una expresion regular para encontrar enlaces en una pagina HTML.
        La expresion regular se define en la variable 'lRegex'.

        Devuelve un vector de enlaces extraídos
    """
    
    def __get_links(self, host, link_path, content):

        lRegex = re.compile('[^>](?:href\=|src\=|content\=\"http)[\'*|\"*](.*?)[\'|\"].*?>',re.IGNORECASE)
    
        try:
            # Obtenemos los enlaces en la respuesta
            links = lRegex.findall(content)

            # Analizamos cada enlace
            for link in links:
                try:
                    link_clean = link.strip(' ')
                except:
                    print 'error'
                    
                parsed_link = urlparse.urlparse(link_clean)

                if not parsed_link.scheme and not parsed_link.netloc:
                    if link_clean.startswith('/'):
                        if host.endswith('/'):
                            links[links.index(link)] = host.rstrip('/')+link_clean
                        else:
                            links[links.index(link)] = host+link_clean
                    elif link_clean.startswith('./'):
                            links[links.index(link)] = host+link_clean
                    else:
                        links[links.index(link)] = link_path+link_clean
                else:
                    links[links.index(link)] = link_clean
    
            for link in links:
                links[links.index(link)] = link.split('#')[0]
    
            return links
    
        except Exception as inst:
            print 'Excepcion en el metodo get_links'       
            return -1 
    
    """
        Rastrear una URL determinada. 

        El metodo devuelve: [enlaces rastreados, urls no rastreadas, enlaces a archivos]
    """        
    def crawl(self,url,output_file,crawl_limit,log=False,log_filename='none'):
        
        """
         Codigos de respuesta HTTP
         -----------------------------------------------------------
        """

        error_codes={}
        error_codes['0']='Excepcion de interrupcion del teclado'
        error_codes['1']='Continuamos'
        error_codes['-2']='Nombre o servicio no conocido'
        error_codes['22']='22 Error desconocido'
        # 1xx Respuestas informativas
        error_codes['104']='104 Conexion restablecida por el interlocutor'
        error_codes['110']='110 Conexion agotada'
        error_codes['111']='111 Conexion rechazada'
        # 2xx Peticiones correctas
        error_codes['200']='200 OK, documento entregado correctamente'
        error_codes['202']='202 Aceptada, pero la petición no es completada con exito'
        error_codes['204']='204 Sin contenido'
        # 3xx Redirecciones
        error_codes['300']='300 Multiples opciones'
        error_codes['301']='301 Movido permanentemente'
        error_codes['302']='302 Movido temporalmente'
        error_codes['304']='304 No modificado'
        error_codes['305']='305 Use Proxy'
        error_codes['306']='306 Cambie de Proxy'
        error_codes['307']='307 Redireccion temporal'
        # 4xx Errores de cliente
        error_codes['400']='400 Solicitud incorrecta'
        error_codes['401']='401 No autorizado'
        error_codes['402']='402 Pago requerido'
        error_codes['403']='403 Prohibido, el conocido Forbidden'
        error_codes['404']='404 No encontrado'
        error_codes['405']='405 Metodo no permitido'
        error_codes['407']='407 Autenticacion proxy requerida'
        error_codes['408']='408 Teimpo de espera agotado'
        # 5xx Errores de servidor
        error_codes['500']='500 Error interno'
        error_codes['501']='500 No implementado'
        error_codes['503']='503 Servicio no disponible'
        error_codes['504']='504 Tiempo de espera de gateway agotado'
        error_codes['505']='505 Version de HTTP no soportada'
        error_codes['9999']='El servidor responde con un código de estado HTTP que no entendemos'
        
        # almacenamos las direcciones URL restante a rastrear
        urls_crawled = []
        urls_not_crawled = []
        links_crawled = []
        links_extracted = []
        files=[]
        crawl_limit_flag=False
        ip = ""

        urls_crawled.append(url)

        if (crawl_limit>0):
            crawl_limit_flag=True

        try:
            self.printout(' Sitio a rastrear: '+ url,output_file)
            self.printout(' Hora de inicio: '+str(datetime.datetime.today()).rpartition('.')[0],output_file)
            if output_file:
                self.printout(' archivo de salida: '+output_file.name,output_file)
            if log:
                self.printout(' Formato de salida de log: '+log_filename.name,output_file)

            self.printout('',output_file)
            url_parsed = urlparse.urlparse(url)
            ip = socket.gethostbyname(url_parsed.netloc)
            self.printout(' Crawling IP: \t'+ ip ,output_file)

            while urls_crawled:
                if crawl_limit_flag:
                    if (len(links_crawled) >= crawl_limit):
                        break
                try:
                    # Extraemos la siguiente url a rastrear
                    url = urls_crawled[0]
                    urls_crawled.remove(url)

                    # Añadimos la url de los enlaces rastreados
                    links_crawled.append(url)

                    # Mostramos la url que se rastrea
                    self.printout('    '+str(url),output_file)

                    # Extraemos los host de las url rastreadas    
                    url_parsed = urlparse.urlparse(url)
                    host = url_parsed.scheme + '://' + url_parsed.netloc

                    if url_parsed.path.endswith('/'):
                        link_path = host + url_parsed.path
                    else:
                        link_path = host + url_parsed.path.rpartition('/')[0] + '/'

                    # obtenemos la respuesta de la dirección URL
                    [request,response] = self.__get_url(url)
                    
                    # Si hay respuesta
                    if response:
                        # Si el servidor no devuelve error
                        if not isinstance(response, int):
                            content = response.read()
    
                            if log:
                                self.__log_line(request,response.getcode(),len(content),log_filename)
    
                            # Imprimimos el tipo de archivo de la pagina rastreada
                            if response.headers.typeheader:
                                # Si no es un archivo HTML
                                if 'text/html' not in response.headers.typeheader:
                                    if url not in files:
                                        files.append([url,str(response.headers.typeheader.split('/')[1].split(';')[0])])
                                   
                                else:
                                   
                                    links_extracted = self.__get_links(host, link_path, content)
                                    links_extracted.sort()
    
                                    # Agregamos nuevos enlaces a la lista de URL a rastrear
                                    for link in links_extracted:
                                        parsed_link= urlparse.urlparse(link)
                                        link_host = parsed_link.scheme + '://' + parsed_link.netloc
    
                                        # Rastreamos las urls del mismo host
                                        if link_host == host:
                                            if link not in links_crawled and link not in urls_crawled:
                                                urls_crawled.append(link)
                                        elif link not in urls_not_crawled:
                                            urls_not_crawled.append(link)
                        else:
                            # Imprimimos el codigo de error
                            self.printout('\t '+error_codes[str(response)],output_file)
                            if log:
                                self.__log_line(request,response,-1,log_filename)
                    else:
                        if response==1:
                            continue
                        if response==0:
                            self.printout('\t '+error_codes[str(response)],output_file)
                            break

                except KeyboardInterrupt:
                    try:
                        print ' Pulsa una tecla para continuar' 
                        raw_input()
                        continue
                    except KeyboardInterrupt:
                        print ' Saliendo'
                        break    

                except Exception as inst:
                    print 'Excepción dentro del while del metodo crawl.'
                    print 'Respuesta: {0}'.format(response)
                    break
            
            self.printout('[*] Total urls crawled: '+str(len(links_crawled)),output_file)
            self.printout('',output_file)

            return [links_crawled,urls_not_crawled,files]
            
        # si pulsamos CTRL-C producimos una interrupcion de teclado
        except KeyboardInterrupt:
            try:
                print ' Presione una tecla para continuar' 
                raw_input()
                return 1
            except KeyboardInterrupt:
                print 'interrupcion de teclado. Salimos.'
                return 1
           
        except Exception as inst:
            print ' Excepcion en el crawl'
            print type(inst)     # instanciamos la excepcion
            print inst.args      # argumentos almacenados en .args
            print inst           # args para imprimir directamente
            x, y = inst          # args se descomprimen directamente
            print 'x =', x
            print 'y =', y
            sys.exit(1)
            
            
    """
        Este metodo identifica directorios y directorios indexados
        devuelve los siguientes valores: [directorios encontrados, directorios indexados]
    """          
    def search_directorios(self, links, output_file, log_filename='none'):
            
        directorios=[]
        indexados=[]
        request=""
        response=""
        title=""
    
        try:
    
            # Identificamos los directorios
            for i in links:
                while ( len(i.split('/')) > 4 ):
                    i=i.rpartition('/')[0]
                    if ( ( i+'/' )  not in directorios ):
                        directorios.append(i+'/')
    
            # ordenamos los directorios
            directorios.sort()
            
            self.printout(' Directorios encontrados:',output_file)
            for directory in directorios:
                self.printout('   [-] '+directory,output_file)
            self.printout('[*] Total de directorios: '+str(len(directorios)),output_file)
            self.printout('',output_file)
            
            self.printout(' Directorios indexados',output_file)
            
            cargando='-'
            for directory in directorios:
                sys.stdout.flush()
                sys.stdout.write(cargando)
                if len(cargando)>30:
                    cargando='-'
                cargando=cargando+'-'
                try:
                    
                    # Obtenemos la respuesta de la url
                    [request,response] = self.__get_url(directory)        
    
                    # Si hay respuesta                                           
                    if response:
                        # Si el servidor no devuelve error              
                        if not isinstance(response, int):
                            content = response.read()
    
                            start_position = content.find('<title>')
                            if start_position != -1:
                                end_position = content.find('</title>', start_position+7)
                            if end_position != -1:
                                title = content[start_position+7:end_position]
    
                            if title:
                                if title.find('Index of') != -1:
                                    self.printout('\n   [!] '+directory,output_file)
                                    indexados.append(directory)
                        
                    else:
                        if response==1:
                            continue
                        if response==0:
                            print 'Saltamos el resto de directorios'
                            break
    
                except KeyboardInterrupt:
                    try:
                        print ' Pulse una tecla para continuar' 
                        raw_input()
                        pass
                    except KeyboardInterrupt:
                        print ' Saliendo'
                        break
                except Exception as inst:
                    print ' Excepcion en indexados'
                    return 1    
    
            self.printout('\n[*] Total directorios indexados: '+str(len(indexados)),output_file)
            self.printout('',output_file)
  
            return [directorios,indexados]
    
        except Exception as inst:
            print ' Excepcion en search_directorios'
            return 1
    
    """
        Este método detecta los links externos. Los links que no coincidan con la URL dada se consideran como externo.
        No devuelve nada. 
    """
    def get_external_links(self, url, external, output_file):
  
        web_externa = []
    
        try:
            url_parsed = urlparse.urlparse(url)
            dominio = url_parsed.netloc.split('www.')[-1]
    
            self.printout('',output_file)
            self.printout(' Subdominios encontrados: ',output_file)
            tmp=[]
            for link in external:
                parsed = urlparse.urlparse(link)
                if dominio in parsed.netloc:
                    subdominio = parsed.scheme+'://'+parsed.netloc
                    if subdominio not in tmp:
                        tmp.append(subdominio)
                        self.printout('   [-] '+subdominio,output_file)
            self.printout('[*] Total:  '+str(len(tmp)),output_file)
           
            self.printout('',output_file)
            self.printout(' Direcciones Email: ',output_file)
            for link in external:
                if 'mailto' in urlparse.urlparse(link).scheme:
                    self.printout('   [-] '+link.split(':')[1].split('?')[0],output_file)
            
            self.printout('',output_file)
            self.printout(' Se hace referencia a las siguientes web: ',output_file)
            for link in external:
                parsed = urlparse.urlparse(link)
                if parsed.netloc:
                    if dominio not in parsed.netloc:
                        dominio_externo = parsed.scheme+'://'+parsed.netloc 
                        if dominio_externo not in web_externa:
                            web_externa.append(dominio_externo)
            web_externa.sort()
            for link in web_externa:
                self.printout('   [-] '+link,output_file)
            self.printout('[*] Total:  '+str(len(web_externa)),output_file)
          
        except Exception as inst:
            print 'Excepcion en get_external_links()'
            return -1
        
    """
        Este metodo encuentra ficheros durante el crawling.
    """
    def search_ficheros(self, files, output_file):

        try:
            if len(files)>0:
                self.printout(' Ficheros encontrados:',output_file)
                
                # We print the files found during the crawling
                for [i,j] in files:
                    self.printout('   [-] '+str(i)+'  ('+str(j)+')',output_file)
                   
                self.printout('[*] Total files: '+str(len(files)),output_file)

        except Exception as inst:
            print 'Excepcion en search_ficheros()'
            return 1 
    """
         metodo en el que usuario puede seleccionar manualmente los archivos para descargar
    
         devuelve una lista de las extensiones de los archivos que se encuentran durante el crawling.
    """
    def download_archivos(self,extensions_to_download,files,output_file):
    
        list_download=[]
        extensions=[]
    
        try:
            if len(files)>0:
                # Buscamos los tipos de archivos    
                for [i,j] in files:
                    if j not in extensions:
                        extensions.append( j )

                print    
                print ' [--]Empezando a descargar archivos[--]'
                print ' Se encontraron los siguientes archivos:'
                print '   ',
                print extensions
                print '    Selecciona el tipo de archivo a descargar. Ej.: css,pdf,jpg.'
                extensions_to_download= raw_input('    ')
    
                # Buscamos archivos que coinciden con el tipo proporcionado   
                for [i,j] in files:
                    if (j in extensions_to_download):
                        list_download.append(i)    
    
                #  Si hay al menos un archivo que coincida, se crea un directorio y se descargan
                if ( len(list_download) > 0 ):
                    # Obtenemos los archivos encontrados
                    self.printout('',output_file)
                    self.printout(' Descarga de archivos especificados: '+extensions_to_download,output_file)
                    self.printout('[*] Total de archivos descargados: '+str(len(list_download)),output_file)
    
                    # Creamos directorio de archivos descargados
                    try:
                        output_directory = output_name.rpartition('.')[0]+'ficheros_crawl'
                        os.mkdir(output_directory)
                        self.printout('[--] Directorio: '+output_directory,output_file)
                    except OSError, error:
                        if 'File exists' in error:
                            print '\n El directorio ya existe. Pulsa una tecla para sobreescribir o CTRL+C para cancelar la descarga'
                            try:
                                raw_input()
                                self.printout('[--] Directorio: '+output_directory,output_file)
                            except KeyboardInterrupt:
                                self.printout('\n Descargar archivos cancelada',output_file)
                                return 1 
                        else:
                            self.printout('\n Descargar archivos cancelada. Error creando directorio.',output_file)
    
    
                    #Descargamos archivos
                    for i in list_download:
                        self.printout('   [-] '+i,output_file)
    
                        [request,response] = self.__get_url(i.replace(' ','%20'))        
    
                        if response:
                            if not isinstance(response, int):
                                response = response.read()
                                try:
                                    #cambiamos la extension por txt para evitar ejecutables
                                    nFicheroExt = i.rpartition('/')[2]
                                    nFichero = nFicheroExt.rpartition('.')[0]
                                    
                                    local_file=open(output_directory+'/'+nFichero+'.txt','w')
                                except OSError, error:
                                    if 'File exists' in error:
                                        pass
                                    else:
                                        self.printout('   [-] Imposible crear el archivo de salida para: '+output_directory+'/'+nFichero+'.txt',output_file)
    
                                if local_file:
                                    local_file.write(response)
                                    local_file.close()
    
                    self.printout('[--] Descarga completada',output_file)
                    self.printout('',output_file)
                    
                else:
                    self.printout('[--] No ha seleccionado ningun fichero a descargar',output_file)
                    self.printout('',output_file)
                    
            return extensions
                        
        except Exception as inst:
            print 'Exception en download_archivos()'
            return -1

    """
        =========================
            metodo PortScanner
        =========================
    """
    def PortScanner(self, host, port, services):

	self.port = int(port)
	socket.setdefaulttimeout(1)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            print e
            sys.exit()

	service = "unknown"
	for serv in services:
	    serv = serv.strip("\n")
	    if str(port) in serv.split():
	        service = services[port]
		break
        try:
	    s.connect((host, self.port))
            self.printout('%s\tOPEN\t%s' % (str(port), service),output_file)
        except:
            self.printout('%s\tCLOSED\t%s' % (str(port), service),output_file)
	finally:
            s.close()

         
"""
    =========================
           Principal
    =========================
"""            
if __name__ == '__main__':
    
    #Definimos los servicios asociados a los puertos

    servs = {'15':'netstat','18':'msp','21':'ftp','22':'ssh','23':'telnet','25':'SMTP','42':'nameserver','43':'whois','49':'tacacs',
	'50':'re-mail-ck','53':'dns','65':'tacacs-db','66':'oracle sqlnet','67':'bootps','68':'bootpc','70':'gopher','77':'rje',
	'79':'Finger','80':'http','87':'link','88':'kerberos','95':'supdup','101':'hostnames','102':'iso-tsap','104':'acr-nema',
	'105':'csnet-ns','107':'rtelnet','109':'pop2','110':'pop3','111':'sunrpc','113':'auth','115':'sftp','117':'uucp-path',
	'119':'nntp','123':'ntp','129':'pwdgen','135':'loc-srv','137':'netbios-ns','138':'netbios-dgm','139':'netbios-ssn',
	'143':'imap2','161':'snmp','162':'snmp-trap','163':'cmip-man','164':'cmip-agent','174':'mailq','177':'xdmcp','178':'nextstep',
	'179':'bgp','191':'prospero','194':'irc','199':'smux','201':'at-rtmp','202':'at-nbp','204':'at-echo','206':'at-zis',
	'209':'qmtp','210':'z3950','213':'ipx','220':'imap3','345':'pawserv','346':'zserv','347':'fatserv','369':'rpc2portmap',
	'370':'codaauth2','371':'clearcase','372':'ulistserv','389':'ldap','406':'imsp','427':'svrloc','443':'https','444':'snpp',
	'445':'microsoft-ds','464':'kpasswd','465':'ssmtp','487':'saft','500':'isakmp','512':'exec','513':'login','514':'shell','515':'printer',
	'526':'tempo','530':'courier','531':'conference','532':'netnews','538':'gdomap','540':'uucp','543':'klogin','544':'kshell',
	'546':'dhcpv6-client','547':'dhcpv6-server','548':'afpovertcp','549':'idfp','554':'rtsp','556':'remotefs','563':'nntps','587':'submission',
	'607':'nqs','610':'npmp-local','611':'npmp-gui','612':'hmmp-ind','628':'qmqp','631':'ipp','636':'ldaps','655':'tinc','706':'silc',
	'749':'kerberos-adm','765':'webster','775':'moira-db','777':'moira-update','779':'moira-ureg','783':'spamd','808':'omirr','873':'rsync',
	'989':'ftps-data','990':'ftps','992':'telnets','993':'imaps','994':'ircs','995':'pop3s','1001':'customs','1080':'socks','1093':'proofd',
	'1094':'rootd','1099':'rmiregistry','1178':'skkserv','1194':'openvpn','1214':'kazaa','1236':'rmtcfg','1241':'nessus','1300':'wipld',
	'1313':'xtel','1314':'xtelw','1352':'lotusnote','1433':'ms-sql-s','1434':'ms-sql-m','1524':'ingreslock','1525':'prospero-np','1529':'support',
	'1645':'datametrics','1646':'sa-msg-port','1649':'kermit','1677':'groupwise','1701':'l2f','1812':'radius','1813':'radius-acct','1863':'msnp',
	'1957':'unix-status','1958':'log-server','1959':'remoteping','2000':'cisco-sccp','2003':'cfinger','2049':'nfs','2086':'gnunet',
	'2101':'rtcm-sc104','2119':'gsigatekeeper','2121':'frox','2135':'gris','2150':'ninstall','2401':'cvspserver','2430':'venus','2431':'venus-se',
	'2432':'codasrv','2433':'codasrv-se','2583':'mon','2600':'zebrasrv','2601':'zebra','2602':'ripd','2603':'ripngd','2604':'ospfd','2605':'bgpd',
	'2606':'ospf6d','2607':'ospfapi','2608':'isisd','2628':'dic','2792':'f5-globalsite','2811':'gsiftp','2947':'gpsd','2988':'afbackup',
	'2989':'afmbackup','3050':'gds-db','3150':'icpv2','3260':'iscsi-target','3306':'mysql','3493':'nut','3632':'distcc','3689':'daap',
	'3690':'svn','4031':'suucp','4094':'sysrqd','4190':'sieve','4224':'xtell','4369':'epmd','4353':'f5-iquery','4373':'remctl','4557':'fax',
	'4559':'hylafax','4569':'iax','4600':'distmp3','4691':'mtn','4899':'radmin-port','4949':'munin','5002':'rfe','5050':'mmcc',
	'5051':'enbd-cstatd','5052':'enbd-sstatd','5060':'sip','5061':'sip-tls','5151':'pcrd','5190':'aol','5222':'xmpp-client','5269':'xmpp-server',
	'5308':'cfengine','5353':'mdns','5354':'noclog','5355':'hostmon','5432':'postgresql','5556':'freeciv','5666':'nrpe','5667':'nsca','5672':'amqp',
	'5674':'mrtd','5675':'bgpsim','5680':'canna','5688':'ggz','6000':'x11','6001':'x11-1','6002':'x11-2','6003':'x11-3','6004':'x11-4',
	'6005':'x11-5','6006':'x11-6','6007':'x11-7','6346':'gnutella-svc','6347':'gnutella-rtr','6444':'sge-qmaster','6445':'sge-execd',
	'6446':'mysql-proxy','6566':'sane-port','6667':'ircd','7000':'afs3-fileserver','7001':'afs3-callback','7002':'afs3-prserver',
	'7003':'afs3-vlserver','7004':'afs3-kaserver','7005':'afs3-volser','7006':'afs3-errors','7007':'afs3-bos','7008':'afs3-update',
	'7009':'afs3-rmtsys','7100':'font-service','8021':'zope-ftp','8080':'http-alt','8081':'tproxy','8088':'omniorb','8990':'clc-build-daemon',
	'9098':'xinetd','9101':'bacula-dir','9102':'bacula-fd','9103':'bacula-sd','9418':'git','9667':'xmms2','9673':'zope','10000':'webmin',
	'10050':'zabbix-agent','10051':'zabbix-trapper','10080':'amanda','10081':'kamanda','10082':'amandaidx','10083':'amidxtape','10809':'nbd',
	'11201':'smsqp','11371':'hkp','13720':'bprd','13721':'bpdbm','13722':'bpjava-msvc','13724':'vnetd','13782':'bpcd','13783':'vopied',
	'15345':'xpilot','17004':'sgi-cad','20011':'isdnlog','20012':'vboxd','22125':'dcap','22128':'gsidcap','22273':'wnn6','24554':'binkp',
	'27374':'asp','30865':'csync2','57000':'dircproxy','60177':'tfido','60179':'fido'}
    
    log = False
    
    claseCrawl = Crawler();        #instanciamos nuestra clase
    
    url_crawl = ""
    limit_crawl = 0
    starttime=0
    endtime=0

    links_crawled = []
    externals_url = []
    files = []
    save_output=False
    output_name = ""
    output_file = ""
    log_name = ""
    log_file = ""
    download_flag=False
    extensions = ""
    ports_scan = ""
    port_flag=False
    
    try:

        # Definimos los argumentos que va a soportar el script
        opts, args = getopt.getopt(sys.argv[1:], "hwu:Ll:dp:", ["help","write","url=","log-format","limit-crawl=","download","portScan="])


    except getopt.GetoptError: claseCrawl.uso()    

    for opt, arg in opts:
        if opt in ("-h", "--help"): claseCrawl.uso()
        if opt in ("-w", "--write"): save_output=True
        if opt in ("-u", "--url"): url_crawl = arg
        if opt in ("-L", "--log-format"): log = True
        if opt in ("-l", "--limit-crawl"): limit_crawl = int(arg)
        if opt in ("-d", "--download"): download_flag=True
        if opt in ("-p", "--portScan"):
            ports_scan = arg
            port_flag = True
	    if args:
		print '[!] Uso incorrecto de la opcion -p'
		print ' --> compruebe que no haya espacios entre puerto y puerto'
		sys.exit()

    try:

	#Comprobamos la forma de uso del -p
	if port_flag:
	    ports_error = ports_scan
	    if (ports_error.find('-')>=0):
		if (ports_error.count('-')>1):
		    print "\n[!]forma de rango incorrecta\n"
		    claseCrawl.uso()
		    sys.exit()

	        ports_error = ports_error.split('-')
		    
	        if not ports_error[0].isdigit() or not ports_error[1].isdigit():
       	            print "\n[!]revise que los puertos introducidos son numericos\n"
		    claseCrawl.uso()
		    sys.exit()

	        if ports_error[0] > ports_error[1]:
       	            print "\n[!] revise que el primer puerto sea menor que el segundo del rango\n"
		    print "--> "+ports_error[0]+" es mayor que "+ports_error[1]
		    claseCrawl.uso()
		    sys.exit()

	    elif (ports_error.find(',')>=0):
	        ports_error = ports_error.split(',')
	        for port in ports_error:
		    if not port.isdigit():
		        print "\n[!]revise que los puertos introducidos son numericos\n"
		        print "--> %s no es un digito" % port
		        sys.exit()

        if claseCrawl.url_check(url_crawl):
		
            """
             almacenamos la fecha formateada y con str la convertimos a string
             el datetime.datetime.today() nos devuelve 2013-05-07 13:03:43.522000
             con el rpartition tendriamos '2013-05-07 13:03:43' , '522000'
             con el 0 nos quedamos con la parte de 2013-05-07 13:03:43 y la formateamos a nuestro gusto
             esto lo usaremos para el nombre del log
            """

            date = str(datetime.datetime.today()).rpartition('.')[0].replace('-','').replace(' ','_').replace(':','')
            
            # Guardamos la salida en un .crawler si no existe ya
            if save_output:
                output_name = urlparse.urlparse(url_crawl).netloc+'.crawler'
                try:
                    output_file = open(output_name,'w')
                except OSError, error:
                    if 'Existe el fichero' in error:
                        pass
                    else:
                        output_name = ""
            else:
                output_name = ""
                
            # Guardamos el log en un .log si no existe ya
            if log:
                log_name = date +'_'+ urlparse.urlparse(url_crawl).netloc + '.log'
                try:
                    log_file = open(log_name,'w')
                except OSError, error:
                    if 'Existe el fichero' in error:
                        pass
                    else:
                        log=False

            starttime=time.time()
            
            # metodo crawl
            [links_crawled, externals_url, files] = claseCrawl.crawl(url_crawl, output_file, limit_crawl, log, log_file)
            
            # metodo indexados
            [directorios,indexados] = claseCrawl.search_directorios(links_crawled, output_file)
            
            # metodo para buscar ficheros
            claseCrawl.search_ficheros(files, output_file)
            
            # metodo para obtener los enlaces externos
            claseCrawl.get_external_links(url_crawl, externals_url, output_file)
            
            # metodo para descargar archivos
            if download_flag:
                claseCrawl.download_archivos(extensions,files,output_file)

            # metodo para escanear puertos    
            if port_flag:	
		if ports_scan.find("-") == -1 and ports_scan.find(",") == -1:
		    ports_scan += "-"+ports_scan
		
		claseCrawl.printout('\nPORT\tSTATUS\tSERVICE',output_file)
		if (ports_scan.find('-')>=0):
		    ports_scan = ports_scan.split('-')		        	    
		    for port in range(int(ports_scan[0]), int(ports_scan[1])+1):
			t= Process(target=claseCrawl.PortScanner, args=(socket.gethostbyname(urlparse.urlparse(url_crawl).netloc), port, servs))
			t.start()
			t.join()

		elif (ports_scan.find(',')>=0):
		    ports_scan = ports_scan.split(',')
		    for port in ports_scan:
			t= Process(target=claseCrawl.PortScanner, args=(socket.gethostbyname(urlparse.urlparse(url_crawl).netloc), port, servs))
			t.start()
			t.join()
  
            claseCrawl.printout('',output_file)
            claseCrawl.printout(' hora de finalizacion: '+str(datetime.datetime.today()).rpartition('.')[0],output_file)

            endtime=time.time()
            

            try:
                output_file.close()
            except:
                pass
            try:
                log_file.close()
            except:
                pass

        else:
            print
            print ' Compruebe la dirección URL, debe ser: http://www.google.com o http://ejemplo.com'
            print
            claseCrawl.uso()
            
    # si pulsamos CTRL-C producimos una interrupcion de teclado
    except KeyboardInterrupt:
        print 'interrupcion de teclado. Salimos.'
        sys.exit(1)
    except Exception as inst:
        print ' Excepcion en el main'
        sys.exit(1)
