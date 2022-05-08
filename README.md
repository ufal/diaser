### Diaser

The dataset is composed as a merge of multiple subdatasets, namely [MultiWOZ](#), [Schema-Guided Dialogue](#) and [DSTC 2](#).
TODO: more description and links

#### Data download and preparation
The scripts expect the data to be located under the specified subdirectories and to have a certain structure.
More specifically, the MultiWOZ and Schema-Guided expect the following structure:
```
/path/to/dataset_name/
	- train/
		- file1.json
		- file2.json
		...
	- dev/
		- file1.json
		...
	- test/
		...
```
This exact structure is contained in the respective dataset repositories from which you can dowload the data.
Specifically:
 - git@github.com:budzianowski/multiwoz.git
 - git@github.com:google-research-datasets/dstc8-schema-guided-dialogue.git

TODO: DSTC2

#### Compiling the data
The preparation scripts are located in the `data_processing/` folder.
There is also a shell script `prepare_data.sh` that process the downloaded data and compile them into the final diaser format.
For this script to work correctly, the respective environment variables need to be set accordingly.

#### Data description

#### License

#### Acknowledgements

