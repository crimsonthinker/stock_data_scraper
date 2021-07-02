#!/bin/bash
source ~/anaconda3/etc/profile.d/conda.sh
conda activate investment
cd /home/khoa/Documents/investment
python3 -m tasks.hnx_stock_codes
python3 -m tasks.hsx_stock_codes
python3 -m tasks.upcom_stock_codes
python3 -m tasks.daily_transaction