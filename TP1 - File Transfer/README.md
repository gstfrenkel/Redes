# Introducción

Este trabajo práctico tiene como objetivo crear una aplicación de red para transferir archivos entre cliente y servidor. Se implementarán dos operaciones fundamentales: UPLOAD (enviar archivos del cliente al servidor) y DOWNLOAD (descargar archivos del servidor al cliente). Se tendrán en cuenta los protocolos TCP y UDP para la comunicación. TCP ofrece un servicio confiable orientado a la conexión, mientras que UDP es sin conexión y menos confiable. Se implementarán versiones de UDP con protocolo Stop & Wait y Go-Back-N con el objetivo de lograr una transferencia confiable al utilizar el protocolo..

# Hipótesis y suposiciones realizadas


# Implementación


# Pruebas


# Análisis


# Preguntas a responder

> _Describa la arquitectura Cliente-Servidor._


En la arquitectura cliente-servidor, un host permanece siempre activo como servidor para atender las solicitudes de otros hosts, denominados clientes. Los clientes no pueden comunicarse directamente entre sí. Para que un cliente se comunique con el servidor, este último posee una dirección fija y conocida llamada dirección IP. Sin embargo, el servidor no tiene previamente conocimiento de las direcciones de los clientes.

> _¿Cuál es la función de un protocolo de capa de aplicación?_


Un protocolo de capa de aplicación establece cómo se comunican los procesos de aplicaciones que se ejecutan en diferentes sistemas finales. Esto implica definir:

- Tipos de mensaje: Los mensajes pueden ser de solicitud o de respuesta. Las solicitudes son enviadas por el cliente al servidor para solicitar algún servicio o información, mientras que las respuestas son enviadas por el servidor al cliente en respuesta a una solicitud.
- Campos de mensaje y su significado: Cada tipo de mensaje tiene campos específicos que contienen información relevante para la comunicación. El significado de cada campo se establece en la especificación del protocolo y puede variar según el contexto de la aplicación.
- Reglas para enviar y responder mensajes: El protocolo define reglas para determinar cuándo y cómo un proceso envía y responde mensajes. Esto incluye aspectos como el establecimiento de conexiones, el formato de los mensajes, el manejo de errores y el cierre de la comunicación.

> _Detalle el protocolo de aplicación desarrollado en este trabajo._


> _La capa de transporte del stack TCP/IP ofrece dos protocolos: TCP y UDP. ¿Qué servicios proveen dichos protocolos? ¿Cuáles son sus características? ¿Cuándo es apropiado utilizar cada uno?_

La capa de transporte en el stack TCP/IP tiene como objetivo principal proporcionar un servicio de entrega confiable de datos de la capa de red a la capa de aplicación. En este contexto, se encuentran dos protocolos principales: UDP (User Datagram Protocol) y TCP (Transmission Control Protocol), cada uno con sus características y servicios específicos.

### TCP: Transmission Control Protocol

#### Características

- Proporciona una entrega de paquetes confiable sin pérdida ni duplicados.
- Es un servicio orientado a la conexión para las aplicaciones que lo utilizan.
- Tiene una estructura de encabezado más compleja que UDP.

#### Servicios

- EOfrece entrega de datos de proceso a proceso.
- Implementa un protocolo de transferencia de datos confiable (RDT) que incluye chequeo de errores e integridad, garantía de entrega, y orden de entrega asegurado.
- Realiza control de congestión para mejorar el rendimiento de la red.

### UDP: User Datagram Protocol

#### Características

- Puede haber pérdida de paquetes y posibilidad de duplicados.
- No requiere establecer una conexión previa.
- Tiene una estructura de encabezado simple.

#### Servicios

- Ofrece la entrega de datos de proceso a proceso.
- Realiza un chequeo de errores e integridad utilizando un campo de detección de errores (checksum) en los encabezados.


UDP se prefiere en casos donde la velocidad de entrega es prioritaria sobre la confiabilidad de los datos. Esto se observa en aplicaciones como streaming multimedia, telefonía por internet y juegos en línea, donde la inmediatez es esencial y la pérdida ocasional de paquetes no afecta significativamente la experiencia del usuario.

En cambio, TCP se utiliza en escenarios donde la confiabilidad de la entrega es crucial. Aplicaciones como el correo electrónico, la web y la transferencia de archivos requieren una garantía de que los datos llegarán correctamente y en el orden adecuado, TCP es la elección preferida.

# Dificultades encontradas


# Conclusión

