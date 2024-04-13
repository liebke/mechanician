#!/bin/bash

# Extracting command-line arguments
while getopts "c:d:" opt; do
  case ${opt} in
    c )
      collection=$OPTARG
      ;;
    d )
      directory=$OPTARG
      ;;
    \? )
      echo "Usage: cmd [-c] collection_name [-d] directory_path"
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

# Check if directory is provided
if [ -z "${directory}" ]; then
    echo "Directory not specified. Use -d to specify the directory."
    exit 1
fi

# Check if collection is provided
if [ -z "${collection}" ]; then
    echo "Collection name not specified. Use -c to specify the collection."
    exit 1
fi

# Loop through all PDF files in the specified directory and its subdirectories
find "${directory}" -type f -name '*.pdf' -exec python3 -m mechanician_chroma.load_pdf_into_chroma -c "${collection}" -f {} \;
