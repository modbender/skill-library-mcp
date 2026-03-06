# TRIZ - Systematic Innovation Methodology

A comprehensive OpenClaw skill that implements the complete TRIZ (Theory of Inventive Problem Solving) methodology to help engineers and product managers solve technical problems systematically.

## Overview

TRIZ is a powerful problem-solving methodology developed by Genrich Altshuller that provides systematic approaches to innovation. This skill implements the "Five Bridges" approach to make TRIZ accessible to engineers who may not be familiar with the full methodology.

**Key Benefits:**
- Reduces traditional 1-2 day TRIZ analysis to 4-5 minutes
- Makes TRIZ accessible to non-experts while maintaining professional quality
- Integrates user experience insights with technical problem solving
- Generates validated innovative solutions with comprehensive evaluation

## Core Methodology

### The Five Bridges of TRIZ

1. **Thinking Bridge** - Creative thinking and system understanding
2. **Parameter Bridge** - Resolving technical contradictions using 39 parameters and 40 principles
3. **Structure Bridge** - Analyzing and improving system structure using substance-field analysis
4. **Function Bridge** - Function modeling and trimming for system optimization
5. **Evolution Bridge** - Applying patterns of technical evolution to predict future improvements

### Nine-Step Analysis Process

#### AA-01: Problem Clarification
- Dialog-based guidance (≤5 interactions)
- Captures domain expertise from engineers
- Transforms fuzzy requirements into structured technical problems

#### AA-02: Experience Insight & IFR Definition
- Deep analysis of user experience pain points
- Defines Ideal Final Result (IFR)
- Classifies problem attributes (general/parameter/structure/function)
- Recommends which TRIZ bridges to execute

#### AA-03 to AA-07: Five Bridges Analysis
- **AA-03**: Thinking Bridge Analysis (for general attribute problems)
- **AA-04**: Parameter Bridge Analysis (for parameter contradictions)
- **AA-05**: Structure Bridge Analysis (for structural issues)
- **AA-06**: Function Bridge Analysis (for functional problems)
- **AA-07**: Evolution Bridge Analysis (for evolutionary opportunities)

#### AA-08: Solution Innovation & Evaluation
- Synthesizes results from all five bridges
- Generates 10 innovative solutions
- Evaluates each solution across 8 criteria including technical validation

#### AA-09: Complete Report Generation
- Generates comprehensive TRIZ analysis report
- Includes all analysis steps and results
- Provides actionable recommendations

## Usage Examples

### Basic Problem Analysis
```
Analyze this technical problem using TRIZ methodology: [describe your problem]
```

### Specific Innovation Request
```
Use TRIZ to find innovative solutions for improving battery life in smart watches
```

### User Experience Focus
```
Apply TRIZ to solve user complaints about slow app loading times
```

### Comprehensive Analysis
```
Perform complete TRIZ analysis on our manufacturing process bottleneck
```

## Technical Implementation

### Problem Attribute Classification
The skill automatically classifies problems into four categories:
- **General**: Broad system-level issues requiring creative thinking
- **Parameter**: Technical contradictions between conflicting parameters
- **Structure**: Issues with system components and their relationships
- **Function**: Problems with system functions and interactions

### TRIZ Tools Implemented

#### Parameter Bridge
- **39 Engineering Parameters**: Complete parameter matrix
- **40 Inventive Principles**: All classical TRIZ principles
- **Contradiction Matrix**: Automated contradiction resolution

#### Structure Bridge  
- **Substance-Field Analysis**: Standard and incomplete models
- **76 Standard Solutions**: Complete standard solution library
- **System Trimming**: Function-based component elimination

#### Function Bridge
- **Function Modeling**: Complete function analysis
- **Function Cost Analysis**: Resource efficiency evaluation
- **Idealization**: Moving toward ideal final result

#### Evolution Bridge
- **8 Patterns of Evolution**: Complete evolutionary trends
- **Technology Forecasting**: Future state prediction
- **Maturity Assessment**: Technology lifecycle analysis

### Solution Evaluation Criteria
Each generated solution is evaluated on 8 dimensions:
1. **Technical Feasibility** - Can it be implemented with current technology?
2. **Cost Effectiveness** - What's the cost-benefit ratio?
3. **User Impact** - How much does it improve user experience?
4. **Implementation Complexity** - How difficult is it to implement?
5. **Risk Level** - What are the potential risks?
6. **Time to Market** - How quickly can it be deployed?
7. **Scalability** - Can it scale to larger applications?
8. **Sustainability** - Is it environmentally and economically sustainable?

## Installation

This skill is automatically available when installed in your OpenClaw workspace.

```bash
npx clawhub@latest install triz
```

## License

MIT License - Free to use and modify.