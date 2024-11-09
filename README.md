# Análisis de Consultas DNS

Este proyecto analiza un archivo de logs de consultas DNS, extrae información relevante y calcula estadísticas sobre las consultas. Además, permite enviar los datos a la API de Lumu en trozos (chunks) utilizando hilos para un procesamiento paralelo eficiente.

**Nota:** El archivo `.env` no debería estar en GitHub por razones de seguridad, ya que contiene claves sensibles. Sin embargo, se ha subido en este caso solo con fines de prueba técnica. Se recomienda gestionar las claves de API de manera segura, utilizando métodos como variables de entorno o un archivo `.env` que no se suba al repositorio.


## Requisitos

Antes de ejecutar este proyecto, asegúrate de tener los siguientes requisitos:

- Python 3.6 o superior
- Claves de la API de Lumu (`LUMU_CLIENT_KEY`, `COLLECTOR_ID`)

## Instalación

1. **Clona este repositorio**:

   ```bash
   git clone https://github.com/tu-usuario/tu-repositorio.git
   cd tu-repositorio

2. **Crea y activa un entorno virtual (opcional pero recomendado)**:

   ```bash 
   python -m venv env
   .\env\Scripts\activate

3. **Crea y activa un entorno virtual (opcional pero recomendado)**:

   ```bash
    pip install -r requirements.txt

## Estructura del Proyecto

.

├── config.py           # Configuración de las claves de la API

├── queries             # Archivo de logs de consultas DNS

├── main.py             # Script principal para procesar los logs

├── requirements.txt    # Lista de dependencias

├── README.md           # Este archivo

##  Descripción del Código

### ```main.py```
```parse_log_file(file_path):``` Lee y analiza el archivo de logs de DNS, extrayendo la información relevante.

```send_data_to_lumu(data, chunk_size):``` Envía los datos procesados a la API de Lumu en trozos, usando procesamiento paralelo para mayor eficiencia.

```calculate_statistics(dns_queries):``` Calcula las estadísticas del número total de registros, las 5 principales direcciones IP de clientes y los 5 principales hosts consultados.

```print_statistics(total_records, client_ip_rank, host_rank):``` Imprime las estadísticas de manera estructurada en la consola.
config.py
Este archivo contiene las claves de configuración necesarias para interactuar con la API de Lumu. Asegúrate de añadir tu LUMU_CLIENT_KEY y COLLECTOR_ID.

### ```config.py```
Este archivo contiene las claves de configuración necesarias para interactuar con la API de Lumu. Asegúrate de añadir tu LUMU_CLIENT_KEY y COLLECTOR_ID.