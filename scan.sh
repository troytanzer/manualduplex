#!/bin/bash

# Add CLI options
#- keep current dir, otherwise wipe it
#- set temp dir
#- set output file name
#- skip duplex

# Default output to current dir unless specified above
# Reverse numbers on the second scan
# Change prompt below to allow not scanning second side if we forgot
#   to turn off duplex mode

#For not actually running the scanner, add echo to see what the CLI would
#look like.  Set this to empty string to include scanner in process
DEBUG="echo"
TMP_DIR=/tmp/ScanFiles
FORMAT="pnm" # Can be pnm, pbm, pgm for color, b/w or greyscale
SCAN_OPTS="--format=${FORMAT}"
SANE_BATCH_OPTS="--batch=${TMP_DIR}/out%04d.${FORMAT} --batch-increment=2"
#Brother specific output options - appears that all printer specific
# options are space, not = separated
BROTHER_OPTS=" --mode 'True Gray' "
BROTHER_OPTS+=" --resolution 300 "

BATCH_OPTS=${SANE_BATCH_OPTS} ${BROTHER_OPTIONS}

#Make sure output dir exists and create if not
if [[ -d ${TMP_DIR} ]]
then
    echo "Outputing files to ${TMP_DIR}"
else
    mkdir -p ${TMP_DIR}
    echo "Created ${TMP_DIR} for output files"
fi

#Scan one side, start with page 1 and number files by 2
${DEBUG} scanimage ${SCAN_OPTS} ${BATCH_OPTS} --batch-start=1
#Prompt to flip the papers

read -p "Please flip the papers and hit enter key to scan the reverse side"

#Scan second side, start with page 2 and number files by 2

${DEBUG} scanimage ${SCAN_OPTS} ${BATCH_OPTS} --batch-start=2 

#Convert the files to pdf into one document

convert ${TMP_DIR}/*.${FORMAT} ${TMP_DIR}/Final.pdf

