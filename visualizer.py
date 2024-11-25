import os
import zlib
import configparser


# Функция получения данных о файлах из обьекта-дерева
def parse_tree_object(tree_hash):
    path = os.path.join('.git', 'objects', tree_hash[:2], tree_hash[2:])
    if not os.path.isfile(path):
        return None
    with open(path, 'rb') as f:
        data = f.read()
    data = zlib.decompress(data)

    header_end = data.index(b'\0')    
    content = data[header_end + 1:]
    index = 0
    files_info = {}

    while index < len(content):
        # Читаем режим доступа
        mode_end = index + 6
        mode = content[index:mode_end].decode() 
        index = mode_end
        
        # Находим конец имени файла
        name_end = content.index(b'\0', index)
        name = content[index:name_end].decode()
        index = name_end + 1 
        
        # Получаем хеш
        hash_value = content[index:index + 20] 
        index += 20 
        
        # Проверяем, является ли обьект деревом или файлом
        if mode.startswith('40000'): # если это дерево
            sub_tree_hash = hash_value.hex()
            sub_files_info = parse_tree_object(sub_tree_hash)
            if sub_files_info:
                for sub_name in sub_files_info:
                    files_info[f"{name}/{sub_name}"] = sub_files_info[sub_name]
        else: 
            files_info[name] = hash_value.hex()

    return files_info



# Функция получения данных о коммите из обьекта-коммита
def parse_commit_object(commit_hash):
    path = os.path.join('.git', 'objects', commit_hash[:2], commit_hash[2:])
    if not os.path.isfile(path):
        return None, None
    with open(path, 'rb') as f:
        data = f.read()
    data = zlib.decompress(data)

    header_end = data.index(b'\0')   
    header = data[:header_end].decode()
    obj_type, size = header.split(' ')        
    content = data[header_end + 1:].decode('utf-8').splitlines()

    return obj_type, content



# Функция обработки коммита
def get_commit_info(commit_hash):
    obj_type, content = parse_commit_object(commit_hash)
    print()
    print(obj_type, content)
    if obj_type != 'commit':
        return None
    
    commit_info = {}
    commit_info['name'] = content[-1]  # Сообщение коммита находится в последней строке
    commit_info['files'] = {}
    commit_info['changed_files'] = []
    commit_info['parent'] = None

    # Сначала собираем информацию о файлах в текущем коммите
    for line in content:
        if line.startswith('parent'):
            parent_hash = line.split()[1]
            commit_info['parent'] = get_commit_info(parent_hash)
        elif line.startswith('tree'):
            tree_hash = line.split()[1]
            files = parse_tree_object(tree_hash)
            commit_info['files'] = files  # Сохраняем файлы и их хэши для данного коммита

    # Если есть родительский коммит, сравниваем файлы
    if commit_info['parent']:
        parent_files = commit_info['parent']['files']
        
        # Сравниваем файлы текущего коммита с файлами родительского
        for filename, current_hash in commit_info['files'].items():
            if filename in parent_files:
                parent_hash = parent_files[filename]
                if current_hash != parent_hash:
                    commit_info['changed_files'].append(filename)  # Файл изменился
            else:
                commit_info['changed_files'].append(filename)  # Файл добавлен

        # Проверяем, есть ли файлы в родительском коммите, которых нет в текущем
        for filename in parent_files:
            if filename not in commit_info['files']:
                commit_info['changed_files'].append(filename)  # Файл удален
    return commit_info



def get_commit_history(repo_path):
    os.chdir(repo_path)
    
    # Получаем последний коммит из ветки master (или другой ветки по умолчанию)
    branch_path = os.path.join(repo_path, '.git', 'refs', 'heads', 'master')  
    with open(branch_path, 'r', encoding='utf-8') as f:
        commit_hash = f.read().strip()
        commit_info = get_commit_info(commit_hash)
        print(commit_info)
        mermaid_output = generate_mermaid(commit_info)
        print(mermaid_output)



def generate_mermaid(commit):
    mermaid_string = "graph TD;\n"

    # Функция для рекурсивного обхода коммитов
    def traverse(commit):
        nonlocal mermaid_string
        commit_message = commit['name']
        changed_files = ', '.join(commit.get('changed_files', [])) or 'No changes'

        # Создаем уникальный идентификатор для коммита на основе его сообщения
        commit_id = commit_message.replace(' ', '_').replace('-', '_')

        # Добавляем текущий коммит в строку mermaid
        mermaid_string += f"    {commit_id}({commit_message}\nChanged files: {changed_files})\n"
        
        # Если есть родительский коммит, добавляем связь
        if commit['parent']:
            parent_message = commit['parent']['name']
            parent_id = parent_message.replace(' ', '_').replace('-', '_')
            mermaid_string += f"    {parent_id} --> {commit_id}\n"
            traverse(commit['parent'])  # Рекурсивно обходим родительский коммит

    traverse(commit)
    return mermaid_string




config_file = 'config.ini'  # Укажите путь к вашему конфигурационному файлу
# Чтение конфигурационного файла формата INI
config = configparser.ConfigParser()
config.read(config_file)

# Извлечение пути к репозиторию
repo_path = config.get('settings', 'repository_path', fallback=None)
    
if repo_path:
    result = get_commit_history(repo_path)
    print(result)
else:
    print("Путь к репозиторию не найден в конфигурационном файле.")

