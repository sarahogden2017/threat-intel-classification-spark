# threat-intel-classification-spark

# Threat Intel MITRE ATT&CK Tactic Classification Project
Final project for DSC499 Big Data course. A project that incorporates collecting 'big' data, developing a data pipeline, and an ML classification model. This is for scraping cyber intel reports and classifying them to MITRE ATT&amp;CK Tactics. Demonstrates knowledge of Docker, spark, HDFS, and Python.

## Setup
### Docker
```
docker compose up -d --scale datanode=4
```