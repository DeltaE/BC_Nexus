# BC-CLEWS-Model data processing with Otoole

This branch has the resources for input data and result data processing with [Otoole](https://otoole.readthedocs.io/en/latest/index.html).

Please go through this [documentation](https://otoole.readthedocs.io/en/latest/install.html) to learn about installation, usage and functionality of otoole

## Otoole Configuration File Setup
Go through Otoole [Setup documentation guideline](https://otoole.readthedocs.io/en/latest/functionality.html#setup) to create the config.yaml file required to use otoole.

### Updates:
The default configuration file **doesn't include** the following paramters:  
* __TechnologyActivityIncreaseByModeLimit__  
* __TechnologyActivityDecreaseByModeLimit__  
* __TechnologyActivityByModeUpperLimit__  
* __TechnologyActivityByModeLowerLimit__  

The updated file has been renamed as __[config_updated.yaml](https://github.com/DeltaE/BC-CLEWS-Model/blob/Datapackage_otoole/config_files/config_updated.yaml)__. 
Check user [configuration file documentation](https://otoole.readthedocs.io/en/latest/data.html#user-configuration-file) to know about the format.
> Parameter Names longer than 31 characters require a short_name field due to character limits on excel sheet names. otoole will raise an error if a short_name is not provided in these instances.
