Elasticsearch Logstash Kibana learning stuff
=============

[![Elastic Stack version](https://img.shields.io/badge/ELK-7.4.0-blue.svg?style=flat)](https://www.elastic.co/what-is/elk-stack)

This is my practice of the ELK course "ElasticSearch, LogStash, Kibana (the ELK Stack)" by Manuj Aggarwal and the TetraTutorials Team. The course is a bit outdated a bit (things change too fast these days), thus I had to updated everything including ELK v7, IMBD datasets, import Python scripts, etc.

## How to run ELK cluster

### Docker compose

    docker-compose up    

Check it running at http://localhost:5601

It also make sense to install the ElasticSearch Head Chrome extension to monitor Elastic nodes:

![Elastic Head Plugin](https://raw.githubusercontent.com/hiper2d/elk-cluster/master/images/ElasticHead.PNG)

### Separate Docker containers

With this I played with adding a third node to an already running cluster. First, run two nodes and a Kibana instance:

    docker run --rm --name es01 --net esnet -p 9200:9200 -v $(pwd)/config/es01/data:/usr/share/elasticsearch/data -v $(pwd)/config/es01/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml --ulimit memlock=-1:-1 docker.elastic.co/elasticsearch/elasticsearch:7.4.0
    docker run --rm --name es02 --net esnet -v $(pwd)/config/es02/data:/usr/share/elasticsearch/data -v $(pwd)/config/es02/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml --ulimit memlock=-1:-1 docker.elastic.co/elasticsearch/elasticsearch:7.4.0
    docker run --name kibana --net esnet -p 5601:5601 docker.elastic.co/kibana/kibana:7.4.0

Then run the third data node, it automatically joins to the existing cluster and no restart is needed:

    docker run --rm --name es03 --net esnet -v $(pwd)/config/es03/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml --ulimit memlock=-1:-1 docker.elastic.co/elasticsearch/elasticsearch:7.4.0

The third node will be attached to the existing container.

When run the container for the first time, go to Kibana Dev Tool and add a common template to specify 2 shards by default for every index:

    PUT _template/template_1
    {
      "index_patterns": ["*"],
      "settings": {
        "number_of_shards": 2,
        "number_of_replicas": 1
      }
    }


### Import IMDB Datasets to Elasticsearch via Bulk API

The dataset can be downloaded from https://www.imdb.com/interfaces/

The idea is to import them to the Elasticsearch cluster and to have fun with the data then. But the datasets are in the plain text format and should be converted to JSON first with a Python script.  

1. Download movies and actors datasets from https://www.imdb.com/interfaces/

        curl -o dataset/title.basics.tsv.gz https://datasets.imdbws.com/title.basics.tsv.gz
        curl -o dataset/name.basics.tsv.gz https://datasets.imdbws.com/title.basics.tsv.gz

2. Unpack them:

        gzip -d dataset/name.basics.tsv.gz > dataset/name.basics.tsv
        gzip -d dataset/title.basics.tsv.gz > dataset/title.basics.tsv

3. Verify:

        head -n 10 dataset/name.basics.tsv
        head -n 10 dataset/title.basics.tsv

4. Run script which reads both datasets files, put movies titles to actors records and converts actors records to the json format

        python scripts/import_imdb_dataset.py

    This will generate about 30 JSON files. Elasticsearch restricts too large files to be imported, thus the output should be split in chunks of 500k rows each. I realized that after tried to import a single 2Gb JSON file and got an error. The workaround with many files is ugly, it's probably better to use the Elasticsearch Client. But I've already did it with files, sorry.

5. Verify the script output:

        ls -l dataset/imdb.basics*.json
        head -n 20 dataset/imdb.basics1.json    
    
6. Import JSON to Elasticsearch Cluster (make sure it's running first):

        find dataset/ -name imdb.basics*.json -exec curl -s -H "Content-Type: application/x-ndjson" -XPOST localhost:9200/_bulk --data-binary "@{}" \;

    You should have around 10 millions documents in the actors index now.

7. Don't forget to remove few Gb of rubbish from your filesystem:

        rm dataset/imdb.basics*

### Playing with Logstash

After you run everything with the Docker Compose send a message to Logstash and find it in Elasticsearch:

        curl -XPOST http://localhost:5000 -d "John Smith 39"

Next we a going to send Linux syslog to Elasticsearch via Logstash. I work in Arch Linux thus I made a syslog dump into the dataset/syslog.log file

        journalctl > dataset/syslog.log # dump Arch Linux syslog into a file

