from app import App
from utils import LockApp, GitHubUploader
from core import AppLogger, AppConfig
from gui.components import show_custom_message

def main():
    singleton = LockApp()
    
    if singleton.is_already_running():
        show_custom_message('Aviso', "O aplicativo já está aberto")
        singleton.bring_to_front()
        return
    
    print("=================Inicializando=================")
    AppLogger()
    AppConfig()
    GitHubUploader()
    
    app = App()
    
    input("Pressiona ENTER...")
    return

if __name__ == "__main__":
    main()