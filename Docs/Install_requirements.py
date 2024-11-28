import sys
import subprocess
import venv
import os
import platform

def crear_entorno_virtual():
    """Crear un entorno virtual para el proyecto"""
    print("Creando entorno virtual...")
    try:
        venv.create('venv', with_pip=True)
        print("✅ Entorno virtual creado exitosamente")
    except Exception as e:
        print(f"❌ Error creando entorno virtual: {e}")
        sys.exit(1)

def instalar_dependencias():
    """Instalar dependencias desde requirements.txt"""
    print("Instalando dependencias...")
    
    # Determinar el comando pip según el sistema operativo
    pip_command = 'pip'
    if platform.system() == 'Windows':
        pip_command = os.path.join('venv', 'Scripts', 'pip')
    else:
        pip_command = os.path.join('venv', 'bin', 'pip')
    
    try:
        # Instalar desde requirements.txt
        subprocess.check_call([pip_command, 'install', '-r', 'requirements.txt'])
        print("✅ Dependencias instaladas correctamente")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        sys.exit(1)

def verificar_instalacion():
    """Verificar que las librerías se instalaron correctamente"""
    print("\nVerificando instalación de librerías...")
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ Todas las librerías se instalaron correctamente")
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        sys.exit(1)

def main():
    """Flujo principal de instalación"""
    print("🚀 Iniciando instalación de dependencias del proyecto")
    
    # Verificar versión de Python
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        sys.exit(1)
    
    crear_entorno_virtual()
    instalar_dependencias()
    verificar_instalacion()
    
    print("\n🎉 Instalación completada exitosamente")
    print("Para activar el entorno virtual:")
    if platform.system() == 'Windows':
        print("- Ejecuta: venv\\Scripts\\activate")
    else:
        print("- Ejecuta: source venv/bin/activate")
    print("Para ejecutar la aplicación: python main.py")

if __name__ == '__main__':
    main()