"""
Mental Health and Psychiatric Genetics Markers.
Markers associated with psychiatric conditions, neurotransmitter function,
and medication response in mental health.

IMPORTANT: These are risk factors, not diagnoses. Mental health conditions
are highly polygenic and heavily influenced by environment.
"""

MENTAL_HEALTH_MARKERS = {
    # =========================================================================
    # MOOD DISORDERS - DEPRESSION
    # =========================================================================
    
    "rs6265": {
        "gene": "BDNF",
        "name": "Val66Met",
        "variant": "Val66Met",
        "risk_allele": "T",
        "category": "depression_anxiety",
        "conditions": ["Major depression", "Anxiety disorders", "PTSD"],
        "evidence": "moderate",
        "references": ["PMID:12805117", "PMID:18779510"],
        "interpretation": {
            "CC": "Val/Val - Normal BDNF secretion",
            "CT": "Val/Met - Reduced activity-dependent BDNF release",
            "TT": "Met/Met - Significantly reduced BDNF secretion, increased stress sensitivity"
        },
        "clinical_notes": "Met carriers may have reduced neuroplasticity and increased depression risk under stress",
        "actionable": {
            "priority": "medium",
            "action_type": "lifestyle",
            "recommendations": [
                "Exercise strongly promotes BDNF (protective)",
                "Stress management particularly important",
                "May affect antidepressant response"
            ]
        }
    },
    
    "rs4570625": {
        "gene": "TPH2",
        "name": "Tryptophan hydroxylase 2",
        "risk_allele": "T",
        "category": "depression",
        "conditions": ["Major depression", "Suicide risk"],
        "evidence": "moderate",
        "references": ["PMID:15985308"],
        "interpretation": {
            "GG": "Normal serotonin synthesis",
            "GT": "Slightly reduced TPH2 activity",
            "TT": "Reduced brain serotonin synthesis capacity"
        },
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["May inform SSRI response expectations"]
        }
    },
    
    "rs25531": {
        "gene": "SLC6A4",
        "name": "Serotonin transporter promoter",
        "risk_allele": "G",
        "category": "depression_anxiety",
        "conditions": ["Depression", "Anxiety", "Stress sensitivity"],
        "evidence": "moderate",
        "references": ["PMID:16389195"],
        "note": "Part of 5-HTTLPR functional variant",
        "interpretation": {
            "AA": "Higher serotonin reuptake",
            "AG": "Intermediate",
            "GG": "Lower expression, increased stress sensitivity"
        },
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": [
                "Stress-diathesis model - environment critical",
                "May benefit more from psychotherapy combined with meds"
            ]
        }
    },
    
    # =========================================================================
    # BIPOLAR DISORDER
    # =========================================================================
    
    "rs1006737": {
        "gene": "CACNA1C",
        "name": "Calcium channel risk",
        "risk_allele": "A",
        "category": "bipolar",
        "conditions": ["Bipolar disorder", "Schizophrenia", "Major depression"],
        "evidence": "strong",
        "references": ["PMID:18711365", "PMID:21926972"],
        "interpretation": {
            "GG": "Lower risk genotype",
            "AG": "Intermediate risk",
            "AA": "Elevated risk for mood disorders"
        },
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["Calcium channel gene - lithium mechanism relevant"]
        }
    },
    
    "rs10994336": {
        "gene": "ANK3",
        "name": "Ankyrin 3 bipolar",
        "risk_allele": "T",
        "category": "bipolar",
        "conditions": ["Bipolar disorder"],
        "evidence": "strong",
        "references": ["PMID:18711365"],
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["One of many bipolar risk variants"]
        }
    },
    
    "rs4027132": {
        "gene": "DGKH",
        "name": "Diacylglycerol kinase",
        "risk_allele": "A",
        "category": "bipolar",
        "conditions": ["Bipolar disorder"],
        "evidence": "moderate",
        "references": ["PMID:18492793"],
        "note": "Lithium response pathway",
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["May relate to lithium response"]
        }
    },
    
    # =========================================================================
    # SCHIZOPHRENIA
    # =========================================================================
    
    "rs1625579": {
        "gene": "MIR137",
        "name": "MicroRNA 137",
        "risk_allele": "T",
        "category": "schizophrenia",
        "conditions": ["Schizophrenia"],
        "evidence": "strong",
        "references": ["PMID:21926974"],
        "note": "Strongest schizophrenia GWAS hit",
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["Risk factor among many; environment crucial"]
        }
    },
    
    "rs6904071": {
        "gene": "ZNF804A",
        "name": "Zinc finger protein schizophrenia",
        "risk_allele": "A",
        "category": "schizophrenia",
        "conditions": ["Schizophrenia", "Bipolar disorder"],
        "evidence": "strong",
        "references": ["PMID:18678675"],
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["Cross-diagnostic risk factor"]
        }
    },
    
    "rs2007044": {
        "gene": "TCF4",
        "name": "Transcription factor 4",
        "risk_allele": "G",
        "category": "schizophrenia",
        "conditions": ["Schizophrenia"],
        "evidence": "strong",
        "references": ["PMID:19571808"],
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["Neurodevelopmental pathway"]
        }
    },
    
    # =========================================================================
    # ANXIETY DISORDERS
    # =========================================================================
    
    "rs4680": {
        "gene": "COMT",
        "name": "Val158Met",
        "variant": "Val158Met",
        "risk_allele": "A",
        "category": "anxiety_cognition",
        "conditions": ["Anxiety", "Pain sensitivity", "Stress response"],
        "evidence": "strong",
        "references": ["PMID:10529231", "PMID:15557296"],
        "interpretation": {
            "GG": "Val/Val (Warrior) - Fast dopamine clearance, stress resilient but lower baseline cognition",
            "AG": "Val/Met - Intermediate phenotype",
            "AA": "Met/Met (Worrier) - Slow dopamine clearance, better cognition but higher anxiety/pain sensitivity"
        },
        "actionable": {
            "priority": "medium",
            "action_type": "awareness",
            "recommendations": [
                "Met/Met: May benefit from stress reduction techniques",
                "Val/Val: May tolerate stress better but need cognitive support",
                "Affects response to stimulants and some medications"
            ]
        }
    },
    
    "rs165599": {
        "gene": "COMT",
        "name": "COMT 3' UTR",
        "risk_allele": "A",
        "category": "anxiety",
        "conditions": ["Anxiety", "Panic disorder"],
        "evidence": "moderate",
        "references": ["PMID:15316609"],
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["Secondary COMT variant"]
        }
    },
    
    "rs3800373": {
        "gene": "FKBP5",
        "name": "FKBP5 stress response",
        "risk_allele": "T",
        "category": "ptsd_stress",
        "conditions": ["PTSD", "Depression", "Stress-related disorders"],
        "evidence": "strong",
        "references": ["PMID:18252227"],
        "note": "HPA axis regulation - trauma response",
        "interpretation": {
            "CC": "Normal cortisol feedback",
            "CT": "Intermediate",
            "TT": "Impaired cortisol feedback, increased PTSD risk after trauma"
        },
        "actionable": {
            "priority": "medium",
            "action_type": "awareness",
            "recommendations": [
                "Gene x environment interaction",
                "T carriers more vulnerable to childhood trauma effects",
                "Early intervention after trauma may be especially important"
            ]
        }
    },
    
    "rs1360780": {
        "gene": "FKBP5",
        "name": "FKBP5 trauma response",
        "risk_allele": "T",
        "category": "ptsd",
        "conditions": ["PTSD", "Childhood trauma effects"],
        "evidence": "strong",
        "references": ["PMID:18252227", "PMID:20962098"],
        "actionable": {
            "priority": "medium",
            "action_type": "awareness",
            "recommendations": ["Trauma-sensitive care approach important"]
        }
    },
    
    # =========================================================================
    # ADHD
    # =========================================================================
    
    "rs27072": {
        "gene": "SLC6A3",
        "name": "Dopamine transporter DAT1",
        "risk_allele": "T",
        "category": "adhd",
        "conditions": ["ADHD", "Stimulant response"],
        "evidence": "moderate",
        "references": ["PMID:15108140"],
        "note": "Associated with DAT1 10-repeat VNTR",
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["May affect stimulant medication response"]
        }
    },
    
    "rs1800544": {
        "gene": "ADRA2A",
        "name": "Alpha-2A adrenergic receptor",
        "risk_allele": "G",
        "category": "adhd",
        "conditions": ["ADHD", "Attention regulation"],
        "evidence": "moderate",
        "references": ["PMID:12858299"],
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["May affect response to guanfacine/clonidine"]
        }
    },
    
    "rs4680_adhd": {
        "gene": "COMT",
        "name": "COMT ADHD variant",
        "risk_allele": "G",
        "category": "adhd",
        "conditions": ["ADHD executive function"],
        "evidence": "moderate",
        "note": "Same SNP as anxiety - context dependent effects",
        "references": ["PMID:17008816"]
    },
    
    # =========================================================================
    # SUBSTANCE USE DISORDERS
    # =========================================================================
    
    "rs1799971": {
        "gene": "OPRM1",
        "name": "Mu opioid receptor",
        "variant": "A118G",
        "risk_allele": "G",
        "category": "addiction",
        "conditions": ["Opioid dependence", "Alcohol dependence", "Pain sensitivity"],
        "evidence": "strong",
        "references": ["PMID:9689128", "PMID:12766631"],
        "interpretation": {
            "AA": "Normal opioid receptor function",
            "AG": "Reduced receptor binding, may need higher opioid doses",
            "GG": "Significantly reduced binding, altered addiction risk"
        },
        "actionable": {
            "priority": "medium",
            "action_type": "medical_alert",
            "recommendations": [
                "G carriers may require higher naltrexone doses for alcohol use disorder",
                "May affect opioid analgesic requirements",
                "Discuss with pain management specialists"
            ]
        }
    },
    
    "rs1229984": {
        "gene": "ADH1B",
        "name": "Alcohol dehydrogenase",
        "variant": "Arg47His",
        "risk_allele": "T",
        "category": "addiction",
        "conditions": ["Alcohol metabolism", "Alcohol dependence protection"],
        "evidence": "strong",
        "references": ["PMID:15457404"],
        "interpretation": {
            "CC": "Normal alcohol metabolism",
            "CT": "Faster acetaldehyde production (protective against alcoholism)",
            "TT": "Much faster metabolism, aversive response to alcohol (protective)"
        },
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["Variant common in East Asian populations"]
        }
    },
    
    "rs4680_dop": {
        "gene": "COMT",
        "name": "COMT addiction",
        "category": "addiction",
        "note": "Met/Met associated with nicotine dependence",
        "evidence": "moderate",
        "references": ["PMID:16287392"]
    },
    
    "rs16969968": {
        "gene": "CHRNA5",
        "name": "Nicotinic receptor",
        "risk_allele": "A",
        "category": "addiction",
        "conditions": ["Nicotine dependence", "Lung cancer risk"],
        "evidence": "strong",
        "references": ["PMID:18385739", "PMID:18385738"],
        "interpretation": {
            "GG": "Lower nicotine dependence risk",
            "AG": "Intermediate",
            "AA": "Higher nicotine dependence and cigarettes per day"
        },
        "actionable": {
            "priority": "medium",
            "action_type": "lifestyle",
            "recommendations": [
                "A carriers may find smoking cessation harder",
                "May benefit from intensive cessation support",
                "Varenicline may be particularly effective"
            ]
        }
    },
    
    # =========================================================================
    # AUTISM SPECTRUM
    # =========================================================================
    
    "rs4307059": {
        "gene": "CNTNAP2",
        "name": "Contactin-associated protein",
        "risk_allele": "T",
        "category": "autism",
        "conditions": ["Autism spectrum", "Language development"],
        "evidence": "moderate",
        "references": ["PMID:18179900"],
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["One of many ASD susceptibility variants"]
        }
    },
    
    "rs7794745": {
        "gene": "CNTNAP2",
        "name": "CNTNAP2 second variant",
        "risk_allele": "T",
        "category": "autism",
        "conditions": ["Autism spectrum"],
        "evidence": "moderate",
        "references": ["PMID:18179900"],
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["ASD is highly polygenic"]
        }
    },
    
    # =========================================================================
    # PSYCHIATRIC PHARMACOGENOMICS
    # =========================================================================
    
    "rs1045642": {
        "gene": "ABCB1",
        "name": "P-glycoprotein",
        "risk_allele": "T",
        "category": "pharma_psych",
        "conditions": ["Antidepressant brain penetration"],
        "evidence": "moderate",
        "references": ["PMID:16261197"],
        "interpretation": {
            "CC": "Normal P-gp function, standard drug levels in brain",
            "CT": "Intermediate",
            "TT": "Reduced P-gp efflux, may have higher brain drug levels"
        },
        "actionable": {
            "priority": "medium",
            "action_type": "medical_alert",
            "recommendations": [
                "May affect brain levels of many psychiatric medications",
                "Consider in non-response or unusual side effects"
            ]
        }
    },
    
    "rs6313": {
        "gene": "HTR2A",
        "name": "Serotonin 2A receptor",
        "risk_allele": "A",
        "category": "pharma_psych",
        "conditions": ["Antidepressant response", "Antipsychotic response"],
        "evidence": "moderate",
        "references": ["PMID:12403829"],
        "interpretation": {
            "GG": "Standard antidepressant response expected",
            "AG": "Intermediate",
            "AA": "May have altered response to SSRIs and atypicals"
        },
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["May inform antidepressant selection"]
        }
    },
    
    "rs6311": {
        "gene": "HTR2A",
        "name": "HTR2A promoter",
        "risk_allele": "A",
        "category": "pharma_psych",
        "conditions": ["Antidepressant response"],
        "evidence": "moderate",
        "references": ["PMID:12403829"],
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["Additional HTR2A variant"]
        }
    },
}

# Risk communication notes for mental health genetics
MENTAL_HEALTH_NOTES = """
IMPORTANT CONTEXT FOR MENTAL HEALTH GENETIC MARKERS:

1. HIGHLY POLYGENIC: Mental health conditions involve hundreds to thousands of
   genetic variants, each with tiny effects. No single marker is diagnostic.

2. ENVIRONMENT CRITICAL: Gene-environment interactions are substantial.
   Childhood trauma, stress, social support, and lifestyle significantly
   modify genetic risk.

3. NOT DETERMINISTIC: Having risk variants does not mean developing a condition.
   Many people with risk variants never develop symptoms.

4. HERITABILITY CONTEXT: While conditions like schizophrenia (~80%) and bipolar
   (~70%) are highly heritable, this doesn't mean genes are destiny.

5. TREATMENT IMPLICATIONS: Some variants (especially pharmacogenomic ones) may
   help guide medication selection and dosing.

6. STIGMA AWARENESS: Present genetic findings carefully to avoid reinforcing
   mental health stigma or genetic determinism.

7. ACTIONABLE FOCUS: Emphasize modifiable factors (sleep, exercise, stress
   management, social connection) that protect against genetic vulnerability.
"""
