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

# Como instalar Openvswitch

- Descargar el paquete comprimido
- Ejecutar el `./boot.sh`

	Puede que necesite descargar unas dependencias. Yo tuve que instalar:
	- `sudo apt-get install autoconf`
	- `sudo apt-get install libtool libtool-bin`
- Ejecutar el `./configure`
- Hacer un make