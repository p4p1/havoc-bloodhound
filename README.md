# havoc-bloodhound
A GUI wrapper inside of Havoc to interact with bloodhound CE

![image](https://github.com/p4p1/havoc-bloodhound/assets/19672114/f12caa80-bf6d-460a-8c00-8a16fd941dda)

## Install

I recommend installing this module through the havoc store only since the module is dependant on beeing located inside of the data/extentions folder inside of havoc:
![image](https://github.com/p4p1/havoc-bloodhound/assets/19672114/8ae014f8-8f56-435c-b83a-92247c6e6ec1)


## Setup

You will need an instance of BloodHound Community Edition more on that [here](https://support.bloodhoundenterprise.io/hc/en-us/articles/17715215791899-Getting-started-with-BloodHound-Community-Edition).
You will then need to download your collector from the web interface inside of the Gear > Download Collectors:

![image](https://github.com/p4p1/havoc-bloodhound/assets/19672114/52d86158-c79c-4603-a260-8dbc74925bb4)

From there inside of the module you can specify it inside of Bloodhound > SharpHound:

![image](https://github.com/p4p1/havoc-bloodhound/assets/19672114/6ce1722b-79da-49ba-896d-b671799ece80)

Make sure you save your changes for persistance. You will then need to generate API keys inside of bloodhound CE
and supply them to the script through BloodHound > Settings:

![image](https://github.com/p4p1/havoc-bloodhound/assets/19672114/3d0c7f40-4870-40bc-92af-393fe83bce31)
![image](https://github.com/p4p1/havoc-bloodhound/assets/19672114/5f90bdef-cb70-4bc2-8185-3d0b922d33f6)

Like before make sure you save everything for persistance.

## Usage

From here you can then use the bloodhound command inside of havoc to run your collector and upload the zip file after your downloaded it.
Note that the arguments of the collector are defined inside of the SharpHound menu.


```
02/01/2024 22:26:13 [leo] Demon » help bloodhound

 - Command       :  bloodhound
 - Description   :  A command to manage bloodhound related things

  Command                   Description      
  ---------                 -------------     
  collect                   Run the Bloodhound collector on the target machine (aka: SharpHound)
  upload                    Upload the zip file to the api

02/01/2024 22:26:17 [leo] Demon » help bloodhound upload

 - Command       :  bloodhound upload
 - Description   :  Upload the zip file to the api
 - Example       :  bloodhound upload /data/ c:\file\number_BloodHound.zip
 - Required Args :  2
```

![image](https://github.com/p4p1/havoc-bloodhound/assets/19672114/2b6aae53-a6b1-41f4-a87c-740a8360ccea)
