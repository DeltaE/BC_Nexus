# 3. How to Run the Model
**Step-by-Step guideline**
This model file was originally named as [CLEWs model](https://github.com/OSeMOSYS/CLEWs); the code is written in GNU MathProg, a high-level mathematical programming language, yet straightforward enough to be understandable by all kinds of users, expert or not, in linear programming. There are four steps in running the model successfully:
* Step one is to prepare the input files based on the research questions and assumptions
* Step two is preparing the model script
* Step three is to choose a right solver 
* and the last step is to run the solver, collect the results, and visualization

These steps are described in detail below:

### 3.1. Create the SCENARIO folder
> Clone this repository [BC-Nexus-BASE](https://github.com/DeltaE/BC-Nexus-BASE-)

## Step one: INPUT FILE
### 3.2. 'data' preparation
> Find the subfolder 'data' from your cloned repository. Input Data CSV files from here. You should find **69 nos of Csv files** there.

The model code (.txt format) is written in GNU Mathprog, and the CSV data files are required to be formatted in a single data file (.txt) compatible with our model file. For that, we can use an [interfacing tool](http://www.osemosys.org/interfaces.html). For now, we are using [Otoole](https://otoole.readthedocs.io/en/latest/) as the interfacing tool to process input data in the required format. But Otoole has **environment dependencies**, so the most time-saving solution is to use the CONDA environment to use Otoole. 

> Now, install the CONDA environment and then Otoole (follow the instructions [here](https://otoole.readthedocs.io/en/latest/)). Open the **Anaconda Powershell prompt**, then enter the following commands.

	cd <directory of the SCENARIO folder>
	conda activate myenv
	otoole convert csv datafile data data.txt
	
**here, 'myenv' could be default/your customized environment where you install the prerequisite packages to run your codes. To know more about the coda environments, click [here](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html#:~:text=A%20conda%20environment%20is%20a,NumPy%201.6%20for%20legacy%20testing.).

If you completed the aforementioned steps correctly, you should get the **data.txt** file inside the <directory of the SCENARIO folder>. To learn more about the functionality of this syntax [Read this](https://otoole.readthedocs.io/en/latest/functionality.html#core-functionality).

This data file is good to run via [Osemosys-Cloud](www.osemosys-cloud.com). But it needs to be processed further to run on your PC. Inside the cloned repository, find the folder **Scripts** and the python script **preprocess_data.py**.

## Step Two: MODEL
### 3.3.'Model' Preparation
Our Model needs a bit of processing with the script **preprocess_data.py**. 
>The script has four input arguments, i.e. input data file, Processed Input file name suggestion, model file, processed model  file name suggestion
> Open your CMD Terminal and write the following commands >>
	
	cd <location of the model file>
	<python <directory of your SCENARIO folder> <IP data file> <processed data file name> <model File name> <processed model file name>

>> Now that we have the ready-to-run Input data file & the model file generated after step 3, the next thing we need is a solver to generate the Linear Programming (LP) file and to solve the problem to give an optimum solution.

## Step Three: SOLVER
We can solve our model with open-source solvers, e.g., GLP, CBC etc. or with commercial solvers, e.g., CPLEX or so on. Let's try the open-source solvers for now.
	
### 3.4. Install GLP solver (follow the instructions [here](http://www.osemosys.org/uploads/1/8/5/0/18504136/glpk_installation_guide_for_windows10_-_201702.pdf) or [here](https://winglpk.sourceforge.net/#:~:text=Installation,the%20standalone%20solver%20glpsol.exe.)).

## Step Four: SOLVE & RESULTS
### 3.5. Create the Result folder & subfolders
As defined in our result processing script, our GLP solver shall create the results in CSV files inside certain defined directors. Hence, we need to create a folder and subfolders under the SCENARIO folder. A sub-folder named **“res”** and inside it another subfolder **‘csv’**.
	
> We are ready to RUN our model! 
	
### 3.6. Run the model through the GLP solver. Run the Commands for Creating the Linear Programming (LP file) & solving the problem >>
	
	glpsol -m <model file name> -d <data file name> --wlp <LP file name>
	
>> We need the LP file to try on another solver. But you can drop the "--wlp <LP file name>" part if you don't have plans for using other solvers!

Now inside the SCENARIO folder, we got a Results sub-folder, “res” with all results files (CSV) inside the subfolder “csv”. You should get **21 nos. of CSV files.**

## Alternate way of solving by using CBC solver
### 3.7. Install the CBC solver ; instructions [here](https://calliope.readthedocs.io/en/stable/user/installation.html) **need to update this link
Open the Anaconda Powershell prompt, then enter the following commands >>

	CD <directory of the model file>
	conda activate myenv
	cbc <LP file> solve -solu <Solution file name suggestion>

> The CBC solver shall give you a single solution file (.txt). If you need to generate csv files from this solution file, follow this <instruction resource>
