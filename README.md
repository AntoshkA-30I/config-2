# Домашнее задание №2 Вариант 29

## Описание
Данный проект представляет собой набор функций на Python, предназначенных для работы с Git-репозиториями. Программа позволяет извлекать информацию о коммитах, измененных файлах и формировать граф коммитов в формате, удобном для визуализации. Проект использует стандартные библиотеки Python, такие как `subprocess` и `configparser`, что делает его легким в использовании и интеграции.

## Описание функций

### Функции:
- **load_config(config_path)**: Читает конфигурационный файл и возвращает настройки в виде словаря.
  
- **get_git_commits(repo_path)**: Получает список всех коммитов в репозитории с их сообщениями, возвращая их в виде списка строк.

- **get_files_from_commit(commit, repo_path)**: Извлекает измененные файлы для конкретного коммита, возвращая их в виде списка строк.

- **build_mermaid_graph(repo_path)**: Строит граф коммитов в формате Mermaid, возвращая его в виде списка строк. Граф включает коммиты и их родительские связи.

- **save_graph_to_file(graph, output_file)**: Сохраняет код графа в указанный файл.

## Переменные и настройки
- **config_path**: Путь к конфигурационному файлу `config.ini`, содержащему настройки для визуализации и путь к репозиторию.
- **visualization_path**: Путь к программе для визуализации графов.
- **repo_path**: Путь к Git-репозиторию, из которого извлекается информация о коммитах.
- **output_file**: Путь к файлу, в который будет сохранен код графа.

## Описание команд для сборки проекта
Для работы с проектом вам потребуется Python, установленный на вашей системе.

### Установка зависимостей
Не требуется установка дополнительных библиотек, так как используются стандартные библиотеки Python.

### Запуск приложения
1. Убедитесь, что у вас есть доступ к Git-репозиторию с необходимыми объектами. Важно: имена папок должны быть написаны латиницей!
2. Сохраните код в файл, например, `git_graph.py`.
3. Создайте конфигурационный файл `config.ini` с необходимыми параметрами.
4. Откройте терминал или командную строку и выполните команду:
   ```bash
   python git_graph.py
   ```
   Замените `git_graph.py` на имя вашего файла с кодом.


## Тестирование
### Тесты функциональности:
- Тест load_config: Функция корректно загружает настройки из конфигурационного файла.
- Тест get_git_commits: Успешное получение списка всех коммитов с сообщениями.
- Тест get_files_from_commit: Корректное извлечение измененных файлов для указанного коммита.
- Тест build_mermaid_graph: Успешное построение графа коммитов с правильными родительскими связями.
- Тест save_graph_to_file: Корректное сохранение графа в указанный файл.

### Результат работы программы-тестировщика:
![](https://github.com/AntoshkA-30I/config-2/blob/main/images/test%20program.png) 
### Ручное тестирование:
![](https://github.com/AntoshkA-30I/config-2/blob/main/images/test.png)
![](https://github.com/AntoshkA-30I/config-2/blob/main/images/test%20graph.png)
