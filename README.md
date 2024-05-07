# Redes

## Instalación

## Ejemplos de Uso

## Pruebas con pérdida de paquetes - Mininet

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
python3 download.py -H 10.0.0.1 -p 12000 -s archivo1mbDown.bin -n archivo1mb.bin -sw -v
```

4. Chequeo entre archivos: 
```
md5sum lib/server/files/archivo1mb.bin lib/client/files/archivo1mbDown.bin
```

## Para correr plugin wireshark

1. Instalar la versión del lenguaje [lua](https://www.lua.org/download.html) que sea compatible con tu versión de wireshark. [ver](https://www.wireshark.org/docs/wsdg_html_chunked/wsluarm.html)


2. Ubicarse en el directorio donde está ubicado el <dissector>.lua y abrir wireshark con el comando:

```
wireshark -X lua_script:dissector.lua
```

3. Elegimos capturar mensajes con 'any' y filtramos wireshark por el protocolo: en nuestro caso, `rdt_protocol_g_09`

4. Enviamos paquetes a través de nuestro protocolo (ver sección Ejemplos de uso).

5. Listo!
