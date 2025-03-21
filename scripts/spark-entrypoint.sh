#!/bin/bash

if [ "$SPARK_MODE" == "master" ]; then
    exec /opt/spark/bin/spark-class org.apache.spark.deploy.master.Master
elif [ "$SPARK_MODE" == "worker" ]; then
    exec /opt/spark/bin/spark-class org.apache.spark.deploy.worker.Worker $SPARK_MASTER_URL
else
    echo "Unknown SPARK_MODE: $SPARK_MODE"
    exit 1
fi 