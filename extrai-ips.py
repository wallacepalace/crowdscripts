# Extrai IPs de qualquer documento e os ordena, um IP por linha
# Basta colocar todo o texto que contém os IPs em um arquivo "ips.txt". Se quiser, troque o nome do arquivo em "with open('ips.txt'...)"
# Wallace Alves

import re

def extrair_ips(texto):
    pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
    return pattern.findall(texto)

ips_unicos = set()

try:
    with open('ips.txt', 'r') as arquivo:
        conteudo = arquivo.read()
        ips_encontrados = extrair_ips(conteudo)
        ips_unicos.update(ips_encontrados)

    ips_ordenados = list(ips_unicos)
    ips_ordenados.sort(key=lambda ip: tuple(int(octeto) for octeto in ip.split('.')))

    with open('tratados.txt', 'w') as arquivo_tratado:
        for ip in ips_ordenados:
            arquivo_tratado.write(ip + '\n')

    print("Arquivo 'tratados.txt' criado com sucesso.")

except FileNotFoundError:
    print("O arquivo com os IPs não foi encontrado.")
except Exception as e:
    print(f"Um erro ocorreu: {e}")
