# Kafka-connect-mongodb

Kafka Connect is a framework to stream data into and out of Kafka. For more information see the [documentation](https://docs.confluent.io/current/connect/concepts.html#concepts).

## Overview
This charm sets up a Kafka connect cluster in Kubernetes and configures it to send Kafka topic data (source) to Mongodb collections (sink). 
The connector used can be found [here](https://github.com/startappdev/kafka-connect-mongodb)

## How to use
```bash
juju deploy kafka-connect-mongodb connect
juju add-relation connect kafka
juju add-relation connect mongodb
juju add-relation connect kubernetes-deployer
juju config connect "topics=topic1 topic2"
juju config connect "db-name=testdb"
juju config connect "db-collections=topic1Collection topic2Collection"
```
Data from `topic1` will be sent to `topic1Collection` and `topic2` to `topic2Collection`.

## Authors

This software was created in the [IBCN research group](https://www.ibcn.intec.ugent.be/) of [Ghent University](https://www.ugent.be/en) in Belgium. This software is used in [Tengu](https://tengu.io), a project that aims to make experimenting with data frameworks and tools as easy as possible.

 - Sander Borny <sander.borny@ugent.be>
