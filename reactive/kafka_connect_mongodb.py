import os
from charms.reactive import when, when_any, when_not, set_flag, clear_flag
from charms.reactive.relations import endpoint_from_flag
from charmhelpers.core.hookenv import config, log, status_set
from charms.layer.kafka_connect_helpers import (
    set_worker_config, 
    register_connector,
    unregister_connector,
)


conf = config()
MONGODB_CONNECTOR_NAME = os.environ['JUJU_UNIT_NAME'].split('/')[0] + "-mongodb"


@when_not("mongodb.connected")
def blocked_for_mongodb():
    status_set('blocked', 'Waiting for mongodb relation')


@when_not("config.set.db-name")
def blocked_for_db_name():
    status_set('blocked', 'Waiting for db-name configuration')


@when_not("config.set.db-collections")
def blocked_for_db_collections():
    status_set('blocked', 'Waiting for db-collections configuration')


@when_any('config.changed.topics',
          'config.changed.db-name',
          'config.changed.db-collections',
          'config.changed.write-batch-enabled',
          'config.changed.write-batch-size')
def config_changed():
    clear_flag('kafka-connect-mongodb.running')


@when('mongodb.connected',
    'config.set.db-name',
    'config.set.db-collections')
@when_not('kafka-connect-mongodb.installed')
def install_kafka_connect_mongodb():
    juju_unit_name = os.environ['JUJU_UNIT_NAME'].replace('/', '.')
    worker_configs = {
        'key.converter': 'org.apache.kafka.connect.json.JsonConverter',
        'value.converter': 'org.apache.kafka.connect.json.JsonConverter',
        'key.converter.schemas.enable': 'false',
        'value.converter.schemas.enable': 'false',
        'internal.key.converter': 'org.apache.kafka.connect.json.JsonConverter',
        'internal.value.converter': 'org.apache.kafka.connect.json.JsonConverter',
        'internal.key.converter.schemas.enable': 'false',
        'internal.value.converter.schemas.enable': 'false',
        'offset.storage.topic': juju_unit_name + '.connectoffsets',
        'offset.flush.interval.ms': '10000',
        'config.storage.topic': juju_unit_name + '.connectconfigs',
        'status.storage.topic': juju_unit_name + '.connectstatus',
    }
    set_worker_config(worker_configs)
    set_flag('kafka-connect-mongodb.installed')
    set_flag('kafka-connect-base.install')


@when('kafka-connect.running',
      'mongodb.connected',
      'config.set.db-name',
      'config.set.db-collections')
@when_not('kafka-connect-mongodb.running')
def start_kafka_connect_mongodb():
    if conf.get('write-batch-enabled') and not conf.get('write-batch-size'):
        status_set('blocked', 'Write-batch-enabled is True but write-batch-size is not set')
        return
    if len(conf.get('db-collections', []).split(' ')) != len(conf.get('topics', []).split(' ')):
        status_set('blocked', 'Number of collections does not match topics')
        return

    mongodb = endpoint_from_flag('mongodb.connected')
    mongodb_connection = mongodb.connection_string()
    
    mongodb_connector_config ={
        'connector.class': 'com.startapp.data.MongoSinkConnector',
        'tasks.max': str(conf.get('max-tasks')),
        'db.host': mongodb_connection.split(':')[0],
        'db.port': mongodb_connection.split(':')[1],
        'db.name': conf.get('db-name'),
        'db.collections': conf.get('db-collections').replace(" ", ","),
        'write.batch.enabled': str(conf.get('write-batch-enabled')).lower(),
        'write.batch.size': str(conf.get('write-batch-size')),
        'connect.use_schema': "false",
        'topics': conf.get("topics").replace(" ", ","),
    }

    response = register_connector(mongodb_connector_config, MONGODB_CONNECTOR_NAME)
    if response and (response.status_code == 200 or response.status_code == 201):
        status_set('active', 'ready')
        clear_flag('kafka-connect-mongodb.stopped')
        set_flag('kafka-connect-mongodb.running')        
    else:
        log('Could not register/update connector Response: ' + response)
        status_set('blocked', 'Could not register/update connector, retrying next hook.')


@when('kafka-connect-mongodb.running')
@when_not('mongodb.connected', 'kafka-connect-mongodb.stopped')
def stop_mongodb_connect():
    response = unregister_connector(MONGODB_CONNECTOR_NAME)
    if response and (response.status_code == 204 or response.status_code == 404):
        set_flag('kafka-connect-mongodb.stopped')
        clear_flag('kafka-connect-mongodb.running')
