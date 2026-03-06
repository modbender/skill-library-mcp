"""
Neurogenetics Markers
Source: Literature, GWAS

Genetic variants affecting cognition, behavior, mental health, and neurotransmission.
Important for understanding individual differences and medication response.

NOTE: These variants explain small % of variance. Environment matters enormously.
"""

NEURO_MARKERS = {
    # =========================================================================
    # DOPAMINE SYSTEM
    # =========================================================================
    "rs4680": {
        "gene": "COMT",
        "system": "Dopamine",
        "variant": "Val158Met",
        "effect_allele": "A",
        "effect": {
            "GG": "Val/Val 'Warrior' - fast dopamine clearance, stress resilient, executive function under pressure",
            "AG": "Val/Met - intermediate",
            "AA": "Met/Met 'Worrier' - slow dopamine clearance, better working memory, more stress sensitive"
        },
        "evidence": "moderate",
        "implications": {
            "cognition": "Met/Met: better baseline cognition, worse under stress",
            "stress": "Val/Val: better under pressure",
            "pain": "Met/Met: higher pain sensitivity",
            "medication": "Met/Met may be more sensitive to stimulants"
        },
        "actionable": {
            "priority": "informational",
            "recommendations": [
                "Met/Met: stress management techniques important",
                "Met/Met: may need less caffeine/stimulants",
                "Val/Val: may need more stimulation to focus"
            ]
        }
    },
    
    "rs1800497": {
        "gene": "DRD2/ANKK1",
        "system": "Dopamine",
        "variant": "Taq1A",
        "effect_allele": "A",
        "effect": {
            "GG": "A2/A2 - normal D2 receptor density",
            "AG": "A1/A2 - reduced D2 density",
            "AA": "A1/A1 - lowest D2 density"
        },
        "evidence": "moderate",
        "implications": {
            "reward": "A1 carriers: lower reward sensitivity, may need more stimulation",
            "addiction": "A1 carriers: increased addiction susceptibility",
            "weight": "A1 carriers: may use food for dopamine reward"
        }
    },
    
    "rs1079597": {
        "gene": "DRD2",
        "system": "Dopamine",
        "variant": "TaqIB",
        "effect_allele": "A",
        "effect": "Altered D2 receptor expression"
    },
    
    "rs1800955": {
        "gene": "DRD4",
        "system": "Dopamine",
        "variant": "-521 C>T",
        "effect_allele": "T",
        "effect": "T allele: higher DRD4 transcription",
        "implications": {
            "attention": "Associated with novelty seeking",
            "adhd": "Some association with ADHD symptoms"
        }
    },
    
    "rs40184": {
        "gene": "DAT1/SLC6A3",
        "system": "Dopamine",
        "variant": "Dopamine transporter",
        "effect_allele": "T",
        "effect": "Altered dopamine reuptake",
        "implications": {
            "stimulants": "Affects response to methylphenidate/Adderall"
        }
    },

    # =========================================================================
    # SEROTONIN SYSTEM
    # =========================================================================
    "rs25531": {
        "gene": "SLC6A4 (5-HTTLPR)",
        "system": "Serotonin",
        "variant": "Serotonin transporter",
        "effect_allele": "G",
        "effect": "Long allele vs short allele (complex)",
        "evidence": "moderate",
        "note": "Short allele associated with stress sensitivity (gene x environment)",
        "implications": {
            "depression": "Controversial - may increase depression risk with life stress",
            "anxiety": "Short allele: higher amygdala reactivity to negative stimuli",
            "medication": "Short allele may respond better to SSRIs (some studies)"
        }
    },
    
    "rs6311": {
        "gene": "HTR2A",
        "system": "Serotonin",
        "variant": "-1438 A>G",
        "effect_allele": "T",
        "effect": "Altered 5-HT2A receptor expression",
        "implications": {
            "antidepressants": "May affect SSRI response",
            "psychedelics": "5-HT2A is primary target of psychedelics"
        }
    },
    
    "rs6313": {
        "gene": "HTR2A",
        "system": "Serotonin",
        "variant": "T102C",
        "effect_allele": "A",
        "effect": "C/C genotype: altered receptor expression"
    },
    
    "rs6295": {
        "gene": "HTR1A",
        "system": "Serotonin",
        "variant": "C-1019G",
        "effect_allele": "G",
        "effect": "G allele: reduced 5-HT1A autoreceptor expression",
        "implications": {
            "depression": "G allele associated with depression in some studies",
            "antidepressants": "May affect response to SSRIs"
        }
    },

    # =========================================================================
    # BDNF / NEUROPLASTICITY
    # =========================================================================
    "rs6265": {
        "gene": "BDNF",
        "system": "Neuroplasticity",
        "variant": "Val66Met",
        "effect_allele": "T",
        "effect": {
            "CC": "Val/Val - normal BDNF secretion",
            "CT": "Val/Met - reduced activity-dependent secretion",
            "TT": "Met/Met - lowest BDNF secretion"
        },
        "evidence": "strong",
        "implications": {
            "memory": "Met carriers: slightly reduced episodic memory",
            "exercise": "Met carriers get MORE benefit from exercise (compensatory)",
            "depression": "Met allele associated with depression risk",
            "brain_volume": "Met carriers: smaller hippocampus"
        },
        "actionable": {
            "priority": "medium",
            "recommendations": [
                "Exercise is especially important for Met carriers",
                "Physical activity boosts BDNF",
                "Cognitive training may help"
            ]
        }
    },

    # =========================================================================
    # GABA SYSTEM
    # =========================================================================
    "rs211014": {
        "gene": "GABRA2",
        "system": "GABA",
        "effect_allele": "T",
        "effect": "Altered GABA-A receptor function",
        "implications": {
            "alcohol": "Associated with alcohol dependence risk",
            "anxiety": "May affect anxiety levels"
        }
    },
    
    "rs279858": {
        "gene": "GABRA2",
        "system": "GABA",
        "effect_allele": "A",
        "effect": "Altered inhibitory neurotransmission"
    },

    # =========================================================================
    # OXYTOCIN / SOCIAL BEHAVIOR
    # =========================================================================
    "rs53576": {
        "gene": "OXTR",
        "system": "Oxytocin",
        "variant": "Oxytocin receptor",
        "effect_allele": "G",
        "effect": {
            "AA": "Lower empathy scores, may be more resilient to social rejection",
            "AG": "Intermediate",
            "GG": "Higher empathy, more sensitive to social cues"
        },
        "evidence": "moderate",
        "implications": {
            "empathy": "GG: higher empathy and emotional sensitivity",
            "attachment": "Affects pair bonding and social behavior",
            "stress": "GG: seek more social support under stress"
        }
    },
    
    "rs2254298": {
        "gene": "OXTR",
        "system": "Oxytocin",
        "effect_allele": "A",
        "effect": "A allele: associated with social cognition differences"
    },

    # =========================================================================
    # STRESS RESPONSE (HPA AXIS)
    # =========================================================================
    "rs1360780": {
        "gene": "FKBP5",
        "system": "Stress/HPA",
        "effect_allele": "T",
        "effect": "T allele: prolonged cortisol response to stress",
        "evidence": "moderate",
        "implications": {
            "ptsd": "T allele + childhood trauma = increased PTSD risk",
            "depression": "Affects stress-related depression risk",
            "medication": "May affect glucocorticoid sensitivity"
        },
        "actionable": {
            "priority": "low",
            "recommendations": [
                "Stress management techniques important",
                "Trauma-informed care if needed"
            ]
        }
    },
    
    "rs6190": {
        "gene": "NR3C1",
        "system": "Glucocorticoid receptor",
        "effect_allele": "A",
        "effect": "ER22/23EK polymorphism - HPA axis regulation"
    },

    # =========================================================================
    # CIRCADIAN / SLEEP
    # =========================================================================
    "rs1801260": {
        "gene": "CLOCK",
        "system": "Circadian",
        "variant": "3111T>C",
        "effect_allele": "C",
        "effect": "C allele: evening chronotype (night owl)",
        "implications": {
            "sleep": "CC: more evening preference",
            "metabolism": "Evening types: higher metabolic syndrome risk",
            "shift_work": "Evening types may tolerate night shifts better"
        }
    },
    
    "rs57875989": {
        "gene": "PER2",
        "system": "Circadian",
        "variant": "FASPS mutation",
        "effect_allele": "G",
        "effect": "Familial Advanced Sleep Phase Syndrome (extremely rare)",
        "note": "Wake at 4-5am naturally, sleep at 7-8pm"
    },
    
    "rs2287161": {
        "gene": "CRY1",
        "system": "Circadian",
        "effect_allele": "C",
        "effect": "Affects circadian period length"
    },

    # =========================================================================
    # PSYCHIATRIC / MENTAL HEALTH
    # =========================================================================
    "rs1006737": {
        "gene": "CACNA1C",
        "system": "Calcium channel",
        "effect_allele": "A",
        "effect": "A allele: cross-disorder risk (bipolar, schizophrenia, MDD)",
        "evidence": "strong",
        "note": "Target of multiple psychiatric medications"
    },
    
    "rs4570625": {
        "gene": "TPH2",
        "system": "Serotonin synthesis",
        "effect_allele": "G",
        "effect": "G allele: increased amygdala reactivity to emotional faces",
        "implications": {
            "anxiety": "May increase anxiety symptoms"
        }
    },
    
    "rs10994336": {
        "gene": "ANK3",
        "system": "Neural",
        "effect_allele": "T",
        "effect": "Associated with bipolar disorder risk"
    },

    # =========================================================================
    # MEMORY / COGNITION
    # =========================================================================
    "rs429358": {
        "gene": "APOE",
        "system": "Lipid/Neural",
        "variant": "APOE ε4",
        "effect_allele": "C",
        "effect": "ε4 allele: Alzheimer's risk, may affect memory with age",
        "implications": {
            "alzheimer": "ε4/ε4: ~12x risk, ε3/ε4: ~3x risk",
            "memory": "ε4 may affect episodic memory in older adults",
            "exercise": "Exercise may be especially protective for ε4 carriers"
        }
    },
    
    "rs17070145": {
        "gene": "WWC1 (KIBRA)",
        "system": "Memory",
        "effect_allele": "T",
        "effect": "T allele: better episodic memory performance",
        "evidence": "moderate"
    },
    
    "rs1393350": {
        "gene": "TYR",
        "system": "Cognition",
        "effect_allele": "A",
        "effect": "Associated with cognitive performance"
    },

    # =========================================================================
    # ADDICTION RISK
    # =========================================================================
    "rs16969968": {
        "gene": "CHRNA5",
        "system": "Nicotinic receptor",
        "effect_allele": "A",
        "effect": "A allele: increased nicotine dependence risk",
        "evidence": "strong",
        "actionable": {
            "priority": "medium",
            "recommendations": [
                "Higher risk of nicotine addiction",
                "Never start smoking",
                "May need more intensive cessation support"
            ]
        }
    },
    
    "rs1229984": {
        "gene": "ADH1B",
        "system": "Alcohol metabolism",
        "effect_allele": "T",
        "effect": "T allele: fast alcohol metabolism, protective against alcoholism",
        "note": "Common in East Asian populations"
    },
    
    "rs671": {
        "gene": "ALDH2",
        "system": "Alcohol metabolism",
        "effect_allele": "A",
        "effect": "A allele: alcohol flush, strongly protective against alcoholism",
        "note": "BUT increased esophageal cancer if drinking despite flush"
    },
}
