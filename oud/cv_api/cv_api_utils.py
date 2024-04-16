"""Module with utils to fetch data from Cineville API"""

import requests

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


def fetch_from_api(API):
    """Fetch data from API."""
    # Make API request and return the JSON response
    url = API
    response = requests.get(url)
    return response.json()


def save_object_to_database(session, db_object_instance):
    """Save instance to database"""
    session.add(db_object_instance)
    session.commit()


def get_session(database):
    """Open a database session"""
    engine = create_engine(database)
    Base.metadata.create_all(engine)

    session = sessionmaker(bind=engine)
    return session


def extract_from_embedded(api_response, json_value):
    # Example function to extract entities from '_embedded'['collections']
    return api_response["_embedded"][json_value]


def get_existing_db_entities(session, db_object_class, db_entity_attr):
    # Get existing values from the database
    existing_entities = session.query(db_object_class).all()
    return set(getattr(entity, db_entity_attr) for entity in existing_entities)


def get_api_response_data(extract_function, api_response):
    return extract_function(api_response)


def get_existing_api_entities(api_entity_attr, api_response_data):
    return set(api_entity[api_entity_attr] for api_entity in api_response_data)


def get_entities_to_add(existing_api_entities, existing_db_entities):
    return existing_api_entities - existing_db_entities


def get_entities_to_remove(existing_api_entities, existing_db_entities):
    return existing_db_entities - existing_api_entities


def add_entities(
    api_response_data,
    api_entity_attr,
    instance_function,
    session,
    entities_to_add,
    **kwargs
):
    for entity_id in entities_to_add:
        entity_to_add = next(
            api_entity
            for api_entity in api_response_data
            if api_entity[api_entity_attr] == entity_id
        )
        db_object_instance = instance_function(entity_to_add, **kwargs)
        save_object_to_database(session, db_object_instance)


def remove_entities(session, db_object_class, entities_to_remove):
    for entity_id in entities_to_remove:
        entity_to_remove = (
            session.query(db_object_class).filter_by(db_entity_attr=entity_id).first()
        )
        session.delete(entity_to_remove)
    session.commit()


def update_database(
    extract_function,
    api_response,
    api_entity_attr,
    instance_function,
    session,
    db_entity_attr,
    db_object_class,
    **kwargs
):
    api_response_data = get_api_response_data(extract_function, api_response)

    existing_api_entities = get_existing_api_entities(
        api_entity_attr, api_response_data
    )
    existing_db_entities = get_existing_db_entities(
        session, db_object_class, db_entity_attr
    )

    entities_to_add = get_entities_to_add(existing_api_entities, existing_db_entities)
    entities_to_remove = get_entities_to_remove(
        existing_api_entities, existing_db_entities
    )

    add_entities(
        api_response_data,
        api_entity_attr,
        instance_function,
        session,
        entities_to_add,
        **kwargs
    )
    remove_entities(session, db_object_class, entities_to_remove)
