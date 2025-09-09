from core import ServiceManager

sm = ServiceManager.instance
if not sm:
    raise ImportError("Service Manager não inicializado")

def getNames(): 
    names = sm.get_service_names() # type: ignore
    return names

def getDescriptionService(service: str):
    return

def getConfig():
    return

def getServiceDefault(service: str):
    return

def removeService():
    return 