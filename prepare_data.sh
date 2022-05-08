set -x

# 1. Define global variables and prepare directory environment
# a path to the directory that contains directories with source data
SOURCE_ROOT=`pwd`/source_diaser_data
# path to the directory that contains MultiWOZ data
MULTIWOZ_ROOT=${SOURCE_ROOT}/multiwoz/data/MultiWOZ_2.2/
# path to the directory that contains Schema-Guided data
SCHEMA_ROOT=${SOURCE_ROOT}/dstc8-schema-guided-dialogue
# path to the directory that contains combined DSTC2 and CamRest676 data and corresponding database
DSCR_ROOT=${SOURCE_ROOT}/dscr
# path to the directory thaht contains the data for onthology unification across all the datasets
ONTGY_ROOT=data
# output directory that contains the compiled dataset
OUT_DIR=diaser-data
# location of temporary processing files
TMP_DIR=/tmp/data

mkdir -p ${SOURCE_ROOT}
mkdir -p ${TMP_DIR}/{train,dev,test} ${OUT_DIR} ${OUT_DIR}/fixed_split

# 2. Download source data - prepare the source data used for the creation of DIASER
PROJECT_ROOT=$(pwd -P)
cd $SOURCE_ROOT

# Multiwoz 2.2
[[ ! -d multiwoz ]] && git clone git@github.com:budzianowski/multiwoz.git
(cd multiwoz/data; [[ ! -d MultiWOZ_2.1 ]] && unzip MultiWOZ_2.1.zip)
# Schema Guided Dialogue
[[ ! -d dstc8-schema-guided-dialogue ]] && git clone git@github.com:google-research-datasets/dstc8-schema-guided-dialogue.git
# CamRest 676
if [[ ! -d CamRest676 ]]
then
	wget https://www.repository.cam.ac.uk/bitstream/handle/1810/260970/CamRest676.zip
	unzip CamRest676.zip
	mkdir -p dscr
	# remove copyright from CamRest676 data so that they can be parsed with python
	for f in CamRest676/{CamRest676.json,CamRestDB.json,CamRestOTGY.json} ; do
		tail -n +6 ${f} > ${f}.tmp && mv ${f}.tmp ${f}
	done
	cp CamRest676/{CamRestDB.json,CamRestOTGY.json} dscr
	# clean
	rm -rf __MACOSX/
	rm CamRest676.zip
fi
# DSTC2
if [[ ! -d dstc2 ]]
then
	for split in traindev test ; do
		[[ ! -d dstc2/${split} ]] && wget https://github.com/matthen/dstc/releases/download/v1/dstc2_${split}.tar.gz && [[ ! -d dstc2_${split} ]] && mkdir -p dstc2_${split} && tar -xf dstc2_${split}.tar.gz -C dstc2_${split}
		mkdir -p dstc2/${split}
		mv dstc2_${split}/data/*  dstc2/${split}
		# clean
		rm dstc2_${split}.tar.gz
		rm -rf dstc2_${split}
	done
fi

cd $PROJECT_ROOT

# 3. Create DIASER data
# first prepare camresr data
python -m data_processing.converter \
        --camrest-path ${SOURCE_ROOT}/CamRest676/CamRest676.json \
        --dstc-dir ${SOURCE_ROOT}/dstc2 \
	--output-file ${DSCR_ROOT}/dstccamrest.json

# converts the data into our annotation structure
for split in dev train test ; do
	python -m data_processing.process_schema_guided \
		--data_dir ${MULTIWOZ_ROOT} \
		--dataset multiwoz \
		--compress \
		--split ${split} \
		--output_file ${TMP_DIR}/${split}/${split}_mw.json
	python -m data_processing.process_schema_guided \
		--data_dir ${SCHEMA_ROOT} \
		--dataset schema \
		--compress \
		--split ${split} \
		--output_file ${TMP_DIR}/${split}/${split}_schema.json
done
python -m data_processing.process_schema_guided \
	--data_dir ${DSCR_ROOT} \
	--dataset dstcamrest \
	--compress \
	--output_file ${TMP_DIR}/train/train_dscr.json \
	--db ${DSCR_ROOT}/CamRestDB.json \
	--otgy ${DSCR_ROOT}/CamRestOTGY.json
#
# adds nlu annotation from dialogue acts into multiwoz
for split in dev train test ; do
	python -m data_processing.extend_mw_annotation \
		--input_file ${TMP_DIR}/${split}/${split}_mw.json.zip \
		--das_file ${MULTIWOZ_ROOT}/dialog_acts.json \
		--goal_file ${MULTIWOZ_ROOT}/../MultiWOZ_2.1/data.json \
		--output_file ${TMP_DIR}/${split}/${split}_mw_acts.json \
		--compress
	rm ${TMP_DIR}/${split}/${split}_mw.json.zip
done

# merges the files into one
for split in dev train test; do
	python -m data_processing.merge_data \
		--data_dir ${TMP_DIR}/${split} \
		--output_file ${OUT_DIR}/${split}.json \
		--compress
done

#fix split
python -m data_processing.fix_data_split \
	--input-dir ${OUT_DIR} \
	--output-dir ${OUT_DIR}/fixed_split \
	--train-split-ids data/camrest_splits_txt/train_ids_split.txt \
	--dev-split-ids data/camrest_splits_txt/dev_ids_split.txt \
	--compress

# Clean
rm -rf ${TMP_DIR}
rm ${OUT_DIR}/{train,dev,test}.*
mv ${OUT_DIR}/fixed_split/* ${OUT_DIR}
rm -rf ${OUT_DIR}/fixed_split

set +x
