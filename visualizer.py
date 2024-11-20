import subprocess
import configparser


# Функция чтения конфигурационного файла
def load_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config['settings']


# Функция получения списка всех коммитов с их сообщениями
def get_git_commits(repo_path):
    result = subprocess.run(['git', 'rev-list', '--all', '--pretty=format:%H %s'], cwd=repo_path, capture_output=True, text=True)
    return result.stdout.splitlines()


# Функция получения измененных файлов для конкретного коммита
def get_files_from_commit(commit, repo_path):
    result = subprocess.run(['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit.split()[0]], cwd=repo_path, capture_output=True, text=True)
    return result.stdout.splitlines()


# Функция построения кода графа
def build_mermaid_graph(repo_path):
    commits = get_git_commits(repo_path)
    graph = ["graph TD"]    # код графа
    seen_commits = set()    # просмотреные коммиты

    for commit in commits:
        commit_hash, commit_message = commit.split(' ', 1)

        # Пропускаем уже добавленные коммиты
        if commit_hash in seen_commits: 
            continue
        
        seen_commits.add(commit_hash) 
        files = get_files_from_commit(commit, repo_path)
        files_list = ', '.join(files) if files else "No files"
        graph.append(f"    {commit_hash}({commit_message.strip()}: {files_list})")

        # Получаем родительские коммиты
        parent_result = subprocess.run(['git', 'rev-list', '--parents', '-n', '1', commit_hash], cwd=repo_path, capture_output=True, text=True)
        parent_commits = parent_result.stdout.split()
        
        for parent in parent_commits[1:]:
            if parent not in seen_commits:
                graph.append(f"    {parent} --> {commit_hash}")

    return graph


# Функция сохранения кода графа в файл
def save_graph_to_file(graph, output_file):
    with open(output_file, 'w') as f:
        f.write(graph)


def main():
    config = load_config('config.ini')                  # Конфигурационный файл
    visualization_path = config['visualization_path']   # Путь к программе для визуализации графов
    repo_path = config['repository_path']               # Путь к анализируемому репозиторию
    output_file = config['output_file']                 # Путь к файлу-результату в виде кода

    # Строим и записываем код графа
    graph = build_mermaid_graph(repo_path)
    graph.pop(1)
    graph = "\n".join(graph)
    save_graph_to_file(graph, output_file)

    print(graph)
    print(f"Путь к программе для визуализации: {visualization_path}")



if __name__ == "__main__":
    main()
