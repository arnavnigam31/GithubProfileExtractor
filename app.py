import requests
import os
import subprocess
import shutil
import time
import stat
import math
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.text import Text


GITHUB_API_URL = "https://api.github.com"

def fetch_github_repositories(username):
    url = f"{GITHUB_API_URL}/users/{username}/repos"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return None

def fetch_repo_details(username, repo_name):
    url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as err:
        print(f"Failed to fetch details for {repo_name}: {err}")
        return None

def clone_repository(repo_url, repo_name):
    repo_dir = os.path.join(os.getcwd(), repo_name)
    if os.path.exists(repo_dir):
        print(f"Repository {repo_name} already exists. Removing and re-cloning...")
        safe_remove_directory(repo_dir)
    
    try:
        subprocess.run(["git", "clone", repo_url, repo_dir], check=True, capture_output=True, text=True)
        print(f"Successfully cloned {repo_name}")
        return repo_dir
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository {repo_name}: {e}")
        print(f"Git output: {e.output}")
        return None

def change_permissions_recursive(path):
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            os.chmod(os.path.join(root, dir), stat.S_IRWXU)
        for file in files:
            os.chmod(os.path.join(root, file), stat.S_IRWXU)

def on_rm_error(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def safe_remove_directory(directory):
    max_attempts = 1
    for attempt in range(max_attempts):
        try:
            change_permissions_recursive(directory)
            shutil.rmtree(directory, onerror=on_rm_error)
            return True
        except PermissionError as e:
            print(f"Permission error when removing directory {directory}: {e}")
            if attempt < max_attempts - 1:
                print(f"Retrying in 5 seconds... (Attempt {attempt + 1}/{max_attempts})")
                time.sleep(5)
            else:
                print(f"Failed to remove directory after {max_attempts} attempts.")
                print("Please manually delete the directory when possible.")
                return False
        except Exception as e:
            print(f"Unexpected error when removing directory {directory}: {e}")
            return False

def analyze_js_code(repo_dir):
    eslint_path = 'eslint'  
    complexity_score = 0
    file_count = 0

    for root, dirs, files in os.walk(repo_dir):
        for file in files:
            if file.endswith('.js'):
                file_path = os.path.join(root, file)
                print(f"Analyzing {file_path} with ESLint...")
                try:
                    result = subprocess.run([eslint_path, file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    print(result.stdout)
                    if result.returncode != 0:
                        complexity_score += 1
                    file_count += 1
                except Exception as e:
                    print(f"Error running ESLint on {file_path}: {e}")
    return complexity_score / file_count if file_count > 0 else 0

def analyze_py_code(repo_dir):
    pylint_path = 'pylint'
    complexity_score = 0
    file_count = 0

    for root, dirs, files in os.walk(repo_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                print(f"Analyzing {file_path} with pylint...")
                try:
                    result = subprocess.run([pylint_path, file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    print(result.stdout)
                    complexity_score += int(result.returncode)
                    file_count += 1
                except Exception as e:
                    print(f"Error running pylint on {file_path}: {e}")
    return complexity_score / file_count if file_count > 0 else 0

def analyze_cpp_code(repo_dir):
    cppcheck_path = 'cppcheck'
    complexity_score = 0
    file_count = 0

    for root, dirs, files in os.walk(repo_dir):
        for file in files:
            if file.endswith('.cpp') or file.endswith('.h'):
                file_path = os.path.join(root, file)
                print(f"Analyzing {file_path} with cppcheck...")
                try:
                    result = subprocess.run([cppcheck_path, file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    print(result.stderr)  # cppcheck outputs to stderr
                    if "error" in result.stderr.lower() or "warning" in result.stderr.lower():
                        complexity_score += 1
                    file_count += 1
                except Exception as e:
                    print(f"Error running cppcheck on {file_path}: {e}")
    return complexity_score / file_count if file_count > 0 else 0

def calculate_cyclomatic_complexity(repo_dir):
    radon_path = 'radon'
    total_complexity = 0
    file_count = 0

    for root, dirs, files in os.walk(repo_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    result = subprocess.run([radon_path, 'cc', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    complexity = sum(int(line.split()[-1]) for line in result.stdout.splitlines() if line.strip())
                    total_complexity += complexity
                    file_count += 1
                except Exception as e:
                    print(f"Error calculating cyclomatic complexity for {file_path}: {e}")

    return total_complexity / file_count if file_count > 0 else 0

def analyze_folder_structure(repo_dir):
    max_depth = 0
    total_files = 0
    
    for root, dirs, files in os.walk(repo_dir):
        depth = root[len(repo_dir):].count(os.sep)
        max_depth = max(max_depth, depth)
        total_files += len(files)
    
    return max_depth, total_files

def analyze_file_dependencies(repo_dir):
    dependencies = defaultdict(set)
    
    for root, dirs, files in os.walk(repo_dir):
        for file in files:
            if file.endswith(('.py', '.js', '.cpp', '.h')):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                    for other_file in files:
                        if other_file != file and other_file in content:
                            dependencies[file].add(other_file)
    
    return len(dependencies), sum(len(deps) for deps in dependencies.values())

def analyze_unique_tech_usage(repo_dir):
    tech_stack = set()
    
    for root, dirs, files in os.walk(repo_dir):
        for file in files:
            if file.endswith('.py'):
                tech_stack.add('Python')
            elif file.endswith('.js'):
                tech_stack.add('JavaScript')
            elif file.endswith('.cpp') or file.endswith('.h'):
                tech_stack.add('C++')
    
    return len(tech_stack)

def calculate_complexity_score(metrics):
    weights = {
        'loc': 0.2,
        'cyclomatic_complexity': 0.2,
        'folder_depth': 0.1,
        'file_count': 0.1,
        'dependencies': 0.15,
        'unique_tech': 0.1,
        'code_quality': 0.15
    }
    
    max_values = {
        'loc': 100000,
        'cyclomatic_complexity': 50,
        'folder_depth': 10,
        'file_count': 1000,
        'dependencies': 1000,
        'unique_tech': 10,
        'code_quality': 10
    }
    
    normalized_metrics = {k: min(v / max_values[k], 1) for k, v in metrics.items()}

    complexity_score = sum(normalized_metrics[k] * weights[k] for k in weights)
    
    return complexity_score

def analyze_repository_complexity(username, repo_name, repo_url):
    repo_dir = clone_repository(repo_url, repo_name)
    if not repo_dir:
        print(f"Failed to clone repository {repo_name}. Skipping analysis.")
        return None

    try:
        js_complexity = analyze_js_code(repo_dir)
        py_complexity = analyze_py_code(repo_dir)
        cpp_complexity = analyze_cpp_code(repo_dir)
        cyclomatic_complexity = calculate_cyclomatic_complexity(repo_dir)
        folder_depth, file_count = analyze_folder_structure(repo_dir)
        dep_count, total_deps = analyze_file_dependencies(repo_dir)
        unique_tech_count = analyze_unique_tech_usage(repo_dir)
        
        repo_details = fetch_repo_details(username, repo_name)
        
        if repo_details is None:
            return None

        metrics = {
            'loc': repo_details['size'] * 1000,  
            'cyclomatic_complexity': cyclomatic_complexity,
            'folder_depth': folder_depth,
            'file_count': file_count,
            'dependencies': total_deps,
            'unique_tech': unique_tech_count,
            'code_quality': (js_complexity + py_complexity + cpp_complexity) / 3
        }

        complexity_score = calculate_complexity_score(metrics)

        return {
            'name': repo_name,
            'html_url': repo_details['html_url'],
            'complexity_score': complexity_score,
            'metrics': metrics,
            'stars': repo_details['stargazers_count'],
            'forks': repo_details['forks_count'],
            'watchers': repo_details['watchers_count'],
            'open_issues': repo_details['open_issues_count']
        }
    finally:
        temp_dir = os.path.join(os.getcwd(), "temp_repos")
        os.makedirs(temp_dir, exist_ok=True)
        try:
            shutil.move(repo_dir, os.path.join(temp_dir, repo_name))
            print(f"Moved {repo_name} to temporary directory.")
        except Exception as e:
            print(f"Failed to move {repo_name}: {e}")
            print("You may need to delete it manually.")

def scrape_github_repositories(username):
    repositories = fetch_github_repositories(username)
    if repositories is None:
        return None

    repo_info_list = []
    for repo in repositories:
        repo_name = repo['name']
        repo_url = repo['clone_url']
        repo_info = analyze_repository_complexity(username, repo_name, repo_url)
        if repo_info:
            repo_info_list.append(repo_info)
    return repo_info_list

def print_sorted_table(repositories):
    # Sort repositories by complexity score in descending order
    sorted_repos = sorted(repositories, key=lambda x: x['complexity_score'], reverse=True)
    
    # Create a rich console
    console = Console()

    # Create a table
    table = Table(title="GitHub Repository Complexity Analysis", show_header=True, header_style="bold magenta")
    
    # Add columns
    table.add_column("Repository", style="cyan", no_wrap=True)
    table.add_column("Complexity Score", justify="right", style="green")
    table.add_column("LOC", justify="right")
    table.add_column("Cyclomatic Complexity", justify="right")
    table.add_column("Folder Depth", justify="right")
    table.add_column("File Count", justify="right")
    table.add_column("Dependencies", justify="right")
    table.add_column("Unique Tech", justify="right")
    table.add_column("Code Quality", justify="right")
    table.add_column("Stars", justify="right", style="yellow")
    table.add_column("Forks", justify="right", style="yellow")
    table.add_column("Watchers", justify="right", style="yellow")
    table.add_column("Open Issues", justify="right", style="red")
    table.add_column("URL", style="blue")

    # Add rows
    for repo in sorted_repos:
        metrics = repo['metrics']
        table.add_row(
            repo['name'],
            f"{repo['complexity_score']:.2f}",
            str(metrics['loc']),
            f"{metrics['cyclomatic_complexity']:.2f}",
            str(metrics['folder_depth']),
            str(metrics['file_count']),
            str(metrics['dependencies']),
            str(metrics['unique_tech']),
            f"{metrics['code_quality']:.2f}",
            str(repo['stars']),
            str(repo['forks']),
            str(repo['watchers']),
            str(repo['open_issues']),
            repo['html_url']
        )

    # Print the table
    console.print(table)

    # Print summary
    console.print(f"\nTotal repositories analyzed: {len(repositories)}", style="bold")
    avg_complexity = sum(repo['complexity_score'] for repo in repositories) / len(repositories)
    console.print(f"Average complexity score: {avg_complexity:.2f}", style="bold")

def analyze_github_profile(username):
    if not username:
        return {"error": "GitHub username is required"}

    repositories = scrape_github_repositories(username)
    if repositories is None:
        return {"error": "Failed to fetch repositories"}

    print_sorted_table(repositories)
    return {"repositories": repositories}

if __name__ == "__main__":
    console = Console()
    username = console.input("[bold cyan]Enter a GitHub username: [/bold cyan]")
    with console.status("[bold green]Analyzing GitHub profile...[/bold green]"):
        result = analyze_github_profile(username)
    if "error" in result:
        console.print(f"[bold red]Error:[/bold red] {result['error']}")