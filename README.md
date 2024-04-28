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
python3 upload.py -H 127.0.0.1 -p 3500 -s lib/client/prueba_a_subir.txt -n prueba_subida.txt
```

donde:
-s: nombre del archivo de origen.
-n: nombre del archivo como se sube al servidor.

### Download

```
python3 download.py -H 127.0.0.1 -p 3500 -d lib/client/pruebaII_descargada.txt -n pruebaII_del_servidor.txt
```

donde:
-d: path(incluyendo nombre) del destino del archivo.
-n: nombre del archivo a descargar.