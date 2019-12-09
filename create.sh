# This is the path where all output is stored
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
out_path=data
mkdir -p $out_path

echo "##############################################################"
echo "# Download corpora"
echo "##############################################################"
dl_path=$out_path/download
python scripts/download.py $dl_path

echo "##############################################################"
echo "# Get infos about downloaded corpora"
echo "##############################################################"
dl_path=$out_path/download
info_path=$dl_path/infos.json
python scripts/corpus_infos.py downloaded $dl_path $info_path

echo "##############################################################"
echo "# Validate corpora"
echo "##############################################################"
dl_path=$out_path/download
val_path=$out_path/validation
python scripts/validate.py $dl_path $val_path


#  The results from the validation step (invalid utterances)
#  have to be incorporated to audiomate manually.


echo "##############################################################"
echo "# Merge and subset"
echo "##############################################################"
dl_path=$out_path/download
full_path=$out_path/full
python scripts/merge_and_subset.py $dl_path $full_path

echo "##############################################################"
echo "# Get infos about merged corpus"
echo "##############################################################"
full_path=$out_path/full
info_path=$out_path/corpus_stats.json
python scripts/corpus_infos.py full $full_path $info_path

echo "##############################################################"
echo "# Generate equivalence state"
echo "##############################################################"
python scripts/equivalence.py generate $out_path

echo "##############################################################"
echo "# Normalize transcripts"
echo "##############################################################"
full_path=$out_path/full
norm_path=$out_path/full_normalized
python scripts/normalize_text.py $full_path $norm_path

echo "##############################################################"
echo "# Waverize"
echo "##############################################################"
in_path=$out_path/full_normalized
wave_path=$out_path/full_waverized
python scripts/waverize.py $in_path $wave_path
