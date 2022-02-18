# DashWasher
Network analysis of Dash blockchain


## Structure
The repository is organized in the following subfolders:
- **analysis**: it contains the scripts to create and analyze the transactions graph and the random graph.
- **results**: the folder in which results of analysis scripts are saved.
- **download**: it contains the scripts to download transactions data.
- **data**: the folder in which the downloaded data are saved.
- **utilities**: data handling scripts.

In the root folder there is a bash script to automatically run the code, as well as two configurations files for the script.

## Usage
First, change the configuration file *config.json* as you wish. For example:

```json
{
    "directed_graph" : true,        
    "weighted_graph" : false,
    "clustering" : true,
    "fraction_samples" : [1.0],
    "num_cpus" : 0,
    "formula_ASPL_rnd": true,
}
```
in which num_cpus is associated to the multiprocessing and it can take two special values: 0 for all available cpus, -1 for all but one.

Then you can simply run the bash script *main.sh* to download and analyze the transactions of a certain day:
```bash
bash main.sh -d 2021-01-01
```
