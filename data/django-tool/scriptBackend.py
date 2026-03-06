import os, time, sys, subprocess

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'
   CYAN_BG = '\33[1;37;40m'

os.system('clear')

print(f'''{color.PURPLE}{color.BOLD}
\t                        _           __                          __            
\t    ____  _________    (_)__  _____/ /_   _____________  ____ _/ /_____  _____
\t   / __ \/ ___/ __ \  / / _ \/ ___/ __/  / ___/ ___/ _ \/ __ `/ __/ __ \/ ___/
\t  / /_/ / /  / /_/ / / /  __/ /__/ /_   / /__/ /  /  __/ /_/ / /_/ /_/ / /    
\t / .___/_/   \____/_/ /\___/\___/\__/   \___/_/   \___/\__,_/\__/\____/_/     
\t/_/              /___/                                                        
\n{color.END}''')

path = input(f'{color.YELLOW}Desired path of this project: {color.END}')

def loading(message, timeout):
    try:
        loadingAnimation = '-\\/-\\/-'

        for i in range(len(loadingAnimation)):
            print(f'{color.GREEN}{message}{color.END} {loadingAnimation[i]}', end='', flush=True)
            time.sleep(timeout)
            
            sys.stdout.write('\r')
            sys.stdout.write(' ' * (len(message) + len(loadingAnimation) + 2))
            sys.stdout.write('\r')
        print(f'{color.GREEN}Created successfully{color.END}')
    except Exception as e:
        print(f'{color.RED}Error please report this problem or create you venv manually !!{color.END}')

def DjangoNoRest():
    os.chdir(appName)
    os.system('touch urls.py')
    os.system(f'''echo "from django.urls import path
from .views import *

urlpatterns = [
    path('AppRoute/', YOUR_VIEW),
]" > urls.py''')
    os.system(f'''echo "from django.shortcuts import render

# Create your views here.
def YOUR_VIEW(request):
    pass" > views.py
''')
    os.chdir(f'../{projectName}')
    searchItem = 'django.contrib.staticfiles'
    with open('settings.py', 'r') as file:
        lines = file.readlines()
    for index, line in enumerate(lines, start=1):
        if searchItem in line:
            lines.insert(index, f'\t\'{appName}\'\n')
            break
    with open('settings.py', 'w') as f:
        f.writelines(lines)
    os.system(f'''echo "from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('{appName}/', include('{appName}.urls')),
]" > urls.py''')
    os.chdir(f'..')
    loading('Configuring Django files...', .5)

def DjangoRest():
    os.chdir(appName)
    run_command('pip install djangorestframework')
    run_command('pip install drf-nested-routers')
    run_command('pip install django-cors-headers')
    searchItem = 'django.contrib.staticfiles'
    with open(f'../{projectName}/settings.py', 'r+') as file:
        lines = file.readlines()
    for index, line in enumerate(lines, start=1):
        if searchItem in line:
            lines.insert(index, f'\t\'{appName}\'\n')
            lines.insert(index, '\t\'rest_framework\',\n')
            break
    with open(f'../{projectName}/settings.py', 'w') as f:
        f.writelines(lines)
    os.system('touch urls.py')
    os.system('touch serializers.py')
    os.system(f'''echo "from rest_framework_nested import routers
from .views import *

router = routers.DefaultRouter()
router.register('UR_ROUTE', ViewSet)

urlpatterns = router.urls" > urls.py''')

    os.system(f'''echo "from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializers import *

class ViewSet(ModelViewSet):
    pass" > views.py
''')

    os.chdir(f'../{projectName}')
    os.system(f'''echo "from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('{appName}/', include('{appName}.urls')),
]" > urls.py''')
    os.chdir(f'..')
    loading('Configuring REST files...', .5)

def run_command(command):
    result = subprocess.run(command.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode == 0:
        print(f'{color.GREEN}Package downloaded successfully{color.END}')
    else:
        print(f'{color.RED}Error occured !{color.END}')

def exit_program():
    print(f"{color.RED}Exiting program...{color.END}")
    print(f'{color.BOLD}{color.GREEN}\n\t\t\t     Done !\n{color.RED}\tDon\'t forget to add your app in setting and django-restframework{color.END}\n\t\t\t{color.CYAN}Github: MoeNassi{color.END}')
    exit(1)

def CreateModuls():
    modulsName = input(f'{color.GREEN}give me all the models (separated by commas for example: model1, model2 ...): {color.END}')
    splitted = modulsName.split(', ')
    os.chdir(appName)
    for module in splitted:
        os.system(f'''echo "class {module}(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name\n" >> models.py''')
    os.chdir('../')
    run_command(f'python3 manage.py makemigrations')
    run_command(f'python3 manage.py migrate')
    loading('Configuring Models...', 1)

if os.path.isdir(path) and os.path.exists(path):
    answer = input(f'{color.YELLOW}Would you like to create a venv in the desired directory: {color.END}')

    if answer.lower() == 'yes' or answer.lower() == 'y':
        os.system(f'python3 -m venv {path}.venv')
        loading('Creating Virtual Envirement', 1)

    projectName = input(f'{color.YELLOW}Choose a name for your project: {color.END}')
    
    if os.path.exists(f'{path}{projectName}'):
        print(f'{color.RED}Directory exists !{color.END}')
        exit(1)
    
    os.chdir(path)
    os.system('source .venv/bin/activate')
    run_command('pip install django')
    os.system(f'django-admin startproject {projectName}')
    os.chdir(f'{path}{projectName}')

    appName = input(f'{color.YELLOW}Choose a name for your app: {color.END}')

    os.system(f'django-admin startapp {appName}')

    create = input(f'{color.YELLOW}would you like to create a requirements file: {color.END}')
    if create.lower() == 'yes' or create.lower() == 'y':
        os.system('pip freeze > requirements.txt')
    
    setup = input(f'{color.YELLOW}you want to set up the files for django ? (yes or no): {color.END}')
   
    if setup.lower() == 'yes' or setup.lower() == 'y':
        functions = [DjangoNoRest, DjangoRest, CreateModuls, exit_program]
        while True:
            print(f'{color.BOLD}\t0. Simple setup (views, urls (if you\'re using Django{color.END}')
            print(f'{color.BOLD}\t1. Advanced setup (serializers, ViewSets (if you\'re using REST framework{color.END}')
            print(f'{color.BOLD}\t2. Configure the models as you like{color.END}')
            print(f'{color.BOLD}\t3. Exit{color.END}')
            number = input(f'{color.YELLOW}Choose a number: {color.END}')
            if number.isdigit() and 0 <= int(number) <= 3:
                functions[int(number)]()

    print(f'{color.BOLD}{color.GREEN}\n\t\t\t     Done !\n{color.RED}\tAdd your app name and rest framework in settings{color.END}\n\t\t\t{color.CYAN}Github: MoeNassi{color.END}')

else:
    print(f'{color.BOLD}{color.RED}\n\t\t\tDirectory doesn\'t exist{color.END}')
