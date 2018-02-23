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

## Caveats
This setup only handles json formatted Kafka keys / messages.

Default values are used for Kafka connect topic creation, a detailed list of these values can be found [here](https://docs.confluent.io/current/connect/userguide.html). This charm will create three topics for kafka connect with the following naming scheme:
```
juju_unit_name = os.environ['JUJU_UNIT_NAME'].replace('/', '.')
offset.storage.topic = juju_unit_name + '.connectoffsets'
config.storage.topic = juju_unit_name + '.connectconfigs'
status.storage.topic = juju_unit_name + '.connectstatus'
``` 
These topics can be manually created before starting Kafka connect with configs that suit your needs.

This charm is not intended to scale. One charm corresponds to one Kafka connect cluster. Modify the `workers` config to scale the number of workers.

## Authors

This software was created in the [IBCN research group](https://www.ibcn.intec.ugent.be/) of [Ghent University](https://www.ugent.be/en) in Belgium. This software is used in [Tengu](https://tengu.io), a project that aims to make experimenting with data frameworks and tools as easy as possible.

 - Sander Borny <sander.borny@ugent.be>
