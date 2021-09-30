# Your Coding Journey Starts Here
Welcome to the Topcon Sitelink3D v2 API example code repository.

If you’re after some out-of-the-box code that you can run against our API right now, then you’re in the right place. We know what it’s like starting to code against a new system and its associated API. The burden of getting something simple running can be much harder than expected. That’s where this repository fits in.

Those interested in an overview of Sitelink3D v2 technology and a walkthrough of some of the code contained here are invited to clone our ```sitelink3dv2-api-documentation``` repository [here](https://github.com/Sitelink3D-v2-Developer/sitelink3dv2-api-documentation). 

So make a cup of coffee and let’s get started!

# Repository Structure
The code in this repository is split into two categories:
-	Components.
-	Workflows.

## Components
The Components folder contains examples of individual self-contained operations that can be performed using the API. These examples can be used to learn how basic semantic steps are implemented and what associated parameters and return values are involved. Component examples include:
-	Create a report.
-	Upload a file.
-	Add an operator.

Each component example is implemented in a function that can be included in other code. In this way, components can be grouped together to implement larger workflows.

## Workflows
The Workflows folder contains examples of how more elaborate functionality is implemented by aggregating various component examples together. These examples can be used to learn how our microservices and technologies work together in a broader context. Workflow examples include:
-	Convert a design file into a task able to be viewed on a machine control client.
-	Stream live information about the machines connected to a site using SmartView.
-	Configure a site with the metadata required to run the Topcon Haul App.

# Running the Examples
The steps required to run the example code will vary depending on:
- The selected cloud environment.
- The particular example being run.
- The type of authorization being used.

The following steps describe the complete process required to run the example code from scratch:
1.	Select a cloud environment.
2.	Setup a Topcon account.
3.	Obtain Service Points.
4.	Obtain API credentials.
5.	Configure the python environment.
6.	Navigate to the desired example.
7.	Configure the example.
8.	Run the example.

## Select a Cloud Environment
Sitelink3D v2 is deployed to two isolated environments:
-	QA.
-	Production.

The choice of environment will impact the process of configuring and running example code.

### QA
Our QA environment is a sand box intended for early testing of features before being deployed to production. QA is the recommended environment for new API users. The services deployed to QA are hosted at the following data centers:
- "US".

The QA web portal is available [here](https://qa.sitelink.topcon.com/).

### Production
Our production environment is stable and tested. Production is the recommended environment for API users who have already tested their code in QA. The services deployed to production are hosted at the following data centers:

-	“US”.
-	“EU”.

The production web portal is available [here](https://sitelink.topcon.com/).

## Setup a Topcon Account
New Sitelink3D v2 users will need to perform the following initial tasks for the selected cloud environment:
- Create a Topcon Account.
- Create or Join an Organization.

These tasks are documented in our Topcon Software Developer Network (TSDN) page at https://developer.topcon.com under the ```Get Setup``` link. Account and organization creation is free.

## Obtain Service Points
Sitelink3D v2 usage is charged under a consumption-based model. Consumption is reconciled by the use of Service Points. Service Points have the following properties:

- Preloaded into an Organization.
- Consumed on a per-client, per-day basis.

Service Points are only consumed from an Organization when data is logged to one of its sites using our ```datalogger``` microservice. As none of these examples log such data, you will only need to apply for Service Points when you intend to connect a datalogging client to your site.

Example datalogging clients include:
- The Topcon Haul App for Android and iOS.
- 3DMC.

Logging data to a site allows you to better utilize these examples by:
- Running reports that contain real data.
- Streaming live information about the connected clients.
- Observing weight payloads being sent between machines.

Service Points are required on both our QA and production environments but are charged differently. Service Points for use on QA organizations may be requested from Topcon free of charge [here](https://developer.topcon.com/en/gwWiCQ). Service Points for use on Production organizations may be purchased from our dealer network.

## Obtain API Credentials
The examples support two forms of authorization:
-	OAuth
-	JWT

At least one form of authorization must be obtained for the selected cloud environment.

### OAuth
Using OAuth credentials is recommended due to its convenience and fine grained access control. Credentials are comprised of the following:
-	Client ID.
-	Client Secret.
-	Scope.

Obtaining OAuth credentials is documented in our Topcon Software Developer Network (TSDN) page at https://developer.topcon.com under the ```Get Connected``` link

### JWT
Using a JWT (JSON Web Token) is supported but incurs the following difficulties in the context of these examples:
- JWTs must be obtained manually from a web browser.
- JWTs are not automatically refreshed on expiration.
- No fine grained access control is possible.

Obtaining a JWT is achieved with the following process:
1. Log in to the Sitelink3D v2 web portal as appropriate for the selected cloud environment.
2. Select the desired organization and site.
3. Press F12 in your Chrome browser to open a console.
4. Type in the following command ``` SitelinkFrontend.core.store.getState().app.owner.jwt[0]``` to obtain the JWT.

The JWT returned will be the one in use by the browser and will allow all operations that the signed in user is capable of.

## Configure the Python Environment
The code in this repository is written and tested against Python 3.9. You can download Python from:
- [Windows](https://www.python.org/downloads/windows/)
- [Linux](https://www.python.org/downloads/source/)

Dependencies can be installed by running the ```python_setup.bat``` or ```python_setup.sh``` top level script in this repository as appropriate for your system. These scripts require PIP to be available in the system path.

For Windows users, run:
```
python_setup.bat
```
For Linux users, run:
```
python_setup.sh
```

## Navigate to the Desired Example
Browse the ```components``` and ```workflows``` folders in this repository. Select an example that best fits your needs and open that directory in a command line or in your IDE console.

## Configure the Example
Every python example in this repository is accompanied by a Windows batch and Linux shell wrapper script. Although each example can be run directly from the python file with the appropriate command line arguments, the wrapper scripts allow easy configuration and execution of their associated python file. 

Before running your selected example, its associated wrapper script must first be configured with certain settings. For Windows users, edit the `.bat` file and for Linux users, edit the `.sh` file to provide the required configuration. Each file may require different configuration depending on the purpose of the example but the following is typical:

### Cloud Environment
Enter the cloud environment selected earlier in this process. This environment should already have an organization associated with it. Valid options are:
- "prod".
- "qa".
```
set env=""
```

### Owner Identifier
Some examples require an owner identifier. This will be the case when operations are targeted at the owner of a site rather than a site itelf. Examples include:
- Creating a site.
- Listing existing sites.
 
Obtaining an owner identifier is achieved with the following process:
1. Log in to the Sitelink3D v2 web portal as appropriate for the selected cloud environment.
2. Select the desired organization.
3. Press F12 in your Chrome browser to open a console.
4. Type in the following command ```SitelinkFrontend.core.store.getState().app.owner.ownerId``` to obtain the owner identifier.

```
set owner_id=""
```

### Site Identifier
Most examples require the 64 alpha-numeric identifier string for the target site. Obtaining a site identifier is achieved with the following process:
1. Log in to the Sitelink3D v2 web portal as appropriate for the selected cloud environment.
2. Select the desired organization and site.
3. Click on the site name to the left of the top banner to expand the site menu.
4. Click on the Site Information menu item to display the Site Information dialog.
5. Copy the displayed identifier string.
```
set site_id=""
```

### Data Center
When sites are created they are assigned to a data center. Once assigned, the data center cannot be changed. Obtaining the data center is achieved with the following process:
1. Log in to the Sitelink3D v2 web portal as appropriate for the selected cloud environment.
2. Select the desired organization and site.
3. Click on the site name to the left of the top banner to expand the site menu.
4. Click on the Site Information menu item to display the Site Information dialog.
5. Observe the site's data center assignment.

Note that the syntax displayed on the Site Information dialog differs from that required in the wrapper script. The options for the latter are:
- “us”.
- “eu”.
```
set dc=""
```

### Authorization
Enter either the OAuth credentials or JWT authorization appropriate for the selected cloud environment. If both authorization types are provided, the examples will preference the JWT. 

```
set jwt=""
rem # - or -
set oauth_id=""
set oauth_secret=""
set oauth_scope=""
```

## Run the Example
Run the configured wrapper script. For example, to run the site creation example on Windows:
```
site_create.bat
```
and on Linux:
```
site_create.sh
```

# Examining the Console Output
## Log Level
The level of detail in the script output can be changed by altering the logging configuration in each python file. The default logging level is INFO. By setting to DEBUG, additional detail useful for development can be observed. The appropriate line will look like:
``` arg_parser = add_arguments_logging(arg_parser, logging.INFO)```
## Output Format
Each line of console output is formatted with the date, time, file, log level and function followed by the log message as follows:
```console
> 2021-09-16 14:21:51,274 site_create INFO main:  
```
The first output from each example is a line that confirms the example being run, the selected cloud environment and any other useful settings relevant to the particular example as follows:
```console
2021-09-16 14:20:49,468 site_create INFO main:   Running site_create.py for server=https://us-qa-api.sitelink.topcon.com:443 dc=us owner=ce235e5e-6d87-4a84-80f2-0e56b137a132
```

# Getting Help
If you require any assistance on your Sitelink3D v2 API journey, please contact us [here](mailto:sitelink3d-api-support@topcon.com).