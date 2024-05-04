# Redes

## Instalación

## Ejemplos de Uso

## Para correr plugin wireshark

1. Instalar la versión del lenguaje [lua](https://www.lua.org/download.html) que sea compatible con tu versión de wireshark. [ver](https://www.wireshark.org/docs/wsdg_html_chunked/wsluarm.html)


2. Ubicarse en el directorio donde está ubicado el <dissector>.lua y abrir wireshark con el comando:

```
wireshark -X lua_script:dissector.lua
```

3. Elegimos capturar mensajes con 'any' y filtramos wireshark por el protocolo: en nuestro caso, `rdt_protocol_g_09`

4. Enviamos paquetes a través de nuestro protocolo (ver sección Ejemplos de uso).

5. Listo!
