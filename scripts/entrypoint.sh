#!/bin/bash
set -e

# Configure pip to use Tsinghua mirror
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF

if [ -e "/opt/airflow/requirements.txt" ]; then
  $(command -v python) -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
  $(command -v pip) install --user -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
fi

# Initialize the database
airflow db init

# Create admin user if it doesn't exist
if ! airflow users list | grep -q "admin"; then
    airflow users create \
        --username admin \
        --firstname admin \
        --lastname admin \
        --role Admin \
        --email admin@example.com \
        --password admin
fi

# Upgrade the database
airflow db upgrade

exec airflow "$@" 