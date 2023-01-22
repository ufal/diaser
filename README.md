### Diaser

The dataset is composed as a merge of multiple subdatasets with a unified format, namely:
 - [MultiWOZ](https://github.com/budzianowski/multiwoz), a fully-labeled collection of human-human written conversations spanning over multiple domains and topics. There are 3,406 single-domain dialogues that include booking if the domain allows for that and 7,032 multi-domain dialogues consisting of at least 2 up to 5 domains.
 - [Schema-Guided Dialogue](https://github.com/google-research-datasets/dstc8-schema-guided-dialogue), dataset consists of over 20k annotated multi-domain, task-oriented conversations between a human and a virtual assistant. These conversations involve interactions with services and APIs spanning 20 domains, such as banks, events, media, calendar, travel, and weather.
 - [DSTC 2](https://github.com/matthen/dstc) The corpus was collected using Amazon Mechanical Turk, and consists of dialogs in two domains: restaurant information, and tourist information. Tourist information subsumes restaurant information, and includes bars, cafés etc. as well as multiple new slots. 
 * [CamRest676](https://www.repository.cam.ac.uk/handle/1810/260970) This is a small restaurant corpus of 676 dialogues collected using Amazon Mechanical Turk.


Please **see our LREC 2022 paper** [(Hudeček et al., A Unifying View On Task-oriented Dialogue Annotation)](https://aclanthology.org/2022.lrec-1.137/) for a detailed description of the data.


### Prebuilt dataset

You can **download the prebuilt data directly on the [Releases page](https://github.com/ufal/diaser/releases)**.
The corresponding ontology is stored directly under [data/global_ontology.json](data/global_ontology.json)


### Building the dataset from original sources

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
 - MultiWOZ: git@github.com:budzianowski/multiwoz.git
 - Schema-guided Dialogue: git@github.com:google-research-datasets/dstc8-schema-guided-dialogue.git
 * DSTC2: git@github.com:matthen/dstc.git
 * CamRest676: https://www.repository.cam.ac.uk/handle/1810/260970

#### Compiling the data

The preparation scripts are located in the `data_processing/` folder.
The main entry point is the shell script `prepare_data.sh` that is able to download the data from their sources, process the downloaded data and compile them into the final diaser format.
For this script to work correctly, the following environment variables need to be set accordingly (see the script code, defaults are provided but you might want to adjust them):
 - `SOURCE_ROOT` to specify the directory in which the data are stored.
 - `MULTIWOZ_ROOT,SCHEMA_ROOT,DSCR_ROOT` to specify directories contaning the respective downloaded datasets.
 - `OUT_DIR` to determine output directory with the compiled data.

If you cannot/do not want use the prepared bash script, follow these steps:
 1. Download source data and prepare the directory structure (`prepare_data.sh`, lines 23-66)
 2. Convert each dataset to our annotation scheme (`prepare_data.sh`, lines 69-89)
 3. For MultiWOZ, add annotations from dialogue acts (`prepare_data.sh`, lines 92-100)
 4. Merge the subdatasets (`prepare_data.sh`, lines 103-108)
 5. Split the dataset into predefined `train,dev,test` sets (`prepare_data.sh`, lines 111-116)

#### LICENSE

The code is licensed under the MIT license.
The released data is licensed under the GPL 3.0 license (to be compatible with the licenses for all original datasets).

#### Acknowledgements

If you use this data, please cite the following paper:
```
@inproceedings{hudecek-etal-2022-unifying,
    title = "A Unifying View On Task-oriented Dialogue Annotation",
    author = "Hude{\v{c}}ek, Vojt{\v{e}}ch  and Schaub, Leon-paul  and Stancl, Daniel  and Paroubek, Patrick  and Du{\v{s}}ek, Ond{\v{r}}ej",
    booktitle = "Proceedings of the Thirteenth Language Resources and Evaluation Conference",
    month = jun,
    year = "2022",
    address = "Marseille, France",
    publisher = "European Language Resources Association",
    url = "https://aclanthology.org/2022.lrec-1.137",
    pages = "1286--1296",
}
```
