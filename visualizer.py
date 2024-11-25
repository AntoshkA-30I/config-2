import os
import zlib
import configparser


def read_object(sha, is_tree):
    obj_type, content = None, None
    path = os.path.join('.git', 'objects', sha[:2], sha[2:])
    if not os.path.isfile(path):
        return None, None
    with open(path, 'rb') as f:
        data = f.read()
    data = zlib.decompress(data)
    print()
    print(data)
    
    if not is_tree:
        header_end = data.index(b'\0')        # Извлекаем заголовок и декодируем его в строку
        header = data[:header_end].decode()
        obj_type, size = header.split(' ')        # Разделяем заголовок на тип и размер
        # Извлекаем содержимое объекта, начиная с байта, следующего за нулевым байтом  # Декодируем содержимое в строку
        content = data[header_end + 1:].decode('utf-8').splitlines()
    else:
        pass # чтение значений дерева #function
    print(obj_type, content)
    return obj_type, content


def get_commit_info(commit_sha):
    obj_type, content = read_object(commit_sha, False)
    if obj_type != 'commit':
        return None
    
    commit_info = {}
    commit_info['name'] = content[-1]  # Сообщение коммита находится в последней строке
    commit_info['parent'] = None
    commit_info['changed_files'] = []

    for line in content:
        if line.startswith('parent'):
            hash = line.split()[1]
            commit_info['parent'] = get_commit_info(hash)
            #parent blobs hash
        elif line.startswith('author'):
            commit_info['author'] = line.split(' ', 2)[2]
        elif line.startswith('tree'):
            tree_hash = line.split()[1]
            commit_info['changed_files'] = read_object(tree_hash, True)

    return commit_info


def get_commit_history(repo_path):
    os.chdir(repo_path)
    
    # Получаем последний коммит из ветки master (или другой ветки по умолчанию)
    branch_path = os.path.join(repo_path, '.git', 'refs', 'heads', 'master')  
    with open(branch_path, 'r', encoding='utf-8') as f:
        commit_sha = f.read().strip()
        commit_info = get_commit_info(commit_sha)
        #print(commit_info)
        #return comp(translate(commit_info))




#-------------------
# Данные в байтовом формате
data = b'\xd5\xa8\x19\xbd\xef\r\xe2\t9K\x10@d\xff\xf7\xa3\x1b\xc3\xd0\xaa'

# Преобразование в шестнадцатеричную строку
hex_representation = data.hex()
print(hex_representation)

print()
print()
#-------------------


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
