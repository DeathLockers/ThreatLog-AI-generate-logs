# ThreatLog-AI-generate-logs

Pequeña aplicacion para generar logs de un servidor ficticio y enviarlo al AWS.

Consiste en una pequeña aplicación utilizando Python que sea capaz de generar logs ficticios de Outlook cada cierto tiempo y que los envíe directamente y de forma automatizada por AWS S3 para tenerlo almacenado

## Entorno de desarrollo

Prepara el entorno virtual local para instalar los paquetes necesarios

```pyhon -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
```
