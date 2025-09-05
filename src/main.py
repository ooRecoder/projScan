from app import App
from utils import LockApp, GitHubUploader, FilePathManager
from core import AppLogger, AppConfig, ServiceManager
from gui.components import show_custom_message

def main():
    singleton = LockApp()
    
    if singleton.is_already_running():
        show_custom_message('Aviso', "O aplicativo já está aberto")
        singleton.bring_to_front()
        return
    
    print("=================Inicializando=================")
    AppLogger()
    FilePathManager()
    AppConfig()
    GitHubUploader()
    ServiceManager()
    
    
    app = App()
    
    input("Pressiona ENTER...")
    return

if __name__ == "__main__":
    main()