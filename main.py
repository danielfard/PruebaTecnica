from typing import List, Dict, Tuple
import requests
from collections import Counter
from datetime import datetime
from config import ConfigLoader
from concurrent.futures import ThreadPoolExecutor

config = ConfigLoader()

API_URL = f"https://api.lumu.io/collectors/{config.COLLECTOR_ID}/dns/queries?key={config.LUMU_CLIENT_KEY}"

def parse_log_file(file_path: str) -> List[Dict[str, str]]:
    """
    Lee y analiza un archivo de log de DNS y extrae la información relevante de las consultas DNS.

    Args:
        file_path (str): Ruta al archivo de log que será procesado.

    Returns:
        List[Dict[str, str]]: Una lista de diccionarios, cada uno conteniendo los detalles 
                               de una consulta DNS, con claves como 'timestamp', 'name', 
                               'client_ip', 'client_name', y 'type'.
    """
    dns_queries = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Divide la línea en partes usando el espacio como delimitador
                parts = line.split()
                # Asegúrate de que la línea tenga suficientes partes para extraer los datos
                if len(parts) < 13:
                    continue
                try:
                    # Convierte la fecha y hora a formato ISO 8601
                    timestamp = datetime.strptime(f"{parts[0]} {parts[1]}", '%d-%b-%Y %H:%M:%S.%f').isoformat() + 'Z'
                    # Extrae la IP del cliente sin el puerto
                    client_ip = parts[6].partition("#")[0]
                    # Extrae el nombre de la consulta y el nombre del cliente
                    name = parts[9]
                    client_name = parts[5]
                    # Extrae el tipo de consulta DNS
                    query_type = parts[11]
                    # Agrega el registro procesado a la lista
                    dns_queries.append({
                        "timestamp": timestamp,
                        "name": name,
                        "client_ip": client_ip,
                        "client_name": client_name,
                        "type": query_type
                    })
                except (ValueError, IndexError) as e:
                    print(f"Skipping line due to error: {e}")
    except (FileNotFoundError, IOError) as e:
        print(f"File error: {e}")
    return dns_queries

def send_data_to_lumu(data: List[Dict[str, str]], chunk_size: int = 500) -> None:
    """
    Envía los datos de consultas DNS a la API de Lumu en trozos (chunks) de tamaño máximo definido.

    Args:
        data (List[Dict[str, str]]): Lista de registros de consultas DNS a enviar, cada uno representado como un diccionario.
        chunk_size (int): Tamaño máximo de cada trozo de datos que se enviará a la API.

    Returns:
        None
    """
    def post_chunk(chunk):
        """
        Envía un solo trozo de datos a la API de Lumu y maneja errores.

        Args:
            chunk (List[Dict[str, str]]): Un trozo de datos para ser enviado.

        Returns:
            str: Mensaje de estado sobre el envío del trozo.
        """
        try:
            response = requests.post(API_URL, json=chunk)
            response.raise_for_status()
            return f"Chunk sent successfully."
        except requests.RequestException as e:
            return f"Error sending chunk: {e}"

    # Usar ThreadPoolExecutor para enviar los trozos en paralelo y acelerar el proceso
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Divide los datos en trozos (chunks) de tamaño definido
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
        # Enviar los trozos en paralelo y manejar los resultados
        executor.map(post_chunk, chunks)

def calculate_statistics(dns_queries: List[Dict[str, str]]) -> Tuple[int, List[Tuple[str, int, float]], List[Tuple[str, int, float]]]:
    """
    Calcula estadísticas a partir de los registros de consultas DNS procesados, como el número total de registros
    y las 5 principales direcciones IP de clientes y los 5 principales hosts consultados.

    Args:
        dns_queries (List[Dict[str, str]]): Lista de registros de consultas DNS.

    Returns:
        Tuple[int, List[Tuple[str, int, float]], List[Tuple[str, int, float]]]: Un tupla con tres elementos:
            - total_records (int): Número total de registros procesados.
            - client_ip_rank (List[Tuple[str, int, float]]): Las 5 direcciones IP de clientes más frecuentes, con su 
              cantidad y porcentaje respecto al total de registros.
            - host_rank (List[Tuple[str, int, float]]): Los 5 hosts más consultados, con su cantidad y porcentaje.
    """
    total_records = len(dns_queries)
    # Contamos las ocurrencias de las direcciones IP de los clientes y de los hosts consultados
    client_ip_counts = Counter(query["client_ip"] for query in dns_queries)
    host_counts = Counter(query["name"] for query in dns_queries)

    # Seleccionamos las 5 direcciones IP y hosts más frecuentes junto con su porcentaje
    client_ip_rank = [(ip, count, (count / total_records) * 100) for ip, count in client_ip_counts.most_common(5)]
    host_rank = [(host, count, (count / total_records) * 100) for host, count in host_counts.most_common(5)]

    return total_records, client_ip_rank, host_rank

def print_statistics(total_records: int, client_ip_rank: List[Tuple[str, int, float]], host_rank: List[Tuple[str, int, float]]) -> None:
    """
    Imprime las estadísticas de las consultas DNS de manera estructurada.

    Args:
        total_records (int): Número total de registros procesados.
        client_ip_rank (List[Tuple[str, int, float]]): Las 5 direcciones IP de clientes más frecuentes.
        host_rank (List[Tuple[str, int, float]]): Los 5 hosts más consultados.

    Returns:
        None
    """
    print(f"Total Records: {total_records}\n")
    print("Client IPs Rank")
    print("-" * 40)
    print(f"{'Client IP':<20} {'Count':<10} {'Percentage'}")
    for ip, count, percentage in client_ip_rank:
        print(f"{ip:<20} {count:<10} {percentage:.2f}%")
    print("\nHost Rank")
    print("-" * 40)
    print(f"{'Host':<30} {'Count':<10} {'Percentage'}")
    for host, count, percentage in host_rank:
        print(f"{host:<30} {count:<10} {percentage:.2f}%")

def main(file_path: str):
    """
    Función principal que coordina el flujo de ejecución del análisis de consultas DNS.

    Args:
        file_path (str): Ruta al archivo de log con las consultas DNS.

    Returns:
        None
    """
    dns_queries = parse_log_file(file_path)
    send_data_to_lumu(dns_queries)  # Descomentarlo para enviar los datos a Lumu
    total_records, client_ip_rank, host_rank = calculate_statistics(dns_queries)
    print_statistics(total_records, client_ip_rank, host_rank)

if __name__ == "__main__":
    main("queries")
