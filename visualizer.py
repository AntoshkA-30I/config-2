import os
import zlib
import configparser
import argparse


class GitParser:
    def __init__(self, repo_path):
        self.repo_path = repo_path


    # Функция получения данных о файлах из объекта-дерева
    def parse_tree_object(self, tree_hash):
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
            
            # Проверяем, является ли объект деревом или файлом
            if mode.startswith('40000'):  # если это дерево
                sub_tree_hash = hash_value.hex()
                sub_files_info = self.parse_tree_object(sub_tree_hash)
                if sub_files_info:
                    for sub_name in sub_files_info:
                        files_info[f"{name}/{sub_name}"] = sub_files_info[sub_name]
            else: 
                files_info[name] = hash_value.hex()

        return files_info


    # Функция получения данных о коммите из объекта-коммита
    def parse_commit_object(self, commit_hash):
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
    def get_commit_info(self, commit_hash):
        obj_type, content = self.parse_commit_object(commit_hash)
        if obj_type != 'commit':
            return None
        
        commit_info = {
            'name': content[-1],  # Сообщение коммита 
            'files': {},          # Текущие файлы
            'changed_files': [],  # Измененные файлы
            'parents': []         # Родители
        }

        for line in content:
            if line.startswith('parent'):
                parent_hash = line.split()[1]
                commit_info['parents'].append(self.get_commit_info(parent_hash))  # Добавляем родителя в список
            elif line.startswith('tree'):
                tree_hash = line.split()[1]
                files = self.parse_tree_object(tree_hash)
                commit_info['files'] = files  # Сохраняем файлы и их хэши для данного коммита

        # Сравниваем файлы с родительскими коммитами
        for parent in commit_info['parents']:
            parent_files = parent['files']
            
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


    # Функция получения истории всех коммитов
    def get_commit_history(self):
        os.chdir(self.repo_path)
        
        # Получаем последний коммит из ветки master (или другой ветки по умолчанию)
        branch_path = os.path.join(self.repo_path, '.git', 'refs', 'heads', 'master')  
        with open(branch_path, 'r', encoding='utf-8') as f:
            commit_hash = f.read().strip()
            commit_info = self.get_commit_info(commit_hash)
        return commit_info


    # Функция перевода на язык mermaid
    def generate_mermaid(self, commit):
        mermaid_string = "graph TD;\n"
        visited_commits = set()  # Множество для отслеживания уже посещенных коммитов

        # Функция для рекурсивного обхода коммитов
        def traverse(commit):
            nonlocal mermaid_string
            commit_message = commit['name']
            changed_files = ', '.join(commit.get('changed_files', [])) or 'No changes'

            # Создаем уникальный идентификатор для коммита на основе его сообщения
            commit_id = commit_message.replace(' ', '_').replace('-', '_')

            # Проверяем, был ли уже добавлен этот коммит
            if commit_id not in visited_commits:
                visited_commits.add(commit_id)  # Добавляем коммит в множество посещенных
                # Добавляем текущий коммит в строку mermaid
                mermaid_string += f"    {commit_id}({commit_message}\nChanged files: {changed_files})\n"
            
                # Если есть родительские коммиты, добавляем связи
                for parent in commit['parents']:
                    parent_message = parent['name']
                    parent_id = parent_message.replace(' ', '_').replace('-', '_')
                    mermaid_string += f"    {parent_id} --> {commit_id}\n"
                    traverse(parent)  # Рекурсивно обходим родительский коммит

        traverse(commit)
        return mermaid_string


def main(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)

    repo_path = config.get('settings', 'repository_path')  # Извлечение пути к репозиторию

    if repo_path:
        git_parser = GitParser(repo_path)
        commit_history = git_parser.get_commit_history()
        mermaid_output = git_parser.generate_mermaid(commit_history)
        print(mermaid_output)
        print('Вы можете визуализировать граф здесь: ', config.get('settings', 'visualization_path'))
    else:
        print("Путь к репозиторию не найден в конфигурационном файле.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path", help="Введите путь до конфигурационного файла", type=str)
    args = parser.parse_args()
    
    main(args.config_path)
