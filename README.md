# Redes

## Ejemplos de uso

### Start Server
```
python3 start-server.py -H 127.0.0.1 -p 3500 -s lib/server/
```

donde:
-s: path donde guarda el archivo en caso de upload.
### Upload

```
python3 upload.py -H 127.0.0.1 -p 3500 -s prueba.txt -n pruebaII.txt
```

donde:
-s: nombre del archivo de origen. (TODO: debería ser un path al archivo, ó un path absoluto)
-n: nombre del archivo como se sube al servidor.

### Download

```
python3 download.py -H 127.0.0.1 -p 3500 -d prueba.txt -n pruebaII.txt
```

donde:
-d: nombre del archivo de destino. (TODO: debería ser un path relativo al archivo, ó un path absoluto)
-n: nombre del archivo a descargar.