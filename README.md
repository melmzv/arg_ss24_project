# Accounting Reading Group - Assignment III: Earnings Management and Investor Protection

## Adopting the Open Science Workflow and TRR 266 Template for Reproducible Empirical Accounting Research 

This repository provides an infrastructure for an open science-oriented empirical project, specifically targeted at the empirical accounting research community. It features a project exploring the relationship between earnings management and investor protection across different countries. The project requires access to the research platform WRDS, which provides access to a variety of different datasets.

This final assignment requires the comprehensive application of all skills learned and feedback received from previous assignments, making it a more complex project workflow. The task involves accessing and retrieving data from the Worldscope Database through WRDS, which adds complexity as it requires both understanding WRDS and writing scripts to pull the data. Similarly to Assignment I, reproducing a table from a seminal paper necessitates a deep understanding of the paper’s methodology and thorough attention to detail to match the results. Additionally, the project output includes  documentation of the steps and explicit assumptions made. The output paper and presentation documents present the findings, compare them with the paper key results and discuss any differences observed.

Even if you are not specifically interested in earnings management (who wouldn’t be?) or do not have access to WRDS Databases, the codebase provided in this repository will give you a clear understanding of how to structure a reproducible empirical project. The template and workflow used here are designed to ensure transparency and reproducibility, making it a valuable resource for any empirical accounting research project.

The default branch, `only_python`, is a stripped-down version of the template containing only the Python workflow. This branch was cloned from the TRR 266 Template for Reproducible Empirical Accounting Research (TREAT) repository, focusing solely on the Python workflow.

### Where do I start?

You start by setting up few tools on your system: 

- If you are new to Python, follow the [Real Python installation guide](https://realpython.com/installing-python/) that gives a good overview of how to set up Python on your system.

- Additionally, you will also need to setup an Integrated Development Environment (IDE) or a code editor. We recommend using VS Code, please follow the [Getting started with Python in VS Code Guide](https://code.visualstudio.com/docs/python/python-tutorial).

- You wll also need [Quarto](https://quarto.org/), a scientific and technical publishing system used for documentation pursoses of this project. Please follow the [Quarto installation guide](https://quarto.org/docs/get-started/) to install Quarto on your system. I recommend downloading the Quarto [Extension](https://marketplace.visualstudio.com/items?itemName=quarto.quarto) for enhanced functionality, which streamlines the workflow and ensures professional documentation quality for this project.

- Finally, you will also need to have `make` installed on your system, if you want to use it. It reads instructions from a `Makefile` and helps automate the execution of these tasks, ensuring that complex workflows are executed correctly and efficiently.
    - For Linux users this is usually already installed. 
    - For MacOS users, you can install `make` by running `brew install make` in the terminal. 
    - For Windows users, there are few options to install `make` and they are dependent on how you have setup your system. For example, if you have installed the Windows Subsystem for Linux (WSL), you can install `make` by running `sudo apt-get install make` in the terminal. If not you are probably better of googling how to install `make` on Windows and follow a reliable source.


Next, explore the repository to familiarize yourself with its folders. You will quickly see that there are three folders that have files in them:

- `config`: This directory holds configuration files that are being called by the program scripts in the `code` directory. We try to keep the configurations separate from the code to make it easier to adjust the workflow to your needs.

- `code`: This directory holds program scripts that are being called to download data from WRDS, prepare the data, run the analysis and create the output files (a paper and a presentation, both PDF files).

- `data`: A directory where data is stored. You will see that it again contains sub-directories and a README file that explains their purpose. You will also see that in the `external` sub-directory there are two data files. Again, the README file explains their content.

- `doc`: Here you will find two Quarto files containing text and program instructions that will become our paper and presentation, by rendering them through the R markdown process and LaTeX.

- `info`: This is a folder that can store additional documentation. In our case you will find a RMarkdown file that introduces our TRR 266-themed ggplot theme.

You also see an `output` directory but it is empty. Why? Because the output is created locally on your computer.


### How do I create the output?

Assuming that you have WRDS access, Python, Vs Code, Quarto and make installed, this should be relatively straightforward. Refer to the setup instructions in section [above](#where-do-i-start).

> [!IMPORTANT]
> To access the financial data needed for this project, use the Worldscope Database available through the WRDS (Wharton Research Data Services) platform. WRDS acts as a gateway, offering tools for data extraction and analysis, and consolidates multiple data sources for academic and corporate research.
> In order to access the Worldscope Database through WRDS, complete this [form](https://wrds-www.wharton.upenn.edu/register/), if not yet registered for WRDS. 
> Ensure that you create an account with your institutional (university) login. If you are from Humboldt-Universität zu Berlin, contact the University Library to get your account request approved. 
> After setting up Two-factor authentication (2FA) and accepting the terms of use, you will be set to go with WRDS Databases.

1. Click on the `Use this template` button on the top right of the repository and choose `Create a new repository`. Give the repository a name, a description and choose whether it should be public or private. Click on `Create repository`.
2. You can now clone the repository to your local machine. Open the repository in Vs Code and open a new terminal.
3. It is advisable to create a virtual environment for the project. You can do this by running `python -m venv venv` in the terminal. This will create a virtual environment in the `venv` directory. You can activate the virtual environment by running `source venv/bin/activate` on MacOS or Linux or `.\venv\Scripts\activate` on Windows. You can deactivate the virtual environment by running `deactivate`.
4. With an active virtual environment, you can install the required packages by running `pip install -r requirements.txt` in the terminal. This will install the required packages for the project.
5. Copy the file _secrets.env to secrets.env in the project main directory. Edit it by adding your WRDS credentials.
> [!NOTE]
> Note that inability to see the password while typing is standard behavior for security reasons. When prompted, type your password even though it won’t be displayed and press Enter. When WRDS prompts you to create a .pgpass file, it’s asking if you want to store your login credentials for easier future access. Answer ‘y’ to create the file now and follow the instructions, or ‘n’ if you prefer to enter your password each time or create the file manually later.

> [!TIP]
> I have included an intermediate check step using the `code/python/test_wrds_connection.py` file to ensure that WRDS access is secure and functional before running the main program script.
6. Run 'make all' either via the console. I use the Makefile Tools extension in VS Code to run the makefile. This will execute the makefile and generate the necessary output files.
7. Eventually, you will be greeted with the two files in the output directory: "paper.pdf" and "presentation.pdf". Congratulations! You have successfully used an open science resource and reproduced our "analysis". Now modify it and make it your own project!

### Setting up for Reproducible Empirical Research

To start a new reproducible project on earnings management and investor protection based on this repo, follow these steps: 
1. Clone the repository by clicking “Use this Template” at the top of the file list on GitHub. 
2. Remove any files that you don’t need for your specific project. 
3. Over time, you can fork this repository and customize it to develop a personalized template that fits your workflow and preferences.

This repository contains the files that TRR 266 members might find particularly useful: 
- The file `code/python/theme_trr.py` features a ggplot theme that makes it easy to generate visuals that comply to the TRR 266 style guide. But ggplot in python is not yet polished and does not have the same level of quality as in R. 
- The RMarkdown file in `info` takes you through the process. With the `doc/beamer_theme_trr266.sty` you can beef up your Quarto based beamer presentations to the fancy TRR design. 
- Finally, the file `code/python/pull_wrds_data.py` is useful if you want to learn how to download WRDS data directly from python.


### Licensing

This project particularly utilizes the template used in collaborative research center [TRR 266 Accounting for Transparency](https://accounting-for-transparency.de), that is centered on workflows that are typical in the accounting and finance domain.

The repository is licensed under the MIT license. Due to reusing a part of the example code from the treat repository, e.g. code for pulling data from WRDS, I would like to give the following credit:

```
This repository was built based on the ['treat' template for reproducible research](https://github.com/trr266/treat).
```

### References

:bulb: If you’re new to collaborative workflows for scientific computing, here are some helpful texts:

- Christensen, Freese and Miguel (2019): Transparent and Reproducible Social Science Research, Chapter 11: https://www.ucpress.edu/book/9780520296954/transparent-and-reproducible-social-science-research
- Gentzkow and Shapiro (2014): Code and data for the social sciences:
a practitioner’s guide, https://web.stanford.edu/~gentzkow/research/CodeAndData.pdf
- Wilson, Bryan, Cranston, Kitzes, Nederbragt and Teal (2017): Good enough practices in scientific computing, PLOS Computational Biology 13(6): 1-20, https://doi.org/10.1371/journal.pcbi.1005510


