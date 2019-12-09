# This is the path where all output is stored
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
out_path=data

echo "##############################################################"
echo "# Jasperize"
echo "##############################################################"
wave_path=$out_path/full_waverized
jasper_path=$out_path/full_jasperized
python scripts/jasperize.py $wave_path $jasper_path
