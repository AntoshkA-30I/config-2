import subprocess
import configparser


def load_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config['settings']


def get_git_commits(repo_path):
    result = subprocess.run(['git', 'rev-list', '--all', '--pretty=format:%H %s'], cwd=repo_path, capture_output=True, text=True)
    return result.stdout.splitlines()


def get_files_from_commit(commit, repo_path):
    result = subprocess.run(['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit.split()[0]], cwd=repo_path, capture_output=True, text=True)
    return result.stdout.splitlines()


def main():
    config = load_config('config.ini')                  # Конфигурационный файл
    visualization_path = config['visualization_path']   # Путь к программе для визуализации графов
    repo_path = config['repository_path']               # Путь к анализируемому репозиторию
    output_file = config['output_file']                 # Путь к файлу-результату в виде кода

    print(get_git_commits(repo_path))
    

if __name__ == "__main__":
    main()
