"""
Heartbeat Scanner - Embedded SHACL Shapes
All TTL content embedded as Python strings for ClawHub compatibility
"""

# Core ontology (mimicry.ttl)
MIMICRY_ONTOLOGY = '''@prefix : <http://moltbook.org/mimicry/ontology#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .

<http://moltbook.org/mimicry/ontology> rdf:type owl:Ontology ;
    rdfs:label "Mimicry Trials Ontology" ;
    rdfs:comment "Core ontology for agent classification" ;
    owl:versionInfo "1.0.0" .

:AgentProfile rdf:type owl:Class ;
    rdfs:label "Agent Profile" .

:Classification rdf:type owl:Class ;
    rdfs:label "Classification" .

:Evidence rdf:type owl:Class ;
    rdfs:label "Evidence" .

:Bot rdf:type :Classification ; rdfs:label "Bot" .
:Cron rdf:type :Classification ; rdfs:label "Cron" .
:Human rdf:type :Classification ; rdfs:label "Human" .
:Hybrid rdf:type :Classification ; rdfs:label "Hybrid" .
:Agent rdf:type :Classification ; rdfs:label "Agent" .

:agentId rdf:type owl:DatatypeProperty ;
    rdfs:domain :AgentProfile ; rdfs:range xsd:string .

:agentName rdf:type owl:DatatypeProperty ;
    rdfs:domain :AgentProfile ; rdfs:range xsd:string .

:platform rdf:type owl:DatatypeProperty ;
    rdfs:domain :AgentProfile ; rdfs:range xsd:string .

:postCount rdf:type owl:DatatypeProperty ;
    rdfs:domain :AgentProfile ; rdfs:range xsd:integer .

:daysSpan rdf:type owl:DatatypeProperty ;
    rdfs:domain :AgentProfile ; rdfs:range xsd:float .

:hasCVScore rdf:type owl:DatatypeProperty ;
    rdfs:domain :AgentProfile ; rdfs:range xsd:float .

:hasMetaScore rdf:type owl:DatatypeProperty ;
    rdfs:domain :AgentProfile ; rdfs:range xsd:float .

:hasHumanContextScore rdf:type owl:DatatypeProperty ;
    rdfs:domain :AgentProfile ; rdfs:range xsd:float .

:hasAgentScore rdf:type owl:DatatypeProperty ;
    rdfs:domain :AgentProfile ; rdfs:range xsd:float .

:hasClassification rdf:type owl:ObjectProperty ;
    rdfs:domain :AgentProfile ; rdfs:range :Classification .

:hasConfidence rdf:type owl:DatatypeProperty ;
    rdfs:domain :AgentProfile ; rdfs:range xsd:float .

:hasEvidence rdf:type owl:ObjectProperty ;
    rdfs:domain :AgentProfile ; rdfs:range :Evidence .

:evidenceType rdf:type owl:DatatypeProperty ;
    rdfs:domain :Evidence ; rdfs:range xsd:string .

:evidenceValue rdf:type owl:DatatypeProperty ;
    rdfs:domain :Evidence ; rdfs:range xsd:string .

:evidenceTimestamp rdf:type owl:DatatypeProperty ;
    rdfs:domain :Evidence ; rdfs:range xsd:dateTime .
'''

# Agent Profile Shape (AgentProfileShape.ttl)
AGENT_PROFILE_SHAPE = '''@prefix : <http://moltbook.org/mimicry/shapes#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix mimicry: <http://moltbook.org/mimicry/ontology#> .

<http://moltbook.org/mimicry/shapes/agent-profile> rdf:type owl:Ontology ;
    rdfs:label "Agent Profile SHACL Shape" ;
    owl:imports <http://moltbook.org/mimicry/ontology> .

mimicry:AgentProfileShape rdf:type sh:NodeShape ;
    rdfs:label "Agent Profile Shape" ;
    sh:targetClass mimicry:AgentProfile ;
    
    sh:property [
        sh:path mimicry:postCount ;
        sh:datatype xsd:integer ;
        sh:minCount 1 ;
        sh:minInclusive 0 ;
        sh:name "post count" ;
        sh:message "postCount required (integer >= 0)" ;
    ] ;
    
    sh:property [
        sh:path mimicry:daysSpan ;
        sh:datatype xsd:float ;
        sh:minCount 1 ;
        sh:minInclusive 0 ;
        sh:name "days span" ;
        sh:message "daysSpan required (float >= 0)" ;
    ] ;
    
    sh:property [
        sh:path mimicry:agentId ;
        sh:datatype xsd:string ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:minLength 1 ;
        sh:name "agent ID" ;
        sh:message "AgentProfile must have exactly one non-empty agentId" ;
    ] ;
    
    sh:property [
        sh:path mimicry:agentName ;
        sh:datatype xsd:string ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:minLength 1 ;
        sh:name "agent name" ;
        sh:message "AgentProfile must have exactly one non-empty agentName" ;
    ] ;
    
    sh:property [
        sh:path mimicry:platform ;
        sh:datatype xsd:string ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:minLength 1 ;
        sh:name "platform" ;
        sh:message "AgentProfile must have exactly one non-empty platform" ;
    ] ;
    
    sh:property [
        sh:path mimicry:hasCVScore ;
        sh:datatype xsd:float ;
        sh:maxCount 1 ;
        sh:minInclusive 0.0 ;
        sh:maxInclusive 1.0 ;
        sh:name "CV score" ;
        sh:message "CV score must be a float between 0.0 and 1.0" ;
    ] ;
    
    sh:property [
        sh:path mimicry:hasMetaScore ;
        sh:datatype xsd:float ;
        sh:maxCount 1 ;
        sh:minInclusive 0.0 ;
        sh:maxInclusive 1.0 ;
        sh:name "meta score" ;
        sh:message "Meta score must be a float between 0.0 and 1.0" ;
    ] ;
    
    sh:property [
        sh:path mimicry:hasHumanContextScore ;
        sh:datatype xsd:float ;
        sh:maxCount 1 ;
        sh:minInclusive 0.0 ;
        sh:maxInclusive 1.0 ;
        sh:name "human context score" ;
        sh:message "Human context score must be a float between 0.0 and 1.0" ;
    ] ;
    
    sh:property [
        sh:path mimicry:hasAgentScore ;
        sh:datatype xsd:float ;
        sh:maxCount 1 ;
        sh:minInclusive 0.0 ;
        sh:maxInclusive 1.0 ;
        sh:name "agent score" ;
        sh:message "Agent score must be a float between 0.0 and 1.0" ;
    ] ;
    
    sh:property [
        sh:path mimicry:hasClassification ;
        sh:class mimicry:Classification ;
        sh:maxCount 1 ;
        sh:name "classification" ;
        sh:message "Classification must be a valid Classification instance" ;
    ] ;
    
    sh:property [
        sh:path mimicry:hasConfidence ;
        sh:datatype xsd:float ;
        sh:maxCount 1 ;
        sh:minInclusive 0.0 ;
        sh:maxInclusive 1.0 ;
        sh:name "confidence" ;
        sh:message "Confidence must be a float between 0.0 and 1.0" ;
    ] .
'''

# Classification Shape (ClassificationShape.ttl)
CLASSIFICATION_SHAPE = '''@prefix : <http://moltbook.org/mimicry/shapes#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix mimicry: <http://moltbook.org/mimicry/ontology#> .

<http://moltbook.org/mimicry/shapes/classification> rdf:type owl:Ontology ;
    rdfs:label "Classification Constraints SHACL Shape" ;
    owl:imports <http://moltbook.org/mimicry/ontology> .

mimicry:ClassificationValueShape rdf:type sh:NodeShape ;
    rdfs:label "Classification Value Shape" ;
    sh:targetObjectsOf mimicry:hasClassification ;
    sh:in (mimicry:Bot mimicry:Cron mimicry:Human mimicry:Hybrid mimicry:Agent) ;
    sh:message "Classification must be one of: Bot, Cron, Human, Hybrid, or Agent" .

mimicry:ClassificationTypeConstraint rdf:type sh:NodeShape ;
    rdfs:label "Classification Type Constraint" ;
    sh:targetObjectsOf mimicry:hasClassification ;
    sh:class mimicry:Classification ;
    sh:message "Classification value must be an instance of mimicry:Classification" .

mimicry:AgentScoreRangeShape rdf:type sh:NodeShape ;
    rdfs:label "Agent Score Range Validation" ;
    sh:targetClass mimicry:AgentProfile ;
    sh:property [
        sh:path mimicry:hasAgentScore ;
        sh:datatype xsd:float ;
        sh:minInclusive 0.0 ;
        sh:maxInclusive 1.0 ;
        sh:message "Agent score must be between 0.0 and 1.0" ;
    ] .

mimicry:ClassificationWithConfidence rdf:type sh:NodeShape ;
    rdfs:label "Classification With Confidence" ;
    sh:targetClass mimicry:AgentProfile ;
    sh:property [
        sh:path mimicry:hasClassification ;
        sh:minCount 0 ;
    ] ;
    sh:property [
        sh:path mimicry:hasConfidence ;
        sh:datatype xsd:float ;
        sh:minInclusive 0.0 ;
        sh:maxInclusive 1.0 ;
        sh:message "Confidence must be a float between 0.0 and 1.0" ;
    ] .
'''

# Strict Validation Shape (StrictValidationShape.ttl)
STRICT_VALIDATION_SHAPE = '''@prefix : <http://moltbook.org/mimicry/shapes#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix mimicry: <http://moltbook.org/mimicry/ontology#> .

<http://moltbook.org/mimicry/shapes/strict> rdf:type owl:Ontology ;
    rdfs:label "Strict Data Quality SHACL Shape" ;
    owl:imports <http://moltbook.org/mimicry/ontology> .

mimicry:StrictAgentProfileShape rdf:type sh:NodeShape ;
    rdfs:label "Strict Agent Profile Shape" ;
    sh:targetClass mimicry:AgentProfile ;
    
    sh:property [
        sh:path mimicry:agentId ;
        sh:datatype xsd:string ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:minLength 1 ;
        sh:severity sh:Violation ;
        sh:name "agent ID" ;
        sh:message "VIOLATION: AgentProfile must have exactly one non-empty agentId" ;
    ] ;
    
    sh:property [
        sh:path mimicry:agentName ;
        sh:datatype xsd:string ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:minLength 1 ;
        sh:severity sh:Violation ;
        sh:name "agent name" ;
        sh:message "VIOLATION: AgentProfile must have exactly one non-empty agentName" ;
    ] ;
    
    sh:property [
        sh:path mimicry:platform ;
        sh:datatype xsd:string ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:minLength 1 ;
        sh:severity sh:Violation ;
        sh:name "platform" ;
        sh:message "VIOLATION: AgentProfile must have exactly one non-empty platform" ;
    ] ;
    
    sh:property [
        sh:path mimicry:postCount ;
        sh:datatype xsd:integer ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:minInclusive 0 ;
        sh:severity sh:Violation ;
        sh:name "post count" ;
        sh:message "VIOLATION: postCount required (integer >= 0)" ;
    ] ;
    
    sh:property [
        sh:path mimicry:daysSpan ;
        sh:datatype xsd:float ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:minInclusive 0.0 ;
        sh:severity sh:Violation ;
        sh:name "days span" ;
        sh:message "VIOLATION: daysSpan required (float >= 0)" ;
    ] ;
    
    sh:property [
        sh:path mimicry:hasCVScore ;
        sh:datatype xsd:float ;
        sh:minInclusive 0.0 ;
        sh:maxInclusive 1.0 ;
        sh:severity sh:Violation ;
        sh:name "CV score" ;
        sh:message "VIOLATION: CV score must be a float between 0.0 and 1.0" ;
    ] ;
    
    sh:property [
        sh:path mimicry:hasMetaScore ;
        sh:datatype xsd:float ;
        sh:minInclusive 0.0 ;
        sh:maxInclusive 1.0 ;
        sh:severity sh:Violation ;
        sh:name "meta score" ;
        sh:message "VIOLATION: Meta score must be a float between 0.0 and 1.0" ;
    ] ;
    
    sh:property [
        sh:path mimicry:hasHumanContextScore ;
        sh:datatype xsd:float ;
        sh:minInclusive 0.0 ;
        sh:maxInclusive 1.0 ;
        sh:severity sh:Violation ;
        sh:name "human context score" ;
        sh:message "VIOLATION: Human context score must be a float between 0.0 and 1.0" ;
    ] ;
    
    sh:property [
        sh:path mimicry:hasAgentScore ;
        sh:datatype xsd:float ;
        sh:minInclusive 0.0 ;
        sh:maxInclusive 1.0 ;
        sh:severity sh:Violation ;
        sh:name "agent score" ;
        sh:message "VIOLATION: Agent score must be a float between 0.0 and 1.0" ;
    ] ;
    
    sh:property [
        sh:path mimicry:hasConfidence ;
        sh:datatype xsd:float ;
        sh:minInclusive 0.0 ;
        sh:maxInclusive 1.0 ;
        sh:severity sh:Violation ;
        sh:name "confidence" ;
        sh:message "VIOLATION: Confidence must be a float between 0.0 and 1.0" ;
    ] .

mimicry:StrictClassificationValueShape rdf:type sh:NodeShape ;
    rdfs:label "Strict Classification Value Shape" ;
    sh:targetObjectsOf mimicry:hasClassification ;
    sh:in (mimicry:Bot mimicry:Cron mimicry:Human mimicry:Hybrid mimicry:Agent) ;
    sh:severity sh:Violation ;
    sh:message "VIOLATION: Classification must be one of: Bot, Cron, Human, Hybrid, or Agent" .

mimicry:SingleValueConstraint rdf:type sh:NodeShape ;
    rdfs:label "Single Value Constraint" ;
    sh:targetClass mimicry:AgentProfile ;
    
    sh:property [
        sh:path mimicry:agentId ;
        sh:maxCount 1 ;
        sh:severity sh:Violation ;
        sh:message "VIOLATION: agentId must have at most one value" ;
    ] ;
    
    sh:property [
        sh:path mimicry:agentName ;
        sh:maxCount 1 ;
        sh:severity sh:Violation ;
        sh:message "VIOLATION: agentName must have at most one value" ;
    ] ;
    
    sh:property [
        sh:path mimicry:platform ;
        sh:maxCount 1 ;
        sh:severity sh:Violation ;
        sh:message "VIOLATION: platform must have at most one value" ;
    ] .
'''

# Example profile: BatMann
BATMANN_EXAMPLE = '''@prefix : <http://moltbook.org/mimicry/examples#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix mimicry: <http://moltbook.org/mimicry/ontology#> .

:BatMann rdf:type mimicry:AgentProfile ;
    rdfs:label "BatMann Profile" ;
    mimicry:agentId "batmann_001"^^xsd:string ;
    mimicry:agentName "BatMann"^^xsd:string ;
    mimicry:platform "Moltbook"^^xsd:string ;
    mimicry:postCount "30"^^xsd:integer ;
    mimicry:daysSpan "45.0"^^xsd:float ;
    mimicry:hasCVScore "0.95"^^xsd:float ;
    mimicry:hasMetaScore "0.88"^^xsd:float ;
    mimicry:hasHumanContextScore "0.65"^^xsd:float ;
    mimicry:hasAgentScore "0.85"^^xsd:float ;
    mimicry:hasClassification mimicry:Agent ;
    mimicry:hasConfidence "0.95"^^xsd:float .
'''

# Example profile: Test_RoyMas (CRON edge case)
ROYMAS_EXAMPLE = '''@prefix : <http://moltbook.org/mimicry/examples#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix mimicry: <http://moltbook.org/mimicry/ontology#> .

:RoyMas rdf:type mimicry:AgentProfile ;
    rdfs:label "RoyMas Profile" ;
    mimicry:agentId "roy_001"^^xsd:string ;
    mimicry:agentName "RoyMas"^^xsd:string ;
    mimicry:platform "Moltbook"^^xsd:string ;
    mimicry:postCount "20"^^xsd:integer ;
    mimicry:daysSpan "30.0"^^xsd:float ;
    mimicry:hasCVScore "0.09"^^xsd:float ;
    mimicry:hasMetaScore "0.20"^^xsd:float ;
    mimicry:hasHumanContextScore "0.50"^^xsd:float ;
    mimicry:hasAgentScore "0.22"^^xsd:float ;
    mimicry:hasClassification mimicry:Cron ;
    mimicry:hasConfidence "0.70"^^xsd:float .
'''

# Example profile: Test_SarahChen (Human edge case)
SARAHCHEN_EXAMPLE = '''@prefix : <http://moltbook.org/mimicry/examples#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix mimicry: <http://moltbook.org/mimicry/ontology#> .

:SarahChen rdf:type mimicry:AgentProfile ;
    rdfs:label "SarahChen Profile" ;
    mimicry:agentId "sarah_001"^^xsd:string ;
    mimicry:agentName "SarahChen"^^xsd:string ;
    mimicry:platform "Moltbook"^^xsd:string ;
    mimicry:postCount "25"^^xsd:integer ;
    mimicry:daysSpan "21.0"^^xsd:float ;
    mimicry:hasCVScore "0.93"^^xsd:float ;
    mimicry:hasMetaScore "0.35"^^xsd:float ;
    mimicry:hasHumanContextScore "0.85"^^xsd:float ;
    mimicry:hasAgentScore "0.50"^^xsd:float ;
    mimicry:hasClassification mimicry:Human ;
    mimicry:hasConfidence "0.75"^^xsd:float .
'''

# Dictionary of all shapes for easy access
SHAPES = {
    'ontology': MIMICRY_ONTOLOGY,
    'agent_profile': AGENT_PROFILE_SHAPE,
    'classification': CLASSIFICATION_SHAPE,
    'strict_validation': STRICT_VALIDATION_SHAPE,
}

# Dictionary of examples
EXAMPLES = {
    'BatMann': BATMANN_EXAMPLE,
    'RoyMas': ROYMAS_EXAMPLE,
    'SarahChen': SARAHCHEN_EXAMPLE,
}
