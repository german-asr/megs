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
echo "# Merge and subset"
echo "##############################################################"
dl_path=$out_path/download
full_path=$out_path/full
python scripts/merge_and_subset.py $dl_path $full_path

echo "##############################################################"
echo "# Check equivalence state"
echo "##############################################################"
python scripts/equivalence.py check $out_path

echo "##############################################################"
echo "# Waverize"
echo "##############################################################"
full_path=$out_path/full
wave_path=$out_path/full_waverized
python scripts/waverize.py $full_path $wave_path
