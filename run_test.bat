@echo off
python src\detect.py --input_dir images --output_dir output_images --output_json output_json --people_conf 0.5 --text_conf 0.3 --visualize
pytest -q
