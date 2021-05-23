#!/bin/bash

source $(which conda | xargs -I{} dirname {} | sed 's/\/bin//g')/etc/profile.d/conda.sh
conda activate disinfo_infra
python /media/nvme/disinfo-infra-public/src/system/bin/disinfo_net_data_fetch.py -tcf -rcf -cp -nt 4  disinfo.cfg

