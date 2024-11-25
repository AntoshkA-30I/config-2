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


#--------------#--------------#--------------#--------------#--------------#--------------#--------------#--------------




import os
import zlib
import configparser

class GitDependencyGraph:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.dependencies = {}


    def get_git_dir(self):
        """Находит директорию .git в указанном репозитории."""
        git_dir = os.path.join(self.repo_path, ".git")
        if not os.path.isdir(git_dir):
            raise FileNotFoundError(f"Каталог .git не найден в репозитории: {self.repo_path}")
        return git_dir


    def read_object(self, sha):
        """Читает объект Git из .git/objects."""
        git_dir = self.get_git_dir()
        obj_dir = os.path.join(git_dir, "objects", sha[:2])  # Первые два символа — подпапка
        obj_path = os.path.join(obj_dir, sha[2:])  # Остальная часть — имя файла
        if not os.path.isfile(obj_path):
            print(f"Пропущен отсутствующий объект {sha}. Возможно, репозиторий повреждён.")
            return None
        try:
            with open(obj_path, "rb") as f:
                compressed_data = f.read()
                data = zlib.decompress(compressed_data)
                print(data)
            return data
        except zlib.error as e:
            print(f"Ошибка при декомпрессии объекта {sha}: {e}")
            return None

    def parse_commit(self, data):
        """Парсит содержимое объекта коммита."""
        if data is None:
            return []
        try:
            lines = data.decode(errors="replace").split("\n")
            parents = []
            for line in lines:
                if line.startswith("parent "):
                    parents.append(line.split()[1])  # SHA родительского коммита
                elif line == "":  # Конец заголовков
                    break
            return parents
        except Exception as e:
            print(f"Ошибка при разборе данных коммита: {e}")
            return []


    def check_repository_integrity(self):
        """Проверяет, что репозиторий содержит хотя бы один коммит."""
        git_dir = self.get_git_dir()
        refs_heads_dir = os.path.join(git_dir, "refs", "heads")
        if not os.path.isdir(refs_heads_dir):
            print("Не найдено ни одной ветки в репозитории.")
            return False

        # Проверка наличия HEAD
        head_path = os.path.join(git_dir, "HEAD")
        if not os.path.isfile(head_path):
            print("Файл HEAD отсутствует. Репозиторий повреждён.")
            return False

        return True


    def collect_dependencies(self):
        """Собирает зависимости коммитов, обходя историю из HEAD."""
        git_dir = self.get_git_dir()
        head_path = os.path.join(git_dir, "HEAD")
        if not os.path.isfile(head_path):
            raise FileNotFoundError("Файл HEAD не найден. Репозиторий повреждён?")

        # Получаем текущую ссылку (ref) или SHA коммита
        with open(head_path, "r") as f:
            ref = f.readline().strip()
        if ref.startswith("ref:"):
            ref_path = os.path.join(git_dir, ref[5:])
            with open(ref_path, "r") as f:
                current_commit = f.readline().strip()
        else:
            current_commit = ref  # Если в HEAD уже прямой SHA

        # Рекурсивно обходим историю коммитов
        to_visit = [current_commit]
        visited = set()

        while to_visit:
            sha = to_visit.pop()
            if sha in visited:
                continue
            visited.add(sha)

            try:
                data = self.read_object(sha)
                if data is None:
                    continue
                parents = self.parse_commit(data)
                self.dependencies[sha] = parents
                to_visit.extend(parents)  # Добавляем родителей для дальнейшего обхода
            except Exception as e:
                print(f"Ошибка при обработке коммита {sha}: {e}")

        return bool(self.dependencies)


    def build_graph(self):
        """Создаёт граф зависимости в формате Mermaid и выводит в консоль."""
        print("Создание графа зависимостей...")
        mermaid_output = "graph TD;\n"

        # Добавляем узлы и связи в граф
        for commit, parents in self.dependencies.items():
            commit_node = commit[:7]  # Для краткости отображаем только первые 7 символов SHA
            mermaid_output += f"    {commit_node}({commit_node})\n"
            for parent in parents:
                parent_node = parent[:7]
                mermaid_output += f"    {commit_node} --> {parent_node}\n"

        # Выводим результат в консоль
        print(mermaid_output)


    def generate_dependency_graph(self):
        """Главная функция для генерации графа зависимостей."""
        if not self.check_repository_integrity():
            print("Репозиторий некорректен или повреждён.")
            return

        if self.collect_dependencies():
            print("Зависимости успешно собраны. Создаём граф...")
            self.build_graph()
        else:
            print("Не удалось создать граф зависимостей.")


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    repo_path = config.get('Settings', 'repository_path')

    graph = GitDependencyGraph(repo_path)
    graph.generate_dependency_graph()

if __name__ == "__main__":
    main()









b"tree 168\x00100644 1.txt\x00\xd8\x00\x88m\x9c\x86s\x1a\xe5\xc4\xa6+\x0bw\xc47\x01^\x00\xd2100644 2.txt\x00\xe6\x9d\xe2\x9b\xb2\xd1\xd6CK\x8b)\xaewZ\xd8\xc2\xe4\x8cS\x9140000 folder1\x00\x88\xfe'\xf7W\xec\x01@\xc6\xa2\x85\x0c\x8a\xac\xd5\xc3\x9e\npl40000 folder2\x00\xea|\x8ag\xb7\xfe\xb3\xb6\xb7\xae\x99\x9f\xcf\xfbg\xcd\xd9&>x40000 folder3\x0056\x95p\xf8#\xfb\x0fm\xe7\xeb\xedJ>\x80:<\xccO\xf4"