# GitHub Repository Complexity Analyzer

## Overview

The GitHub Repository Complexity Analyzer is a Python tool designed to analyze and compare the complexity of GitHub repositories. It fetches repository data, performs various complexity analyses, and presents the results in a visually appealing table format.

## Features

- Fetches public repositories for a given GitHub username
- Analyzes repositories for various complexity metrics:
  - Lines of Code (LOC)
  - Cyclomatic Complexity
  - Folder Structure Depth
  - File Count
  - File Dependencies
  - Unique Technology Usage
  - Code Quality (based on static analysis)
- Calculates an overall complexity score
- Presents results in a color-coded, sorted table
- Provides a summary of the analysis

## Requirements

- Python 3.6+
- Git
- ESLint (for JavaScript analysis)
- PyLint (for Python analysis)
- CppCheck (for C++ analysis)
- Radon (for cyclomatic complexity calculation)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/github-repo-complexity-analyzer.git
   cd github-repo-complexity-analyzer
   ```

2. Install the required Python packages:
   ```
   pip install requests rich radon
   ```

3. Ensure you have the following tools installed and accessible from the command line:
   - Git
   - ESLint
   - PyLint
   - CppCheck

## Usage

Run the script from the command line:

```
python app.py
```

You will be prompted to enter a GitHub username. The script will then analyze all public repositories for that user and display the results in a table.

## Output

The script outputs a color-coded table with the following information for each repository:

- Repository Name
- Complexity Score
- Lines of Code (LOC)
- Cyclomatic Complexity
- Folder Depth
- File Count
- Dependencies
- Unique Technologies Used
- Code Quality Score
- Stars
- Forks
- Watchers
- Open Issues
- Repository URL

The table is sorted by the Complexity Score in descending order, with the most complex repositories at the top.

## Limitations

- The tool relies on external static analysis tools (ESLint, PyLint, CppCheck) which must be installed separately.
- The complexity score is a composite metric and may not perfectly reflect the true complexity of a repository in all cases.
- The tool only analyzes public repositories.
- Large repositories may take a significant amount of time to analyze.

## Contributing

Contributions to improve the GitHub Repository Complexity Analyzer are welcome. Please feel free to submit pull requests or open issues to suggest improvements or report bugs.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and analytical purposes only. It should not be used as the sole metric for judging the quality or complexity of a software project. Always consider multiple factors and contexts when evaluating code repositories.
