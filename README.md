# Sitelink3D v2 API Sample

## TLDR;

This repository contains sample scripts for both Windows and Linux operating systems which demonstrate basic interactions with the Sitelink3D v2 API. Browse the folders for an example to run, add configuration to the associated ```.bat``` or ```.sh```file and then run it.

Let's get started!

## Some More Background

This repository is broken into two sections as follows:

* Components.
* Workflows.

The components folder provides examples of self-contained, semantically structured functionality. Those interested in specific, isolated functionality such as uploading a file or enumerating reports at a site as part of a larger body of work can browse the components folder for examples of the the minimum required work. 

Shell and batch scripts are provided with each component example for convenience. These supporting files include the required configuration and call a main function that runs the example code without superfluous context.

The workflows folder provides examples of more elaborate functionality achieved by chaining the component functions together. Those interested in implementing larger bodies of work such as creating a Task from a design file can browse the workflows folder for examples of how components are aggregated to achieve such outcomes. 

As with the components folder, shell and batch scripts are provided with each workflow example for convenience.


## Step 1. Install Python
An installation of Python is required to run the sample scripts. At time of writing, Python 3.9.1 is the recommended version.

You can download Python 3.9.1 from:
- [Windows](https://www.python.org/downloads/windows/)
- [Linux](https://www.python.org/downloads/source/)

*NOTE: When installing Python, make sure to include it in the system PATH settings*

## Step 2. Install required Python Libraries
If required, prerequisite Python libraries can be installed by opening a console in the repository root and;

for Windows users, run:
```
python_setup.bat
```
or, for Linux users, run:
```
python_setup.sh
```

## Step 3. Find and Configure the Desired Example
Navigate the components and workflows folders described in the Background section above and;

for Windows users, edit the `.bat` file and for Linux users, edit the `.sh` file to provide the required configuration. Each file may require different configuration depending on the purpose of the example but the following is typical:

The Sitelink3D v2 environment that the target Site resides on. The options are either "prod" or "qa".
```
env=""
```

The 64 alpha-numeric ID string of the target Site. This can be found in `the Sitelink3D v2 web portal -> Site menu -> Site Information` menu.
```
site_id=""
```

The Data Centre (dc) that the target Site was created on.
```
dc=""
```

Your client OAuth details provided by the Sitelink3D v2 support team.
For more information, please refer to the `Sitelink3D v2 -> Integrating -> Getting Started` documentation on the [Topcon Software Developer Network](https://developer.topcon.com/en/) site.
```
oauth_id=""
oauth_secret=""
oauth_scope=""
```

## Step 4. Run the script
To run the script, open a console in the repository root and;

for Windows users, run:
```
run-report.bat
```
or, for Linux users, run:
```
run-report.sh
```

## Step 5. Inspect the results
Results from running the script can be inspected in the `root\results` folder, or alternatively within the Sitelink3D v2 web portal within the `Report Manager`.