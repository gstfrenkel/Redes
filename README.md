# Redes

## Instalación

## Ejemplos de Uso

## Topología Mininet

'sudo python3 topology.py': Ejecuta mininet con la topologìa creada por nosotros.

'link s1 h1 up': Establece la conexión entre el switch y el host y la pone en estado activo.

's1 tc qdisc add dev s1-eth2 root netem loss 10%' : Establece perdida de paquetes del 10% para el switch s1 salida eth2.

's1 tc qdisc del dev s1-eth2 root netem loss 10%': Elimina la regla establecida para la pèrdida de paquetes.

'xterm h1': Abre una ventana de terminal gráfica para el host h1.

## Para correr plugin wireshark

1. Ubicarse en el directorio donde está ubicado el <dissector>.lua y abrir wireshark con el comando:

```
wireshark -X lua_script:dissector.lua
```

2. filtramos wireshark por el protocolo: en nuestro caso, `rdt_protocol_g_09`

3. Enviamos paquetes a través de nuestro protocolo (ver sección Ejemplos de uso).

4. Listo!