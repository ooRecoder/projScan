from app import App
from utils import LockApp, GitHubUploader, FilePathManager
from core import AppLogger, AppConfig, ServiceManager, ComputerManager, ConfigManager
from gui.components import show_custom_message

def main():
    singleton = LockApp()
    
    if singleton.is_already_running():
        show_custom_message('Aviso', "O aplicativo já está aberto")
        singleton.bring_to_front()
        return
    
    print("=================Inicializando=================")
    AppLogger() # Logging
    FilePathManager() # Serve para resolver caminhos
    AppConfig() # Carrega as configurações gerais da aplicação
    GitHubUploader() # Serve para fazer upload dos scaneamentos
    ServiceManager() # Carrega as configurações gerais dos serviços
    ConfigManager() # Carrega as configurações do usuário para os serviços
    ComputerManager() # Carrega os dados das máquinas scanneadas
    
    app = App()
    
    input("Pressiona ENTER...")
    return

if __name__ == "__main__":
    main()