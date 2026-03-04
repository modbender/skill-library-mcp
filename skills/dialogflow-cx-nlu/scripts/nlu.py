#!/usr/bin/env python3
"""
Dialogflow CX NLU CLI - Intents and Entity Types management

Usage:
    python nlu.py list-intents --agent AGENT_NAME
    python nlu.py create-intent --agent AGENT_NAME --intent "Intent Name" --phrases "phrase1,phrase2"
    python nlu.py get-intent --intent INTENT_NAME
    python nlu.py update-intent --intent INTENT_NAME --name "New Name"
    python nlu.py delete-intent --intent INTENT_NAME
    python nlu.py list-entities --agent AGENT_NAME
    python nlu.py create-entity --agent AGENT_NAME --name "Entity Name" --values "value1,value2"
    python nlu.py get-entity --entity ENTITY_NAME
    python nlu.py update-entity --entity ENTITY_NAME --name "New Name"
    python nlu.py delete-entity --entity ENTITY_NAME

Requires:
    - google-cloud-dialogflow-cx
    - google-auth

Install:
    pip install google-cloud-dialogflow-cx google-auth
"""

import argparse
import json
import sys
import os

try:
    from google.cloud.dialogflowcx_v3beta1 import (
        IntentsClient, EntityTypesClient, Intent, EntityType
    )
    from google.cloud.dialogflowcx_v3beta1.types import intent as intent_types
    from google.cloud.dialogflowcx_v3beta1.types import entity_type as entity_types
    from google.protobuf.json_format import MessageToDict
except ImportError:
    print("Error: google-cloud-dialogflow-cx not installed")
    print("Run: pip install google-cloud-dialogflow-cx google-auth")
    sys.exit(1)


def list_intents(agent_name: str):
    """List all intents in an agent."""
    client = IntentsClient()
    
    print(f"Listing intents for {agent_name}...\n")
    
    for intent in client.list_intents(parent=agent_name):
        print(f"  {intent.display_name}")
        print(f"    Name: {intent.name}")
        phrases = [tp.parts[0].text for tp in intent.training_phrases[:3] if tp.parts]
        if phrases:
            print(f"    Sample phrases: {', '.join(phrases)}")
        print()


def create_intent(agent_name: str, display_name: str, phrases: list):
    """Create a new intent with training phrases."""
    client = IntentsClient()
    
    training_phrases = []
    for phrase in phrases:
        part = intent_types.Intent.TrainingPhrase.Part(text=phrase.strip())
        training_phrase = intent_types.Intent.TrainingPhrase(parts=[part], repeat_count=1)
        training_phrases.append(training_phrase)
    
    intent = Intent(
        display_name=display_name,
        training_phrases=training_phrases
    )
    
    result = client.create_intent(parent=agent_name, intent=intent)
    print(f"Created intent: {result.name}")
    print(f"Display name: {result.display_name}")


def get_intent(intent_name: str):
    """Get intent details."""
    client = IntentsClient()
    
    intent = client.get_intent(name=intent_name)
    print(json.dumps(MessageToDict(intent._pb), indent=2))


def update_intent(intent_name: str, display_name: str = None, description: str = None):
    """Update an intent."""
    client = IntentsClient()
    
    intent = client.get_intent(name=intent_name)
    
    if display_name:
        intent.display_name = display_name
    if description is not None:
        intent.description = description
    
    result = client.update_intent(intent=intent)
    print(f"Updated intent: {result.name}")
    print(f"Display name: {result.display_name}")


def delete_intent(intent_name: str):
    """Delete an intent."""
    client = IntentsClient()
    
    client.delete_intent(name=intent_name)
    print(f"Deleted intent: {intent_name}")


def list_entity_types(agent_name: str):
    """List all entity types in an agent."""
    client = EntityTypesClient()
    
    print(f"Listing entity types for {agent_name}...\n")
    
    for et in client.list_entity_types(parent=agent_name):
        print(f"  {et.display_name}")
        print(f"    Name: {et.name}")
        print(f"    Kind: {et.kind}")
        if et.entities:
            print(f"    Entities: {len(et.entities)}")
        print()


def create_entity_type(agent_name: str, display_name: str, values: list, kind: str = "KIND_LIST"):
    """Create a new entity type."""
    client = EntityTypesClient()
    
    entities = []
    for value in values:
        entity = entity_types.EntityType.Entity(value=value.strip())
        entities.append(entity)
    
    entity_type = EntityType(
        display_name=display_name,
        kind=kind,
        entities=entities
    )
    
    result = client.create_entity_type(parent=agent_name, entity_type=entity_type)
    print(f"Created entity type: {result.name}")
    print(f"Display name: {result.display_name}")


def get_entity_type(entity_name: str):
    """Get entity type details."""
    client = EntityTypesClient()
    
    et = client.get_entity_type(name=entity_name)
    print(json.dumps(MessageToDict(et._pb), indent=2))


def update_entity_type(entity_name: str, display_name: str = None):
    """Update an entity type."""
    client = EntityTypesClient()
    
    et = client.get_entity_type(name=entity_name)
    
    if display_name:
        et.display_name = display_name
    
    result = client.update_entity_type(entity_type=et)
    print(f"Updated entity type: {result.name}")
    print(f"Display name: {result.display_name}")


def delete_entity_type(entity_name: str):
    """Delete an entity type."""
    client = EntityTypesClient()
    
    client.delete_entity_type(name=entity_name)
    print(f"Deleted entity type: {entity_name}")


def main():
    parser = argparse.ArgumentParser(description="Dialogflow CX NLU CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # list-intents
    p = subparsers.add_parser("list-intents", help="List intents")
    p.add_argument("--agent", required=True, help="Full agent name")
    
    # create-intent
    p = subparsers.add_parser("create-intent", help="Create intent")
    p.add_argument("--agent", required=True, help="Full agent name")
    p.add_argument("--intent", required=True, help="Intent display name")
    p.add_argument("--phrases", required=True, help="Comma-separated training phrases")
    
    # get-intent
    p = subparsers.add_parser("get-intent", help="Get intent details")
    p.add_argument("--intent", required=True, help="Full intent name")
    
    # update-intent
    p = subparsers.add_parser("update-intent", help="Update intent")
    p.add_argument("--intent", required=True, help="Full intent name")
    p.add_argument("--name", help="New display name")
    p.add_argument("--description", help="New description")
    
    # delete-intent
    p = subparsers.add_parser("delete-intent", help="Delete intent")
    p.add_argument("--intent", required=True, help="Full intent name")
    
    # list-entities
    p = subparsers.add_parser("list-entities", help="List entity types")
    p.add_argument("--agent", required=True, help="Full agent name")
    
    # create-entity
    p = subparsers.add_parser("create-entity", help="Create entity type")
    p.add_argument("--agent", required=True, help="Full agent name")
    p.add_argument("--name", required=True, help="Entity type display name")
    p.add_argument("--values", required=True, help="Comma-separated entity values")
    p.add_argument("--kind", default="KIND_LIST", help="Entity kind (KIND_LIST, KIND_MAP, KIND_REGEXP)")
    
    # get-entity
    p = subparsers.add_parser("get-entity", help="Get entity type details")
    p.add_argument("--entity", required=True, help="Full entity type name")
    
    # update-entity
    p = subparsers.add_parser("update-entity", help="Update entity type")
    p.add_argument("--entity", required=True, help="Full entity type name")
    p.add_argument("--name", help="New display name")
    
    # delete-entity
    p = subparsers.add_parser("delete-entity", help="Delete entity type")
    p.add_argument("--entity", required=True, help="Full entity type name")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "list-intents":
        list_intents(args.agent)
    elif args.command == "create-intent":
        phrases = args.phrases.split(",")
        create_intent(args.agent, args.intent, phrases)
    elif args.command == "get-intent":
        get_intent(args.intent)
    elif args.command == "update-intent":
        update_intent(args.intent, args.name, args.description)
    elif args.command == "delete-intent":
        delete_intent(args.intent)
    elif args.command == "list-entities":
        list_entity_types(args.agent)
    elif args.command == "create-entity":
        values = args.values.split(",")
        create_entity_type(args.agent, args.name, values, args.kind)
    elif args.command == "get-entity":
        get_entity_type(args.entity)
    elif args.command == "update-entity":
        update_entity_type(args.entity, args.name)
    elif args.command == "delete-entity":
        delete_entity_type(args.entity)


if __name__ == "__main__":
    main()