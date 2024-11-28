import subprocess
import sys
import platform

def run_tests():
    """Ejecutar pruebas unitarias"""
    print("🧪 Ejecutando pruebas unitarias...")
    
    # Determinar el comando pip y pytest según el sistema operativo
    if platform.system() == 'Windows':
        pytest_command = '.\\venv\\Scripts\\pytest'
    else:
        pytest_command = './venv/bin/pytest'
    
    try:
        # Ejecutar pruebas con cobertura y detalles
        result = subprocess.run(
            [pytest_command, 
             'test_api.py', 
             '-v',  # Verbose
             '--tb=short',  # Traceback corto
             '--disable-warnings'  # Deshabilitar warnings
            ], 
            capture_output=True, 
            text=True
        )
        
        print(result.stdout)
        
        if result.returncode != 0:
            print("❌ Algunas pruebas fallaron:")
            print(result.stderr)
            sys.exit(result.returncode)
        else:
            print("✅ Todas las pruebas pasaron exitosamente")
    
    except Exception as e:
        print(f"❌ Error ejecutando pruebas: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_tests()