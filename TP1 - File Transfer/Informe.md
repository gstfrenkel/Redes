# Introducción

Este trabajo práctico tiene como objetivo crear una aplicación de transferencia de archivos entre un servidor y sus clientes de forma tal que se soporten las siguientes operaciones: 
- UPLOAD: enviar archivos del cliente al servidor.
- DOWNLOAD: descargar archivos del servidor al cliente.

Dicha transferencia es implementada sobre el protocolo de transporte UDP y debe ser confiable, es decir, soportar pérdida de paquetes en la transferencia. Con el fin de lograr esto es que se implementan dos protocolos de la capa de transporte: Stop & Wait y Selective Repeat.

# Implementación

### Mensajes

Cada mensaje de los protocolos implementados cuenta con un header y un payload. El header contiene un **type** el cual ocupa un byte y que refiere al tipo de mensaje que se está enviando o recibiendo. Los tipos soportados son:
- UPLOAD_TYPE_SW: subir archivo utilizando protocolo Stop & Wait.
- UPLOAD_TYPE_SR: subir archivo utilizando protocolo Selective Repeat.
- DOWNLOAD_TYPE_SW: : descargar archivo utilizando protocolo Stop & Wait.
- DOWNLOAD_TYPE_SR: descargar archivo utilizando protocolo Selective Repeat.
- DATA_TYPE: envío de chunk del archivo.
- LAST_DATA_TYPE: envío del último chunk del archivo.
- ACK_TYPE: confirmación del recibo de un chunk.
- END_TYPE: pedido de desconexión.

A su vez, el header contiene el campo de **seq_num** el cual ocupa cuatro bytes y que se utiliza para poder tener un orden entre los paquetes que se envían y se reciben. Por último, el payload puede contener chunks del archivo a subir/descargar (para el caso de DATA_TYPE o LAST_DATA_TYPE), o bien el nombre de la ruta o archivo que se busca subir/descargar (para el caso de UPLOAD_TYPE_SW, UPLOAD_TYPE_SR, DOWNLOAD_TYPE_SW, DOWNLOAD_TYPE_SR).

### Handshake

Tanto como para subir archivos como para descargalos, el cliente establece una conexión con el servidor utilizando un socket y la dirección IP y puerto proporcionados como parámetros del programa. Mediante este socket es que se envía al servidor un pedido de conexión. Es en este mismo mensaje y mediante el payload que se le comunica al servidor el nombre con el cual el archivo debe ser subido, o el nombre del archivo a descargar.

El servidor al recibir este pedido crea un thread de ejecución el cual abre su propio socket con el cliente y envía un mensaje en respuesta. En caso de no recibir este mensaje, el cliente volverá a intentar establecer una conexión con el servidor, y el thread recién mencionado será finalizado por el servidor. En caso de sí recibir el mensaje, el cliente de ese momento en adelante se comunicará con el thread, dejando disponible al servidor para recibir nuevos pedidos, permitiendo así manejar múltiples clientes de forma concurrente.

Una vez terminada la subida/descarga del archivo deseado, el cliente envía un aviso de desconexión al servidor y se espera por la confirmación por parte de este. En caso de no recibirla, el cliente se desconecta sin la certeza de si el servidor recibió el aviso pero con la certeza de haber completado la transferencia del archivo.

### Cliente
###### Upload:

El comando `upload` envía un archivo al servidor para ser guardado con el nombre asignado.

`python3 upload.py [-h] [-v | -q] [-H ADDR] [-p PORT] [-s FILEPATH] [-n FILENAME] [-sw | -sr]`

Donde cada flag indica:

- `-h, --help`: Imprime el mensaje de "help"
- `-v, --verbose`: Incrementa en uno la verbosidad en cuanto al sistema de logueo del servidor.
- `-q, --quiet`: Decrementa en uno la verbosidad en cuanto al sistema de logueo.
- `-H, --host`: Indica la dirección IP del servicio.
- `p, --port`: Indica el puerto.
- `-s, --src`: Indica el path del archivo a subir.
- `-n, --name`: Nombre del archivo a subir.
- `-sw`: Ejecuta el comando utilizando el protocolo de Stop & Wait.
- `-sr`: Ejecuta el comando utilizando el protocolo de Selective Repeat.

En el caso del upload, el mensaje que el servidor responde al pedido de conexión es una confirmación, o ACK, de forma que se le informa al cliente que se puede iniciar la subida inmediatamente. Una vez que el cliente recibe el ACK del último paquete (en Stop & Wait) o que recibe todos los ACK pendientes tras haber enviado el último paquete (en Selective Repeat), se envía el pedido de desconexión.

###### Download:

El comando `download` descarga un archivo especificado desde el servidor.

`python3 download.py [-h] [-v | -q] [-H ADDR] [-p PORT] [-d FILEPATH] [-n FILENAME] [-sw | -sr] `

Donde todos los flags indican lo mismo que con el comando anterior, con la diferencia de `-d` que indica el path de destino del archivo a descargar. Además, el flag `-n` indica cuál es el nombre del archivo a descargar del servidor.

En el caso del upload, el mensaje que el servidor responde al pedido de conexión no es una confirmación, o ACK, sino que es el primer chunk de información del archivo a descargar de forma que en un solo mensaje se le indica al cliente que la conexión fue exitosa y que puede iniciar la descargar inmediatamente. Una vez que el cliente recibe el último paquete de data (en Stop & Wait) o que recibe todos los paquetes de data pendientes para escribir en disco el último (en Selective Repeat), se envía el pedido de desconexión.

### Servidor

El servidor debe estar preparado para recibir un mensaje que indica que comienza una nueva conexión, es decir que tiene que estar ejecutándose como proceso antes de que el cliente trate de iniciar el contacto. Es por eso, que el primer comando a ejecutar es el `start-server`.

`start-server.py [-h] [-v | -q] [-H ADDR] [-p PORT] [-s DIRPATH]`

Donde los flags indican:

- `-h/--help`: Imprime el mensaje de "help"
- `-v/--verbose`: Incrementa en uno la verbosidad en cuanto al sistema de logueo del servidor
- `-q/--quiet`: Decrementa en uno la verbosidad en cuanto al sistema de logueo.
- `-H/--host`: Indica la dirección IP del servicio
- `-p/--port`: Indica el puerto
- `-s/--storage`: El path en el que se almacenan los archivos.

Al iniciar el servidor, este crea un socket y espera por pedidos de conexión entrantes. Para cada pedido, inicia un thread el cual se encarga de manejar la transferencia de información con el cliente pertinente. De esta forma se logra un procesamiento simple en el que el servidor actúa como "recepcionista" indicándole a los clientes con qué thread se deben comunicar, logrando así la posibilidad de manejar múltiples clientes de forma concurrente.

###### Upload

En caso de no ser posible subir el archivo pedido (ej ruta inválida), se le informa al cliente mediante un mensaje de error para que rectifique el pedido. En cualquier otro caso, la respuesta del thread ante el pedido de subida es un ACK. En Stop & Wait, el servidor reenvía ACKs en tanto y cuanto el cliente no haya respondido con un paquete con nuevos chunks a subir o bien un pedido de desconexión, mientras que en Selective Repeat, cada mensaje de data es respondido con un ACK independientemente de si ya había sido enviado o no.

###### Download

En caso de no ser posible descargar el archivo pedido (ej ruta inválida), se le informa al cliente mediante un mensaje de error para que rectifique el pedido. En cualquier otro caso, la respuesta del thread ante el pedido de subida es un ACK. En Stop & Wait, el servidor reenvía paquetes de data en tanto y cuanto el cliente no haya respondido con un ACK o bien un pedido de desconexión, mientras que en Selective Repeat, el servidor envía tantos paquetes de data como permita la ventana, reenviando aquellos que no hayan sido confirmados por el cliente mediante un ACK pasado el timeout definido.

### Stop & Wait

A continuación, se explica el funcionamiento del protocolo Stop & Wait implementado, tomando como caso la subida de un archivo (la descarga es la operación inversa con las excepciones anteriormente mencionadas).

Tras establecida la conexión, el cliente envía paquetes con chunks de información del archivo a subir, esperando entre cada uno a recibir el ACK correspondiente con el sequence number del paquete enviado.

![1714709709843](image/Informe/1714709709843.png)

En caso de perderse un ACK del servidor, el cliente jamás obtendrá la confirmación del servidor, por lo que debe reenviar el paquete tantas veces como lo permita la constante de `MAX_TRIES`, o hasta recibir el ACK correspondiente. En este caso, el servidor guarda un registro de cuál fue el último paquete de data que recibió por lo que no vuelve a escribir el paquete recibido por duplicado.

En caso de que se pierda data, el cliente jamás obtendrá el ACK del servidor por lo que se reenvía el paquete de data. En este caso, el sequence number del nuevo paquete de data no coincidirá con el último recibido por el servidor, por lo que este escribirá la nueva información recibida en el archivo.

### Selective Repeat

A continuación, se explica el funcionamiento del protocolo Selective Repeat implementado, tomando como caso la subida de un archivo (la descarga es la operación inversa con las excepciones anteriormente mencionadas).

Tras establecida la conexión, el cliente inicia dos threads adicionales de forma que se utilizan tres threads en total. El primero (y el principal) se encarga de enviar paquetes de información, mover la ventana, guardar registro de los paquetes enviados y recibidos y procesar requests o pedidos de los otros threads. El segundo se encarga de recibir ACKs de parte del servidor e informarle al thread principal de los sequence number que llegaron exitosamente al servidor. Por último, el tercer thread se encarga de mantener un hashmap de los paquetes enviados con el timestamp en el que fueron enviados, con el fin de identificar aquellos que hayan entrado en timeout, e informa al thread principal sobre cuáles paquetes debe reenviar.

La comunicación de los dos threads secundarios con el principal se realiza a través de colas de mensajes, de forma que no son necesarios locks entre threads. Los mensajes que se comunican son:
- El thread principal le comunica al thread de timeouts el sequence number del paquete enviado y el timestamp en el que fue enviado.
- El thread de ACKs le comunica al thread principal sobre los sequence numbers de los paquetes que han llegado al servidor exitosamente. Cada vez que el thread prinicipal toma consciencia de que un nuevo paquete llegó a destino, le comunica al thread de timeouts que puede dejar de trackear dicho sequence number.
- El thread de timeouts le comunica al thread principal que un paquete entró en timeout y que lo debe reenviar.

Una vez iniciados los threads, el thread principal envía tantos paquetes con chunks de información como permita la ventana, informando de los timestamps y recibiendo información de los paquetes que llegaron y que entraron en timeout de forma concurrente. Cuando se recibe el ACK del primer paquete de la ventana, esta se actualiza en función de todos los paquetes que se hayan recibido. Por ejemplo, si se recibió el ACK del segundo paquete de la ventana y luego del primero, la ventana se puede mover dos lugares. En caso de que no se haya recibido el segundo pero sí el primero, tercero, cuarto, quinto, etc, solo se puede mover un lugar ya que la ventana debe esperar a ese segundo ACK para poder moverla.

![1714709716588](image/Informe/1714709716588.png)

![1714709950584](image/Informe/1714709950584.png)

![1714709999321](image/Informe/1714709999321.png)

![1714710022980](image/Informe/1714710022980.png)

---

# Pruebas

## Mininet

Para este trabajo utilizamos una topología de 1 switch y 3 host, donde 1 de ellos actúa como servidor y cada host está linkeado con el switch.

1. Tener instalado mininet. [ver](https://mininet.org/download/)

2. Ejecutar el siguiente comando para establecer la topología anteriomente mencionada:

```
sudo mn --topo linear,1,4
```

3. Establecemos la pérdida de paquetes en todos los host. En este caso h1, h2 y h3:

- Si se quiere establecer pérdida de paquete en el switch:

```
s1 tc qdisc add dev s1-eth1 root netem loss 10%
```

- Si se quiere establecer pérdida de paquete en el host:

```
h1s1 tc qdisc add dev h1s1-eth0 root netem loss 10%
```

**Nota**: análogamente ejecutamos el comando para eth2 y eth3.

4. abrimos las terminales para c/u de los host, incluyendo el servidor:

```
xterm h1
```
**Nota**: análogamente abrimos terminales para h2 y h3.

5. Levantamos el servidor y probamos los comandos upload u download.

## Para correr server y cliente:

1. Ejecucion server:
```
python3 start-server.py -H 10.0.0.1 -p 12000 -s ./ -v
```

2. Ejecución cliente upload: 
```
python3 upload.py -H 10.0.0.1 -p 12000 -s archivo1mb.bin -n archivo1mbUP.bin -sw -v

```

3. Ejecución cliente download:
```
python3 download.py -H 10.0.0.1 -p 12000 -d archivo1mbDown.bin -n archivo1mb.bin -sw -v
```

4. Chequeo entre archivos: 
```
md5sum lib/server/files/archivo1mb.bin lib/client/files/archivo1mbDown.bin
```

## Wireshark

Para constatar que los mensajes de los protocolos desarrollados se coinciden con lo descripto en el presente informe, se pueden capturar paquetes con Wireshark para lo cual fue desarrollado un plugin `dissector.lua` que parsea el payload de los paquetes UDP con el formato de los mensajes de los protocolos implementados.

1. Instalar la versión del lenguaje [lua](https://www.lua.org/download.html) que sea compatible con tu versión de wireshark. [ver](https://www.wireshark.org/docs/wsdg_html_chunked/wsluarm.html)

2. Ubicarse en el directorio donde está ubicado el <dissector>.lua y abrir wireshark con el comando:

```
wireshark -X lua_script:dissector.lua
```

3. Empezar a capturar mensajes en la IP elegida y filtrar por el protocolo `rdt_protocol_g_09`.

4. Iniciar la subida o descarga de un archivo.

# Análisis

A continuación se adjuntan las mediciones de tiempo realizadas para ambos protocolos teniendo en cuenta, distintos tamaños de archivos y diferentes porcentajes de pérdida de paquetes.

**Archivo 50KB**

| Packet Loss   | Selective Repeat | Stop and Wait |
|----------|------|--------|
| 0%     | 0.484   | 0.039 |
| 5%    | 0.641   | 0.354  |
| 10%   | 2.025   | 1.159 |
| 15%   | 2.396   | 3.790|

![arch_50kb](image/Informe/arch_50kb.png)

**Archivo 100KB**

| Packet Loss   | Selective Repeat | Stop and Wait |
|----------|------|--------|
| 0%     | 0.771   | 0.047 |
| 5%    | 3.687   | 2.922  |
| 10%   | 3.754   | 5.673 |
| 15%   | 4.457   | 7.032|

![arch_100kb](image/Informe/arch_100kb.png)

**Archivo 200KB**

| Packet Loss   | Selective Repeat | Stop and Wait |
|----------|------|--------|
| 0%     | 2.228   | 0.079 |
| 5%    | 4.614   | 3.724  |
| 10%   | 7.082   | 10.539 |
| 15%   | 7.559   | 14.635|

![arch_200kb](image/Informe/arch_200kb.png)


# Preguntas a responder

_**Describa la arquitectura Cliente-Servidor.**_

En la arquitectura cliente-servidor, un host permanece siempre activo como servidor para atender las solicitudes de otros hosts, denominados clientes. Los clientes no pueden comunicarse directamente entre sí. Para que un cliente se comunique con el servidor, este último posee una dirección fija y conocida llamada dirección IP. Sin embargo, el servidor no tiene previamente conocimiento de las direcciones de los clientes.

_**¿Cuál es la función de un protocolo de capa de aplicación?**_

Un protocolo de capa de aplicación establece cómo se comunican los procesos de aplicaciones que se ejecutan en diferentes sistemas finales. 

Esto implica definir:
   - **Tipos de mensaje**: Los mensajes pueden ser de solicitud o de respuesta. Las solicitudes son enviadas por el cliente al servidor para solicitar algún servicio o información, mientras que las respuestas son enviadas por el servidor al cliente en respuesta a una solicitud.
   - **Campos de mensaje y su significado**: Cada tipo de mensaje tiene campos específicos que contienen información relevante para la comunicación. El significado de cada campo se establece en la especificación del protocolo y puede variar según el contexto de la aplicación.
   - **Reglas para enviar y responder mensajes**: El protocolo define reglas para determinar cuándo y cómo un proceso envía y responde mensajes. Esto incluye aspectos como el establecimiento de conexiones, el formato de los mensajes, el manejo de errores y el cierre de la comunicación.

 _**Detalle el protocolo de aplicación desarrollado en este trabajo.**_

Se explicó en el item Implementación.

_**La capa de transporte del stack TCP/IP ofrece dos protocolos: TCP y UDP. ¿Qué servicios proveen dichos protocolos? ¿Cuáles son sus características? ¿Cuándo es apropiado utilizar cada uno?**_

La capa de transporte en el stack TCP/IP tiene como objetivo principal proporcionar un servicio de entrega confiable de datos de la capa de red a la capa de aplicación. En este contexto, se encuentran dos protocolos principales: UDP (User Datagram Protocol) y TCP (Transmission Control Protocol), cada uno con sus características y servicios específicos.

### TCP: Transmission Control Protocol

- Características

  - Proporciona una entrega de paquetes confiable sin pérdida ni duplicados.
  - Es un servicio orientado a la conexión para las aplicaciones que lo utilizan.
  - Tiene una estructura de encabezado más compleja que UDP.
- Servicios

  - EOfrece entrega de datos de proceso a proceso.
  - Implementa un protocolo de transferencia de datos confiable (RDT) que incluye chequeo de errores e integridad, garantía de entrega, y orden de entrega asegurado.
  - Realiza control de congestión para mejorar el rendimiento de la red.

### UDP: User Datagram Protocol

- Características

  - Puede haber pérdida de paquetes y posibilidad de duplicados.
  - No requiere establecer una conexión previa.
  - Tiene una estructura de encabezado simple.
- Servicios:

  - Ofrece la entrega de datos de proceso a proceso.
  - Realiza un chequeo de errores e integridad utilizando un campo de detección de errores (checksum) en los encabezados._

UDP se prefiere en casos donde la velocidad de entrega es prioritaria sobre la confiabilidad de los datos. Esto se observa en aplicaciones como streaming multimedia, telefonía por internet y juegos en línea, donde la inmediatez es esencial y la pérdida ocasional de paquetes no afecta significativamente la experiencia del usuario.

En cambio, TCP se utiliza en escenarios donde la confiabilidad de la entrega es crucial. Aplicaciones como el correo electrónico, la web y la transferencia de archivos requieren una garantía de que los datos llegarán correctamente y en el orden adecuado, TCP es la elección preferida.

# Dificultades encontradas

- Mantener consistencia en todos los protocolos para mantener separada la aplicación y la implementación de los protocolos.
- Realizar un correcto manejo de la pérdida de paquetes para ambos protocolos implementados.
- Definición los valores de los timeout, dado que dependiendo de los tamaños de archivo podían quedar cortos.
- Definir los campos necesarios en los mensajes con el fin de realizar una buena comunicación entre cliente y servidor.
- Concurrencia en Selective Repeat.

# Conclusión

El proyecto realizado fue una inmersión profunda en el desarrollo de dos protocolos de transporte para la transferencia de archivos a través del protocolo de transporte UDP, con extensiones para garantizar una comunicación confiable. Durante este trabajo práctico se presentaron diversos desafíos; desde la definición de los mensajes hasta el manejo de timeouts y la gestión de la pérdida de paquetes, entre otros aspectos cruciales de la comunicación cliente-servidor. En resumen, este proyecto permitió comprender en profundidad los desafíos asociados con la implementación de un protocolo de transporte y brindó una buena experiencia en el diseño y desarrollo de sistemas de comunicación confiables.
