import sys
from cx_Freeze import setup, Executable

base = None

if sys.platform == 'win32':
    base = 'Win32GUI'

options = {
    'build_exe': {
        'include_files': ['files'],  # Add any additional files or data needed here
    },
}

executables = [
    Executable('attend.py', base=base, icon='files/icon/icon.ico', target_name='Biomedance.exe'),  # Replace 'your_main_script.py' with your main script
]

setup(
    name='Biomedance',
    version='1.0',
    description='Biomedance - Biometric attendance tracking software',
    options=options,
    executables=executables
)
