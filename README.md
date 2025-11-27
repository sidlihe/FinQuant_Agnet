<p align="center">
    <img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" align="center" width="30%">
</p>
<p align="center"><h1 align="center">FINQUANT AGENT</h1></p>
<p align="center">
	<em><code>Terminal-first Screener + Gemini research copilot</code></em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/sidlihe/FinQuant_Agnet.git?style=default&logo=opensourceinitiative&logoColor=white&color=00e0ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/sidlihe/FinQuant_Agnet.git?style=default&logo=git&logoColor=white&color=00e0ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/sidlihe/FinQuant_Agnet.git?style=default&color=00e0ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/sidlihe/FinQuant_Agnet.git?style=default&color=00e0ff" alt="repo-language-count">
</p>
<p align="center"><!-- default option, no dependency badges. -->
</p>
<p align="center">
	<!-- default option, no dependency badges. -->
</p>
<br>

##  Table of Contents

- [ Overview](#-overview)
- [ Features](#-features)
- [ Project Structure](#-project-structure)
  - [ Project Index](#-project-index)
- [ Getting Started](#-getting-started)
  - [ Prerequisites](#-prerequisites)
  - [ Installation](#-installation)
  - [ Usage](#-usage)
  - [ Testing](#-testing)
- [ Project Roadmap](#-project-roadmap)
- [ Contributing](#-contributing)
- [ License](#-license)
- [ Acknowledgments](#-acknowledgments)

---

##  Overview

FinQuant Agent marries deterministic Screener.in scraping, yfinance technicals, and Gemini reasoning to deliver human-grade trading advice. Enter a casual stock name (e.g., “niva bupa”), the agent resolves the exact Screener slug + NSE ticker, scrapes fundamentals, saves everything to disk, and finally asks Gemini to craft a personalized action plan depending on whether you already own the stock.

---

##  Features

- Deterministic alias resolver that maps colloquial names to Screener + NSE tickers.
- Headless Selenium scraper that exports structured JSON snapshots per company.
- yfinance-based technical summary with volatility stats and markdown export.
- Personalized Gemini verdict that adapts to the user’s holding status.
- CLI workflow that logs everything, persists outputs, and is resilient to transient failures.

---

##  Project Structure

```text
Gemini-Retail-Agent/
├── main.py
├── outputs/
├── info_json/
├── requirement.txt
└── src
    ├── scraper/
    ├── tools.py
    ├── workflow.py
    ├── nodes.py
    ├── config.py
    ├── state.py
    └── logger.py
```


###  Project Index
<details open>
	<summary><b><code>FINQUANT_AGNET.GIT/</code></b></summary>
	<details> <!-- __root__ Submodule -->
		<summary><b>__root__</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/sidlihe/FinQuant_Agnet.git/blob/master/requirement.txt'>requirement.txt</a></b></td>
				<td><code>Runtime dependencies</code></td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/sidlihe/FinQuant_Agnet.git/blob/master/main.py'>main.py</a></b></td>
				<td><code>Interactive CLI entrypoint</code></td>
			</tr>
			</table>
		</blockquote>
	</details>
	<details> <!-- src Submodule -->
		<summary><b>src</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/sidlihe/FinQuant_Agnet.git/blob/master/src/logger.py'>logger.py</a></b></td>
				<td><code>Central logging configuration</code></td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/sidlihe/FinQuant_Agnet.git/blob/master/src/config.py'>config.py</a></b></td>
				<td><code>Env + directory helpers</code></td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/sidlihe/FinQuant_Agnet.git/blob/master/src/workflow.py'>workflow.py</a></b></td>
				<td><code>LangGraph assembly</code></td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/sidlihe/FinQuant_Agnet.git/blob/master/src/tools.py'>tools.py</a></b></td>
				<td><code>Deterministic tools + helpers</code></td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/sidlihe/FinQuant_Agnet.git/blob/master/src/nodes.py'>nodes.py</a></b></td>
				<td><code>Gemini node + bindings</code></td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/sidlihe/FinQuant_Agnet.git/blob/master/src/state.py'>state.py</a></b></td>
				<td><code>LangGraph AgentState</code></td>
			</tr>
			</table>
		</blockquote>
	</details>
</details>

---
##  Getting Started

###  Prerequisites

Before getting started with FinQuant_Agnet.git, ensure your runtime environment meets the following requirements:

- **Programming Language:** Python


###  Installation

```sh
git clone https://github.com/sidlihe/FinQuant_Agnet.git
cd FinQuant_Agnet.git
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
# .\venv\Scripts\activate
pip install -r requirement.txt
cp .env.example .env  # set GOOGLE_API_KEY and optional CHROMEDRIVER_PATH
```

###  Usage

```sh
python main.py
```

1. Type any Indian stock/casual alias when prompted.
2. Confirm the detected Screener + NSE ticker (override if needed).
3. Answer whether you already own the stock.
4. Read/save the personalized verdict in `outputs/`; raw JSON goes to `info_json/`.

###  Testing

Smoke check imports and Selenium wiring:

```sh
python -m compileall src
python src/tools.py  # optional: runs the stock verdict tool in debug mode
```

---
##  Project Roadmap

- [X] **`Task 1`**: <strike>Implement feature one.</strike>
- [ ] **`Task 2`**: Implement feature two.
- [ ] **`Task 3`**: Implement feature three.

---

##  Contributing

- **💬 [Join the Discussions](https://github.com/sidlihe/FinQuant_Agnet.git/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/sidlihe/FinQuant_Agnet.git/issues)**: Submit bugs found or log feature requests for the `FinQuant_Agnet.git` project.
- **💡 [Submit Pull Requests](https://github.com/sidlihe/FinQuant_Agnet.git/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/sidlihe/FinQuant_Agnet.git
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/sidlihe/FinQuant_Agnet.git/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=sidlihe/FinQuant_Agnet.git">
   </a>
</p>
</details>

---

##  License

This project is protected under the [SELECT-A-LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

##  Acknowledgments

- List any resources, contributors, inspiration, etc. here.

---
