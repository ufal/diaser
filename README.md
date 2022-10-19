### Diaser

The dataset is composed as a merge of multiple subdatasets, namely:
 - [MultiWOZ](https://github.com/budzianowski/multiwoz) ), a fully-labeled collection of human-human written conversations spanning over multiple domains and topics. There are 3,406 single-domain dialogues that include booking if the domain allows for that and 7,032 multi-domain dialogues consisting of at least 2 up to 5 domains.
 - [Schema-Guided Dialogue](https://github.com/google-research-datasets/dstc8-schema-guided-dialogue), dataset consists of over 20k annotated multi-domain, task-oriented conversations between a human and a virtual assistant. These conversations involve interactions with services and APIs spanning 20 domains, such as banks, events, media, calendar, travel, and weather.
 - [DSTC 2](https://github.com/matthen/dstc) The corpus was collected using Amazon Mechanical Turk, and consists of dialogs in two domains: restaurant information, and tourist information. Tourist information subsumes restaurant information, and includes bars, cafés etc. as well as multiple new slots. 

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
In particular, you might want to set variables:
 - `SOURCE_ROOT` to specify the directory in which the data are stored.
 - `MULTIWOZ_ROOT,SCHEMA_ROOT,DSCR_ROOT` to specify directories contaning the respective downloaded datasets.
 - `OUT_DIR` to determine output directory with the compiled data.

If you cannot/do not want use the prepared bash script, follow these steps:
 1. Download source data and prepare the directory structure (`prepare\_data.sh`, lines 23-66)
 2. Convert each dataset to our annotation scheme (`prepare\_data.sh`, lines 69-89)
 3. For MultiWOZ, add annotations from dialogue acts (`prepare\_data.sh`, lines 92-100)
 4. Merge the subdatasets (`prepare\_data.sh`, lines 103-108)
 5. Split the dataset into predefined `train,dev,test` sets (`prepare\_data.sh`, lines 111-116)

#### LICENSE
#### Acknowledgements

