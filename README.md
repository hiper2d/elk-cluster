Elasticsearch Logstash Kibana learning stuff
=============

## How to run

### Docker compose

    docker-compose up    

Check it running at http://localhost:5601

It also make sense to install the ElasticSearch Head Chrome extension to monitor Elastic nodes

### Separate Docker containers

    docker run --rm --name es01 --net esnet -p 9200:9200 -v $(pwd)/config/es01/data:/usr/share/elasticsearch/data -v $(pwd)/config/es01/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml --ulimit memlock=-1:-1 docker.elastic.co/elasticsearch/elasticsearch:7.4.0
    docker run --rm --name es02 --net esnet -v $(pwd)/config/es02/data:/usr/share/elasticsearch/data -v $(pwd)/config/es02/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml --ulimit memlock=-1:-1 docker.elastic.co/elasticsearch/elasticsearch:7.4.0
    docker run --name kibana --net esnet -p 5601:5601 docker.elastic.co/kibana/kibana:7.4.0

Then run the third data node to so how it automatically joins to the existing cluster with no restart

    docker run --rm --name es03 --net esnet -v $(pwd)/config/es03/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml --ulimit memlock=-1:-1 docker.elastic.co/elasticsearch/elasticsearch:7.4.0
