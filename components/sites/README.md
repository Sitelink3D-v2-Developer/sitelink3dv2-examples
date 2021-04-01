# Sitelink3D v2 Create Site Sample
This example demonstrates a basic interaction with the Sitelink3D v2 API to create a site.

Let's get started!

## Step 1. Install Python
An installation of Python is required to run the sample scripts. At time of writing, Python 3.9.1 is the recommended version.

You can download Python 3.9.1 from:
- [Windows](https://www.python.org/downloads/windows/)
- [Linux](https://www.python.org/downloads/source/)

*NOTE: When installing Python, make sure to include it in the system PATH settings*

## Step 2. Install required Python libraries
To install the required Python libraries, open a console in the repository root and;

for Windows users, run:
```
setup.bat
```
or, for Linux users, run:
```
setup.sh
```

## Step 3. Configure new Site Parameters
For Windows users, edit the `site_create.bat` file and for Linux users, edit the `site_create.sh` file to provide the following:

The Sitelink3D v2 environment to create the new Site on. The options are either "prod" or "qa".
```
env=""
```

The Data Centre (dc) to create the new Site.
```
dc=""
```

The Topcon Organization (also known as Owner) to create the Site within.

*NOTE: To obtain this, in a web browser open the Sitelink3D v2 web portal (in the target environment). In the developer console window, copy the result of `SitelinkFrontend.core.store.getState().app.owner.ownerId`*

```bash
owner_id="1234abcd-12ab-12ab-12ab-123456abcdef"
```

Required site settings example:
```bash
site_name="My New Site"
site_lat="-27.4699"
site_lon="153.0252"
site_timezone="Australia/Brisbane"
```

Site contact settings:
```bash
site_contact_name="John Doe"
site_contact_email="john.doe@mynewsite.com"
site_contact_phone="1234567890"
```        

*NOTE: (as of at 29th December 2020) Your client OAuth details do not currently permit the creation of a new Site. You are required to use the JWT provided to you when you log in to the Sitelink3D v2 web portal. In the developer console window, copy the result of `SitelinkFrontend.core.store.getState().app.owner.jwt[0]`*
```bash
jwt=""
```

## Step 4. Run the script
To run the script, open a console in the repository root and;

for Windows users, run:
```
site_create.bat
```
or, for Linux users, run:
```
site_create.sh
```

## Step 5. Inspect the results
You can verify the creation of the new Site within the Sitelink3D v2 web portal.
