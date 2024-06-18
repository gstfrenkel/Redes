# Paso a paso para levantar la topología con el controller POX

1. Comando para levantar un controller con POX

```
python3 pox.py --verbose openflow.of_01 samples.pretty_log forwarding.l2_learning firewall
```

2. Comando para levantar mininet con la topología requerida

```
sudo mn --custom topology.py --topo customTopo,switches_number=4 --mac --switch ovsk --controller remote,port=6633
```

### Comentario
Si no tenemos instalado el `ovsk` se puede construir la topologia con `--switch ovsbr`

## Como instalar Openvswitch

- Descargar el paquete comprimido
- Ejecutar el `./boot.sh`

	Puede que necesite descargar unas dependencias. Yo tuve que instalar:
	- `sudo apt-get install autoconf`
	- `sudo apt-get install libtool libtool-bin`
- Ejecutar el `./configure`
- Hacer un make

## Requisitos de instalación

- Python version 3.7|3.8|3.9
- Tener instalado mininet.
- Tener instalado Openvswitch.

## Levantar servidor pox sobre OpenFlow

1. Dar permisos de ejecución al script `run_server.sh`:

```
chmod +x run_server.sh
```

2. Ejecutar con:

```
./run_firewall.sh
```

## Levantar topología con switchs variable

1. Dar permisos de ejecución al script `run_topo.sh`:

```
chmod +x run_topo.sh
```

2. Ejecutar con:

```
./run_topo.sh <cantidad de switches>
```

## Ejecutar pruebas con iperf

### Para levantar un servidor

Una vez abierta la terminal sobre el host que queremos levantar el servidor ejecutamos:

```
iperf -s -p <puerto> -u
```

### Para generar un cliente y enviar mensajes 

Para levantar un cliente, simplemente dentro de la terminal del host cliente ejecutamos:

```
iperf -c <ip_srv> -p <puerto_srv> -u 
```

**Nota**: 
El flag `-u` es para indicar que queremos usar el protocolo UDP. Se puede quitar el flag y eso provocará que el protocolo usado sea TCP.