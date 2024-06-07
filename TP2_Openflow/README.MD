# Paso a paso para levantar la topología con el controller POX

1. Comando para levantar un controller con POX

```
./pox/pox.py --verbose forwarding.l2_learning
```

2. Comando para levantar mininet con la topología requerida

```
sudo mn --custom topology.py --topo customTopo,switches_number=4 --mac --switch ovsk --controller=remote
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