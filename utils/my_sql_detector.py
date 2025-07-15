import socket
import time
import getpass
import json
import os

HISTORIAL_FILE = os.path.expanduser("~/.historial_sql_instances.json")

def get_available_sql_servers(timeout=5):
    """
    Escanea la red por broadcast UDP para descubrir instancias SQL Server.
    Devuelve una lista de strings con formato IP\INSTANCIA o IP si no tiene nombre.
    """
    message = b'\x02'
    broadcast_address = ('255.255.255.255', 1434)
    responses = []

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)

    try:
        sock.sendto(message, broadcast_address)
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                data, addr = sock.recvfrom(4096)
                response = data.decode(errors='ignore')
                responses.append((addr[0], response))
            except socket.timeout:
                break
    finally:
        sock.close()

    instances = []
    for ip, resp in responses:
        fields = resp.split(";")
        data = dict(zip(fields[::2], fields[1::2]))
        server = data.get("ServerName", "")
        instance = data.get("InstanceName", "")
        if instance and instance.upper() != "MSSQLSERVER":
            instances.append(f"{ip}\\{instance}")
        else:
            instances.append(ip)

    # Guardar en historial
    save_to_history(instances)

    return instances

def get_default_username():
    """
    Retorna el nombre de usuario actual del sistema.
    """
    return getpass.getuser()

def save_to_history(instances):
    """
    Guarda las instancias detectadas en un historial persistente.
    """
    historial = load_history()
    for inst in instances:
        if inst not in historial:
            historial.append(inst)
    with open(HISTORIAL_FILE, "w") as f:
        json.dump(historial, f, indent=4)

def load_history():
    """
    Carga el historial de instancias SQL detectadas.
    """
    if not os.path.exists(HISTORIAL_FILE):
        return []
    with open(HISTORIAL_FILE, "r") as f:
        return json.load(f)

def seleccionar_instancia():
    """
    Permite al usuario seleccionar una instancia del historial.
    """
    historial = load_history()
    if not historial:
        print("No hay historial de instancias guardadas.")
        return None

    print("\nHistorial de instancias SQL disponibles:")
    for idx, inst in enumerate(historial, 1):
        print(f"{idx}. {inst}")

    opcion = input("Seleccione una instancia por número: ")
    try:
        idx = int(opcion) - 1
        if 0 <= idx < len(historial):
            return historial[idx]
        else:
            print("Opción inválida.")
            return None
    except ValueError:
        print("Entrada inválida.")
        return None
