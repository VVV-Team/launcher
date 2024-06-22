## Bedrock Launcher

Простой лаунчер для Minecraft, написанный на Python с использованием PyQt5 и minecraft-launcher-lib.

### Особенности

* Современный пользовательский интерфейс с использованием PyQt5
* Поддержка ванильного Minecraft, Forge и Fabric
* Управление установкой Minecraft 
* Настройка параметров памяти и графики
* Встроенный менеджер модов
* Автоматическое обновление списка доступных версий

### Установка

1. Установите Python 3.7 или выше.
2. Установите зависимости:
```
pip install -r requirements.txt
```
3. Запустите лаунчер:
```
python bedrock.py
```

### Использование

1. На вкладке "Launch" выберите директорию установки Minecraft, версию игры, имя пользователя и нажмите "Launch Client".
2. На вкладке "Memory" настройте параметры выделения памяти для игры.
3. На вкладке "Graphics" настройте параметры графики.
4. На вкладке "Mod Manager" управляйте модами для выбранной версии Minecraft.

### Зависимости

* PyQt5
* minecraft-launcher-lib
* requests
* random-username
* uuid

### Лицензия

MIT LICENSE
