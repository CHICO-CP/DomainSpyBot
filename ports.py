import subprocess
import sys

def scan_ports(domain):
    try:

        # Ejecuta el comando Nmap en el dominio o subdominio
        result = subprocess.run(['nmap', domain], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Verifica si hubo algún error
        if result.stderr:
            print(f"❌ Error al ejecutar nmap: {result.stderr}")
            return

        # Extrae los puertos abiertos de la salida de nmap
        open_ports = []
        for line in result.stdout.splitlines():
            if "/tcp" in line and "open" in line:
                open_ports.append(line.strip())

        # Formatea el resultado para imprimirlo
        if open_ports:
            print(f"\n🌐 **Puertos abiertos en {domain}:**")
            for index, port in enumerate(open_ports, start=1):
                print(f"  {index}. {port} 🔓")
        else:
            print(f"⚠️ No se encontraron puertos abiertos para {domain}.")

    except Exception as e:
        print(f"❗ Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    # Verifica si se ha pasado un dominio como argumento
    if len(sys.argv) != 2:
        print("❗ Por favor, ingresa un dominio o subdominio como argumento.")
        sys.exit(1)

    domain = sys.argv[1]  # Obtiene el dominio o subdominio desde la línea de comandos
    scan_ports(domain)