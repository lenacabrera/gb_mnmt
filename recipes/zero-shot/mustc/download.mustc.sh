#!/usr/bin/env bash
export AUTHCODE=$1

# Download of MuST-C V1.2 (https://ict.fbk.eu/must-c-release-v1-2/)
dest_path=$DATADIR/mustc/raw/download
mkdir -p $dest_path
echo "Downloading MuST-C data to " $dest_path

# https://www.quora.com/How-do-I-download-a-very-large-file-from-Google-Drive/answer/Shane-F-Carr
# https://developers.google.com/oauthplayground/
# curl -H "Authorization: Bearer YYYYY" https://www.googleapis.com/drive/v3/files/XXXXX?alt=media -o ZZZZZ    where YYYYY=authcode XXXXX=drivefileid ZZZZZZ=outputfile

if [ -z $AUTHCODE ]; then
    $AUTHCODE="ya29.a0ARrdaM90rQHQKsmvMtHp2vBwbhmS88QSTOwdSbVjcHURlr4XKdTuaFKwPKOHwLyePsl2pVGLN7-FAYKCtCGXPwAOxrugE7GQA4_uAh8IVDKaDXh3SDGCjJJEBucXvbta3jHt1sN3yTuYYQkVDVr0-Lf81hae"
fi

# -- from v1.0
# English-to-German (63.4 GB)
curl -H "Authorization: Bearer $AUTHCODE" https://www.googleapis.com/drive/v3/files/1Mf2il_VelDIJMSio0bq7I8M9fSs-X4Ie?alt=media -o $dest_path/MUSTC_v1.0_en-de.tar.gz
# English-to-Spanish (78.1 GB)
curl -H "Authorization: Bearer $AUTHCODE" https://www.googleapis.com/drive/v3/files/14d2ttsuEUFXsxx-KRWJMsFhQGrYOJcpH?alt=media -o $dest_path/MUSTC_v1.0_en-es.tar.gz 
# English-to-French (76.5 GB)
curl -H "Authorization: Bearer $AUTHCODE" https://www.googleapis.com/drive/v3/files/1acIBqcPVX5QXXXV9u8_yDPtCgfsdEJDV?alt=media -o $dest_path/MUSTC_v1.0_en-fr.tar.gz 
# English-to-Italian (72.3 GB)
curl -H "Authorization: Bearer $AUTHCODE" https://www.googleapis.com/drive/v3/files/1qbK88SAKxqjMUybkMeIjrJWnNAZyE8V0?alt=media -o $dest_path/MUSTC_v1.0_en-it.tar.gz 
# English-to-Dutch (68.6 GB)
curl -H "Authorization: Bearer $AUTHCODE" https://www.googleapis.com/drive/v3/files/11fNraDQs-LiODDxyV5ZW0Slf3XuDq5Cf?alt=media -o $dest_path/MUSTC_v1.0_en-nl.tar.gz 
# English-to-Portuguese (59.8 GB)
curl -H "Authorization: Bearer $AUTHCODE" https://www.googleapis.com/drive/v3/files/1C5qK1FckA702nsYcXwmGdzlMmHg1F_ot?alt=media -o $dest_path/MUSTC_v1.0_en-pt.tar.gz 
# English-to-Romanian (67.1 GB)
curl -H "Authorization: Bearer $AUTHCODE" https://www.googleapis.com/drive/v3/files/1nbdYR5VqcTbLpOB-9cICKCgsLAs7fVzd?alt=media -o $dest_path/MUSTC_v1.0_en-ro.tar.gz 
# English-to-Russian (70.6 GB)
curl -H "Authorization: Bearer $AUTHCODE" https://www.googleapis.com/drive/v3/files/1Z3hSiP7fsR3kf8fjQYzIa07jmw4KXNnw?alt=media -o $dest_path/MUSTC_v1.0_en-ru.tar.gz 

# --- additional only in c1.2
# English-to-Arabic (74 GB)
curl -H "Authorization: Bearer $AUTHCODE" https://www.googleapis.com/drive/v3/files/1W4mZcr8YywF92DNF9gf0fa3fOem-el0O?alt=media -o $dest_path/MUSTC_v1.0_en-ar.tar.gz 
# English-to-Chinese (71 GB)
curl -H "Authorization: Bearer $AUTHCODE" https://www.googleapis.com/drive/v3/files/1iwOO60H_1DdcU1zSIqBv_y5PwXbJHjQ2?alt=media -o $dest_path/MUSTC_v1.0_en-zh.tar.gz 
# English-to-Czech (37 GB)
curl -H "Authorization: Bearer $AUTHCODE" https://www.googleapis.com/drive/v3/files/1BVgx2rum62n-RCk35JamyM_Jr518dlmC?alt=media -o $dest_path/MUSTC_v1.0_en-cs.tar.gz 
# English-to-Persian (55 GB)
curl -H "Authorization: Bearer $AUTHCODE" https://www.googleapis.com/drive/v3/files/1nDvHEDipiyyEthqLhBVXQO_q3MIpJPKR?alt=media -o $dest_path/MUSTC_v1.0_en-fa.tar.gz 
# English-to-Turkish (71 GB)
curl -H "Authorization: Bearer $AUTHCODE" https://www.googleapis.com/drive/v3/files/1VgMGcBxtZ7UIlIICAItksEeKDYZBmLvj?alt=media -o $dest_path/MUSTC_v1.0_en-tr.tar.gz 
# English-to-Vietnamese (69 GB)
curl -H "Authorization: Bearer $AUTHCODE" https://www.googleapis.com/drive/v3/files/13MJscb-OB7culc8j8Zo9BpXyJ1TalNVg?alt=media -o $dest_path/MUSTC_v1.0_en-vi.tar.gz 


# ------ 
# Alternatively try lines below, however, below might run into forbidden error (potentially due to google drive download quota?)

# # -- from v1.0
# # English-to-German (63.4 GB)
# wget -nc --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/u/0/uc?id=1Mf2il_VelDIJMSio0bq7I8M9fSs-X4Ie&export=download' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1Mf2il_VelDIJMSio0bq7I8M9fSs-X4Ie" -O $dest_path/MUSTC_v1.0_en-de.tar.gz && rm -rf /tmp/cookies.txt
# # English-to-Spanish (78.1 GB)
# wget -nc --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/u/0/uc?id=14d2ttsuEUFXsxx-KRWJMsFhQGrYOJcpH&export=download' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=14d2ttsuEUFXsxx-KRWJMsFhQGrYOJcpH" -O $dest_path/MUSTC_v1.0_en-es.tar.gz && rm -rf /tmp/cookies.txt
# # English-to-French (76.5 GB)
# wget -nc --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/u/0/uc?id=1acIBqcPVX5QXXXV9u8_yDPtCgfsdEJDV&export=download' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1acIBqcPVX5QXXXV9u8_yDPtCgfsdEJDV" -O $dest_path/MUSTC_v1.0_en-fr.tar.gz && rm -rf /tmp/cookies.txt
# # English-to-Italian (72.3 GB)
# wget -nc --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/u/0/uc?id=1qbK88SAKxqjMUybkMeIjrJWnNAZyE8V0&export=download' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1qbK88SAKxqjMUybkMeIjrJWnNAZyE8V0" -O $dest_path/MUSTC_v1.0_en-it.tar.gz && rm -rf /tmp/cookies.txt
# # English-to-Dutch (68.6 GB)
# wget -nc --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/u/0/uc?id=11fNraDQs-LiODDxyV5ZW0Slf3XuDq5Cf&export=download' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=11fNraDQs-LiODDxyV5ZW0Slf3XuDq5Cf" -O $dest_path/MUSTC_v1.0_en-nl.tar.gz && rm -rf /tmp/cookies.txt
# # English-to-Portuguese (59.8 GB)
# wget -nc --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/u/0/uc?id=1C5qK1FckA702nsYcXwmGdzlMmHg1F_ot&export=download' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1C5qK1FckA702nsYcXwmGdzlMmHg1F_ot" -O $dest_path/MUSTC_v1.0_en-pt.tar.gz && rm -rf /tmp/cookies.txt
# # English-to-Romanian (67.1 GB)
# wget -nc --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/u/0/uc?id=1nbdYR5VqcTbLpOB-9cICKCgsLAs7fVzd&export=download' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1nbdYR5VqcTbLpOB-9cICKCgsLAs7fVzd" -O $dest_path/MUSTC_v1.0_en-ro.tar.gz && rm -rf /tmp/cookies.txt
# # English-to-Russian (70.6 GB)
# wget -nc --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/u/0/uc?id=1Z3hSiP7fsR3kf8fjQYzIa07jmw4KXNnw&export=download' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1Z3hSiP7fsR3kf8fjQYzIa07jmw4KXNnw" -O $dest_path/MUSTC_v1.0_en-ru.tar.gz && rm -rf /tmp/cookies.txt

# # --- additional only in c1.2
# # English-to-Arabic (74 GB)
# wget -nc --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/u/0/uc?id=1W4mZcr8YywF92DNF9gf0fa3fOem-el0O&export=download' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1W4mZcr8YywF92DNF9gf0fa3fOem-el0O" -O $dest_path/MUSTC_v1.2_en-ar.tar.gz && rm -rf /tmp/cookies.txt
# # English-to-Chinese (71 GB)
# wget -nc --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/u/0/uc?id=1iwOO60H_1DdcU1zSIqBv_y5PwXbJHjQ2&export=download' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1iwOO60H_1DdcU1zSIqBv_y5PwXbJHjQ2" -O $dest_path/MUSTC_v1.2_en-zh.tar.gz && rm -rf /tmp/cookies.txt
# # English-to-Czech (37 GB)
# wget -nc --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/u/0/uc?id=1BVgx2rum62n-RCk35JamyM_Jr518dlmC&export=download' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1BVgx2rum62n-RCk35JamyM_Jr518dlmC" -O $dest_path/MUSTC_v1.2_en-cs.tar.gz && rm -rf /tmp/cookies.txt
# # English-to-Persian (55 GB)
# wget -nc --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/u/0/uc?id=1nDvHEDipiyyEthqLhBVXQO_q3MIpJPKR&export=download' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1nDvHEDipiyyEthqLhBVXQO_q3MIpJPKR" -O $dest_path/MUSTC_v1.2_en-fa.tar.gz && rm -rf /tmp/cookies.txt
# # English-to-Turkish (71 GB)
# wget -nc --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/u/0/uc?id=1VgMGcBxtZ7UIlIICAItksEeKDYZBmLvj&export=download' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1VgMGcBxtZ7UIlIICAItksEeKDYZBmLvj" -O $dest_path/MUSTC_v1.2_en-tr.tar.gz && rm -rf /tmp/cookies.txt
# # English-to-Vietnamese (69 GB)
# wget -nc --load-cookies /tmp/cookies.txt "https://drive.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://drive.google.com/u/0/uc?id=13MJscb-OB7culc8j8Zo9BpXyJ1TalNVg&export=download' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=13MJscb-OB7culc8j8Zo9BpXyJ1TalNVg" -O $dest_path/MUSTC_v1.2_en-vi.tar.gz && rm -rf /tmp/cookies.txt
