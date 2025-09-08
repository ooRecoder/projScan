import os
from pathlib import Path

def escanear_estrutura(diretorio=".", nivel=0, mostrar_arquivos_ocultos=False):
    """
    Escaneia a estrutura de pastas e arquivos de um diretório
    
    Args:
        diretorio (str): Diretório a ser escaneado
        nivel (int): Nível de indentação (para recursão)
        mostrar_arquivos_ocultos (bool): Se deve mostrar arquivos/pastas ocultos
    """
    try:
        caminho = Path(diretorio)
        
        # Verifica se o diretório existe
        if not caminho.exists():
            print(f"❌ Diretório não encontrado: {caminho}")
            return
        
        # Lista todos os itens no diretório
        itens = list(caminho.iterdir())
        
        # Ordena os itens: pastas primeiro, depois arquivos, ambos em ordem alfabética
        pastas = sorted([item for item in itens if item.is_dir() and (mostrar_arquivos_ocultos or not item.name.startswith('.'))], 
                       key=lambda x: x.name.lower())
        arquivos = sorted([item for item in itens if item.is_file() and (mostrar_arquivos_ocultos or not item.name.startswith('.'))], 
                         key=lambda x: x.name.lower())
        
        # Imprime a estrutura
        indentacao = "    " * nivel
        
        for pasta in pastas:
            print(f"{indentacao}📁 {pasta.name}/")
            escanear_estrutura(pasta, nivel + 1, mostrar_arquivos_ocultos)
        
        for arquivo in arquivos:
            tamanho = arquivo.stat().st_size
            print(f"{indentacao}📄 {arquivo.name} ({tamanho} bytes)")
            
    except PermissionError:
        print(f"{indentacao}❌ Permissão negada: {caminfo.name}")
    except Exception as e:
        print(f"{indentacao}❌ Erro ao acessar {caminho}: {e}")

def escanear_estrutura_simples(diretorio="."):
    """
    Versão simplificada do escaneamento
    """
    for raiz, pastas, arquivos in os.walk(diretorio):
        nivel = raiz.count(os.sep) - diretorio.count(os.sep)
        indentacao = "    " * nivel
        print(f"{indentacao}📁 {os.path.basename(raiz)}/")
        
        sub_indentacao = "    " * (nivel + 1)
        for pasta in sorted(pastas):
            print(f"{sub_indentacao}📁 {pasta}/")
        
        for arquivo in sorted(arquivos):
            caminho_completo = os.path.join(raiz, arquivo)
            tamanho = os.path.getsize(caminho_completo)
            print(f"{sub_indentacao}📄 {arquivo} ({tamanho} bytes)")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Escaneia a estrutura de pastas e arquivos")
    parser.add_argument("-d", "--diretorio", default=".", help="Diretório a ser escaneado")
    parser.add_argument("-o", "--ocultos", action="store_true", help="Mostrar arquivos/pastas ocultos")
    parser.add_argument("-s", "--simples", action="store_true", help="Usar método simplificado")
    
    args = parser.parse_args()
    
    print(f"🔍 Escaneando estrutura de: {os.path.abspath(args.diretorio)}")
    print("=" * 60)
    
    if args.simples:
        escanear_estrutura_simples(args.diretorio)
    else:
        escanear_estrutura(args.diretorio, 0, args.ocultos)
    
    print("=" * 60)
    print("✅ Escaneamento concluído!")