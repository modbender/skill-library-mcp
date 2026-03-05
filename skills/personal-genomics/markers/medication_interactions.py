"""
Medication Interaction Checker v4.1.0
Cross-references user's pharmacogenomics markers with a comprehensive drug database.

Sources:
- PharmGKB Clinical Annotations
- CPIC (Clinical Pharmacogenetics Implementation Consortium) Guidelines
- FDA Table of Pharmacogenomic Biomarkers
- DrugBank

This module provides actionable medication safety information based on genetic profile.
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum


class InteractionSeverity(Enum):
    """Severity levels for drug-gene interactions."""
    CRITICAL = "critical"  # Life-threatening, contraindicated
    SERIOUS = "serious"    # Major dosing change or alternative needed
    MODERATE = "moderate"  # Significant but manageable
    MINOR = "minor"        # Awareness only
    INFORMATIONAL = "informational"  # No clear clinical action


@dataclass
class DrugInfo:
    """Drug information including aliases."""
    generic_name: str
    brand_names: List[str]
    drug_class: str
    common_uses: List[str]


# =============================================================================
# DRUG DATABASE - Common medications with aliases
# =============================================================================

DRUG_DATABASE: Dict[str, DrugInfo] = {
    # Antiplatelet agents
    "clopidogrel": DrugInfo(
        generic_name="clopidogrel",
        brand_names=["Plavix"],
        drug_class="Antiplatelet",
        common_uses=["Heart attack prevention", "Stroke prevention", "Stent thrombosis prevention"]
    ),
    "prasugrel": DrugInfo(
        generic_name="prasugrel",
        brand_names=["Effient"],
        drug_class="Antiplatelet",
        common_uses=["ACS with PCI", "Heart attack prevention"]
    ),
    "ticagrelor": DrugInfo(
        generic_name="ticagrelor",
        brand_names=["Brilinta", "Brilique"],
        drug_class="Antiplatelet",
        common_uses=["ACS", "Heart attack prevention"]
    ),
    
    # Anticoagulants
    "warfarin": DrugInfo(
        generic_name="warfarin",
        brand_names=["Coumadin", "Jantoven"],
        drug_class="Anticoagulant",
        common_uses=["Atrial fibrillation", "DVT/PE", "Mechanical heart valves"]
    ),
    
    # Opioid analgesics
    "codeine": DrugInfo(
        generic_name="codeine",
        brand_names=["Tylenol #3", "Tylenol #4"],
        drug_class="Opioid analgesic",
        common_uses=["Mild-moderate pain", "Cough suppression"]
    ),
    "tramadol": DrugInfo(
        generic_name="tramadol",
        brand_names=["Ultram", "ConZip", "Ultracet"],
        drug_class="Opioid analgesic",
        common_uses=["Moderate pain"]
    ),
    "oxycodone": DrugInfo(
        generic_name="oxycodone",
        brand_names=["OxyContin", "Roxicodone", "Percocet"],
        drug_class="Opioid analgesic",
        common_uses=["Moderate-severe pain"]
    ),
    "hydrocodone": DrugInfo(
        generic_name="hydrocodone",
        brand_names=["Vicodin", "Norco", "Lortab"],
        drug_class="Opioid analgesic",
        common_uses=["Moderate-severe pain"]
    ),
    "morphine": DrugInfo(
        generic_name="morphine",
        brand_names=["MS Contin", "Kadian", "Roxanol"],
        drug_class="Opioid analgesic",
        common_uses=["Severe pain", "Post-operative pain"]
    ),
    
    # Antidepressants - SSRIs
    "citalopram": DrugInfo(
        generic_name="citalopram",
        brand_names=["Celexa"],
        drug_class="SSRI antidepressant",
        common_uses=["Depression", "Anxiety"]
    ),
    "escitalopram": DrugInfo(
        generic_name="escitalopram",
        brand_names=["Lexapro"],
        drug_class="SSRI antidepressant",
        common_uses=["Depression", "GAD"]
    ),
    "sertraline": DrugInfo(
        generic_name="sertraline",
        brand_names=["Zoloft"],
        drug_class="SSRI antidepressant",
        common_uses=["Depression", "OCD", "PTSD", "Anxiety"]
    ),
    "fluoxetine": DrugInfo(
        generic_name="fluoxetine",
        brand_names=["Prozac", "Sarafem"],
        drug_class="SSRI antidepressant",
        common_uses=["Depression", "OCD", "Bulimia"]
    ),
    "paroxetine": DrugInfo(
        generic_name="paroxetine",
        brand_names=["Paxil", "Brisdelle"],
        drug_class="SSRI antidepressant",
        common_uses=["Depression", "Anxiety", "OCD", "PTSD"]
    ),
    "fluvoxamine": DrugInfo(
        generic_name="fluvoxamine",
        brand_names=["Luvox"],
        drug_class="SSRI antidepressant",
        common_uses=["OCD", "Social anxiety"]
    ),
    
    # Antidepressants - SNRIs
    "venlafaxine": DrugInfo(
        generic_name="venlafaxine",
        brand_names=["Effexor", "Effexor XR"],
        drug_class="SNRI antidepressant",
        common_uses=["Depression", "Anxiety", "Nerve pain"]
    ),
    "duloxetine": DrugInfo(
        generic_name="duloxetine",
        brand_names=["Cymbalta"],
        drug_class="SNRI antidepressant",
        common_uses=["Depression", "Nerve pain", "Fibromyalgia"]
    ),
    
    # Antidepressants - Tricyclics
    "amitriptyline": DrugInfo(
        generic_name="amitriptyline",
        brand_names=["Elavil"],
        drug_class="Tricyclic antidepressant",
        common_uses=["Depression", "Neuropathic pain", "Migraine prevention"]
    ),
    "nortriptyline": DrugInfo(
        generic_name="nortriptyline",
        brand_names=["Pamelor"],
        drug_class="Tricyclic antidepressant",
        common_uses=["Depression", "Neuropathic pain"]
    ),
    "imipramine": DrugInfo(
        generic_name="imipramine",
        brand_names=["Tofranil"],
        drug_class="Tricyclic antidepressant",
        common_uses=["Depression", "Bedwetting"]
    ),
    
    # Antipsychotics
    "risperidone": DrugInfo(
        generic_name="risperidone",
        brand_names=["Risperdal"],
        drug_class="Atypical antipsychotic",
        common_uses=["Schizophrenia", "Bipolar", "Irritability in autism"]
    ),
    "aripiprazole": DrugInfo(
        generic_name="aripiprazole",
        brand_names=["Abilify"],
        drug_class="Atypical antipsychotic",
        common_uses=["Schizophrenia", "Bipolar", "Depression adjunct"]
    ),
    "haloperidol": DrugInfo(
        generic_name="haloperidol",
        brand_names=["Haldol"],
        drug_class="Typical antipsychotic",
        common_uses=["Schizophrenia", "Agitation"]
    ),
    
    # PPIs
    "omeprazole": DrugInfo(
        generic_name="omeprazole",
        brand_names=["Prilosec", "Losec"],
        drug_class="Proton pump inhibitor",
        common_uses=["GERD", "Ulcers", "H. pylori"]
    ),
    "esomeprazole": DrugInfo(
        generic_name="esomeprazole",
        brand_names=["Nexium"],
        drug_class="Proton pump inhibitor",
        common_uses=["GERD", "Erosive esophagitis"]
    ),
    "pantoprazole": DrugInfo(
        generic_name="pantoprazole",
        brand_names=["Protonix"],
        drug_class="Proton pump inhibitor",
        common_uses=["GERD", "Zollinger-Ellison"]
    ),
    "lansoprazole": DrugInfo(
        generic_name="lansoprazole",
        brand_names=["Prevacid"],
        drug_class="Proton pump inhibitor",
        common_uses=["GERD", "Ulcers"]
    ),
    
    # Statins
    "simvastatin": DrugInfo(
        generic_name="simvastatin",
        brand_names=["Zocor"],
        drug_class="HMG-CoA reductase inhibitor",
        common_uses=["High cholesterol", "CVD prevention"]
    ),
    "atorvastatin": DrugInfo(
        generic_name="atorvastatin",
        brand_names=["Lipitor"],
        drug_class="HMG-CoA reductase inhibitor",
        common_uses=["High cholesterol", "CVD prevention"]
    ),
    "rosuvastatin": DrugInfo(
        generic_name="rosuvastatin",
        brand_names=["Crestor"],
        drug_class="HMG-CoA reductase inhibitor",
        common_uses=["High cholesterol", "CVD prevention"]
    ),
    "pravastatin": DrugInfo(
        generic_name="pravastatin",
        brand_names=["Pravachol"],
        drug_class="HMG-CoA reductase inhibitor",
        common_uses=["High cholesterol", "CVD prevention"]
    ),
    "lovastatin": DrugInfo(
        generic_name="lovastatin",
        brand_names=["Mevacor", "Altoprev"],
        drug_class="HMG-CoA reductase inhibitor",
        common_uses=["High cholesterol", "CVD prevention"]
    ),
    
    # Beta blockers
    "metoprolol": DrugInfo(
        generic_name="metoprolol",
        brand_names=["Lopressor", "Toprol-XL"],
        drug_class="Beta blocker",
        common_uses=["Hypertension", "Heart failure", "Angina"]
    ),
    "carvedilol": DrugInfo(
        generic_name="carvedilol",
        brand_names=["Coreg"],
        drug_class="Beta blocker",
        common_uses=["Heart failure", "Hypertension"]
    ),
    "propranolol": DrugInfo(
        generic_name="propranolol",
        brand_names=["Inderal"],
        drug_class="Beta blocker",
        common_uses=["Hypertension", "Tremor", "Migraine prevention"]
    ),
    "timolol": DrugInfo(
        generic_name="timolol",
        brand_names=["Timoptic", "Betimol"],
        drug_class="Beta blocker",
        common_uses=["Glaucoma", "Hypertension"]
    ),
    
    # Chemotherapy
    "5-fluorouracil": DrugInfo(
        generic_name="5-fluorouracil",
        brand_names=["Adrucil", "5-FU", "Efudex"],
        drug_class="Antimetabolite chemotherapy",
        common_uses=["Colorectal cancer", "Breast cancer", "Skin cancer"]
    ),
    "capecitabine": DrugInfo(
        generic_name="capecitabine",
        brand_names=["Xeloda"],
        drug_class="Antimetabolite chemotherapy",
        common_uses=["Colorectal cancer", "Breast cancer"]
    ),
    "tegafur": DrugInfo(
        generic_name="tegafur",
        brand_names=["UFT", "Tegafur-uracil"],
        drug_class="Antimetabolite chemotherapy",
        common_uses=["Colorectal cancer"]
    ),
    "tamoxifen": DrugInfo(
        generic_name="tamoxifen",
        brand_names=["Nolvadex", "Soltamox"],
        drug_class="Selective estrogen receptor modulator",
        common_uses=["Breast cancer treatment/prevention"]
    ),
    "irinotecan": DrugInfo(
        generic_name="irinotecan",
        brand_names=["Camptosar"],
        drug_class="Topoisomerase inhibitor",
        common_uses=["Colorectal cancer"]
    ),
    "mercaptopurine": DrugInfo(
        generic_name="mercaptopurine",
        brand_names=["Purinethol", "6-MP"],
        drug_class="Antimetabolite",
        common_uses=["Leukemia", "IBD"]
    ),
    "azathioprine": DrugInfo(
        generic_name="azathioprine",
        brand_names=["Imuran", "Azasan"],
        drug_class="Immunosuppressant",
        common_uses=["Organ transplant", "IBD", "Rheumatoid arthritis"]
    ),
    
    # Antiepileptics
    "phenytoin": DrugInfo(
        generic_name="phenytoin",
        brand_names=["Dilantin"],
        drug_class="Antiepileptic",
        common_uses=["Seizures"]
    ),
    "carbamazepine": DrugInfo(
        generic_name="carbamazepine",
        brand_names=["Tegretol", "Carbatrol"],
        drug_class="Antiepileptic",
        common_uses=["Seizures", "Trigeminal neuralgia", "Bipolar"]
    ),
    "oxcarbazepine": DrugInfo(
        generic_name="oxcarbazepine",
        brand_names=["Trileptal"],
        drug_class="Antiepileptic",
        common_uses=["Seizures"]
    ),
    
    # Antifungals
    "voriconazole": DrugInfo(
        generic_name="voriconazole",
        brand_names=["Vfend"],
        drug_class="Triazole antifungal",
        common_uses=["Invasive aspergillosis", "Serious fungal infections"]
    ),
    
    # Gout
    "allopurinol": DrugInfo(
        generic_name="allopurinol",
        brand_names=["Zyloprim", "Aloprim"],
        drug_class="Xanthine oxidase inhibitor",
        common_uses=["Gout", "Hyperuricemia"]
    ),
    
    # HIV
    "abacavir": DrugInfo(
        generic_name="abacavir",
        brand_names=["Ziagen"],
        drug_class="NRTI antiretroviral",
        common_uses=["HIV infection"]
    ),
    
    # NSAIDs
    "celecoxib": DrugInfo(
        generic_name="celecoxib",
        brand_names=["Celebrex"],
        drug_class="COX-2 inhibitor",
        common_uses=["Arthritis", "Pain", "Inflammation"]
    ),
    "ibuprofen": DrugInfo(
        generic_name="ibuprofen",
        brand_names=["Advil", "Motrin", "Nurofen"],
        drug_class="NSAID",
        common_uses=["Pain", "Inflammation", "Fever"]
    ),
    "naproxen": DrugInfo(
        generic_name="naproxen",
        brand_names=["Aleve", "Naprosyn"],
        drug_class="NSAID",
        common_uses=["Pain", "Inflammation", "Arthritis"]
    ),
    
    # Muscle relaxants
    "cyclobenzaprine": DrugInfo(
        generic_name="cyclobenzaprine",
        brand_names=["Flexeril", "Amrix"],
        drug_class="Muscle relaxant",
        common_uses=["Muscle spasms", "Back pain"]
    ),
    
    # ADHD medications
    "atomoxetine": DrugInfo(
        generic_name="atomoxetine",
        brand_names=["Strattera"],
        drug_class="SNRI (ADHD)",
        common_uses=["ADHD"]
    ),
    
    # Antiemetics
    "ondansetron": DrugInfo(
        generic_name="ondansetron",
        brand_names=["Zofran"],
        drug_class="5-HT3 antagonist",
        common_uses=["Nausea/vomiting", "Chemotherapy-induced nausea"]
    ),
    
    # Immunosuppressants
    "tacrolimus": DrugInfo(
        generic_name="tacrolimus",
        brand_names=["Prograf", "Envarsus"],
        drug_class="Calcineurin inhibitor",
        common_uses=["Organ transplant", "Atopic dermatitis"]
    ),
}


# =============================================================================
# GENE-DRUG INTERACTIONS DATABASE
# =============================================================================

GENE_DRUG_INTERACTIONS: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # CYP2D6 Interactions
    # =========================================================================
    "CYP2D6": {
        "poor_metabolizer": {
            "markers": ["rs3892097", "rs5030655", "rs28371706", "rs28371725"],
            "risk_genotypes": {"rs3892097": ["AA", "GA"], "rs5030655": ["del"]},
            "drugs": {
                "codeine": {
                    "severity": InteractionSeverity.SERIOUS,
                    "effect": "Codeine is a PRODRUG - requires CYP2D6 to convert to morphine",
                    "recommendation": "AVOID codeine. Use morphine or oxymorphone instead.",
                    "alternative": ["morphine", "oxymorphone", "fentanyl"],
                    "pmid": ["22205192", "17622591"]
                },
                "tramadol": {
                    "severity": InteractionSeverity.SERIOUS,
                    "effect": "Reduced conversion to active metabolite O-desmethyltramadol",
                    "recommendation": "AVOID tramadol. May be ineffective for pain.",
                    "alternative": ["morphine", "oxymorphone"],
                    "pmid": ["17622591"]
                },
                "tamoxifen": {
                    "severity": InteractionSeverity.SERIOUS,
                    "effect": "Reduced conversion to active metabolite endoxifen",
                    "recommendation": "Consider alternative or aromatase inhibitor if post-menopausal.",
                    "alternative": ["aromatase inhibitors"],
                    "pmid": ["22205192"]
                },
                "ondansetron": {
                    "severity": InteractionSeverity.MODERATE,
                    "effect": "Reduced metabolism - increased exposure",
                    "recommendation": "May need dose reduction for ondansetron.",
                    "pmid": ["25974703"]
                },
                "risperidone": {
                    "severity": InteractionSeverity.MODERATE,
                    "effect": "Increased risperidone levels",
                    "recommendation": "Consider 50% dose reduction.",
                    "pmid": ["19724245"]
                },
                "aripiprazole": {
                    "severity": InteractionSeverity.MODERATE,
                    "effect": "Increased aripiprazole levels",
                    "recommendation": "Consider 50% dose reduction.",
                    "pmid": ["27997040"]
                },
                "metoprolol": {
                    "severity": InteractionSeverity.MODERATE,
                    "effect": "Increased metoprolol exposure and beta-blockade",
                    "recommendation": "Consider alternative beta-blocker or lower dose.",
                    "alternative": ["atenolol", "bisoprolol"],
                    "pmid": ["27622575"]
                },
            },
            "ultrarapid_metabolizer": {
                "markers": ["rs16947"],  # Gene duplication indicator
                "drugs": {
                    "codeine": {
                        "severity": InteractionSeverity.CRITICAL,
                        "effect": "RAPID conversion to morphine - RISK OF FATAL OVERDOSE",
                        "recommendation": "AVOID codeine. HIGH RISK of respiratory depression and death.",
                        "alternative": ["morphine at reduced dose", "non-opioid alternatives"],
                        "pmid": ["22205192", "17622591"],
                        "fda_warning": True
                    },
                    "tramadol": {
                        "severity": InteractionSeverity.SERIOUS,
                        "effect": "Rapid conversion to active metabolite - overdose risk",
                        "recommendation": "AVOID tramadol or use 50% dose.",
                        "pmid": ["17622591"]
                    },
                }
            }
        }
    },
    
    # =========================================================================
    # CYP2C19 Interactions
    # =========================================================================
    "CYP2C19": {
        "poor_metabolizer": {
            "markers": ["rs4244285", "rs4986893"],
            "risk_genotypes": {"rs4244285": ["AA", "GA"], "rs4986893": ["AA", "GA"]},
            "drugs": {
                "clopidogrel": {
                    "severity": InteractionSeverity.CRITICAL,
                    "effect": "Clopidogrel is a PRODRUG - reduced activation to active metabolite",
                    "recommendation": "USE ALTERNATIVE antiplatelet. Prasugrel or ticagrelor recommended.",
                    "alternative": ["prasugrel", "ticagrelor"],
                    "pmid": ["20801498", "22992668"],
                    "fda_warning": True
                },
                "omeprazole": {
                    "severity": InteractionSeverity.MODERATE,
                    "effect": "Increased omeprazole exposure - may be more effective",
                    "recommendation": "May use standard or lower dose.",
                    "pmid": ["26417955"]
                },
                "esomeprazole": {
                    "severity": InteractionSeverity.MODERATE,
                    "effect": "Increased esomeprazole exposure",
                    "recommendation": "May use standard or lower dose.",
                    "pmid": ["26417955"]
                },
                "voriconazole": {
                    "severity": InteractionSeverity.MODERATE,
                    "effect": "Increased voriconazole levels",
                    "recommendation": "Consider dose reduction by 50%.",
                    "pmid": ["26417955"]
                },
                "citalopram": {
                    "severity": InteractionSeverity.MODERATE,
                    "effect": "Increased citalopram exposure",
                    "recommendation": "Do not exceed 20mg/day. Consider alternative.",
                    "alternative": ["sertraline", "escitalopram at lower dose"],
                    "pmid": ["26417955"]
                },
                "escitalopram": {
                    "severity": InteractionSeverity.MODERATE,
                    "effect": "Increased escitalopram exposure",
                    "recommendation": "Consider 50% dose reduction.",
                    "pmid": ["26417955"]
                },
            }
        },
        "ultrarapid_metabolizer": {
            "markers": ["rs12248560"],
            "risk_genotypes": {"rs12248560": ["TT", "CT"]},
            "drugs": {
                "omeprazole": {
                    "severity": InteractionSeverity.MODERATE,
                    "effect": "Rapid metabolism - reduced efficacy",
                    "recommendation": "May need higher dose or alternative PPI.",
                    "pmid": ["26417955"]
                },
                "citalopram": {
                    "severity": InteractionSeverity.MODERATE,
                    "effect": "Rapid metabolism - may need higher dose",
                    "recommendation": "Monitor response, may need dose increase.",
                    "pmid": ["26417955"]
                },
            }
        }
    },
    
    # =========================================================================
    # CYP2C9 Interactions
    # =========================================================================
    "CYP2C9": {
        "poor_metabolizer": {
            "markers": ["rs1799853", "rs1057910"],
            "risk_genotypes": {
                "rs1799853": ["TT", "CT"],  # *2
                "rs1057910": ["CC", "AC"]   # *3
            },
            "drugs": {
                "warfarin": {
                    "severity": InteractionSeverity.CRITICAL,
                    "effect": "Significantly reduced warfarin clearance - HIGH BLEEDING RISK",
                    "recommendation": "Use pharmacogenomic dosing algorithm. Typical reduction 25-50%.",
                    "alternative": ["DOACs (apixaban, rivaroxaban)"],
                    "pmid": ["21900891", "26417955"],
                    "fda_warning": True
                },
                "phenytoin": {
                    "severity": InteractionSeverity.SERIOUS,
                    "effect": "Reduced clearance - toxicity risk",
                    "recommendation": "Reduce dose by 25-50%. Monitor levels closely.",
                    "pmid": ["26417955"]
                },
                "celecoxib": {
                    "severity": InteractionSeverity.MODERATE,
                    "effect": "Increased celecoxib exposure",
                    "recommendation": "Start with lowest dose.",
                    "pmid": ["26417955"]
                },
            }
        }
    },
    
    # =========================================================================
    # VKORC1 Interactions
    # =========================================================================
    "VKORC1": {
        "high_sensitivity": {
            "markers": ["rs9923231"],
            "risk_genotypes": {"rs9923231": ["AA", "GA"]},
            "drugs": {
                "warfarin": {
                    "severity": InteractionSeverity.SERIOUS,
                    "effect": "Increased warfarin sensitivity - lower dose required",
                    "recommendation": "Use pharmacogenomic dosing. Typical 25-35% dose reduction.",
                    "pmid": ["21900891"],
                    "fda_warning": True
                }
            }
        }
    },
    
    # =========================================================================
    # DPYD Interactions - CRITICAL
    # =========================================================================
    "DPYD": {
        "deficient": {
            "markers": ["rs3918290", "rs55886062", "rs67376798"],
            "risk_genotypes": {
                "rs3918290": ["AA", "GA"],   # *2A - most severe
                "rs55886062": ["AA", "CA"],  # *13
                "rs67376798": ["AA", "TA"]   # D949V
            },
            "drugs": {
                "5-fluorouracil": {
                    "severity": InteractionSeverity.CRITICAL,
                    "effect": "FATAL TOXICITY RISK - Cannot metabolize fluoropyrimidines",
                    "recommendation": "CONTRAINDICATED if homozygous. Reduce dose 50% if heterozygous.",
                    "alternative": ["Non-fluoropyrimidine chemotherapy"],
                    "pmid": ["29152729", "28881920"],
                    "fda_warning": True
                },
                "capecitabine": {
                    "severity": InteractionSeverity.CRITICAL,
                    "effect": "FATAL TOXICITY RISK - Capecitabine converted to 5-FU",
                    "recommendation": "CONTRAINDICATED if homozygous. Reduce dose 50% if heterozygous.",
                    "pmid": ["29152729"],
                    "fda_warning": True
                },
                "tegafur": {
                    "severity": InteractionSeverity.CRITICAL,
                    "effect": "FATAL TOXICITY RISK",
                    "recommendation": "CONTRAINDICATED if deficient.",
                    "pmid": ["29152729"],
                    "fda_warning": True
                }
            }
        }
    },
    
    # =========================================================================
    # TPMT Interactions
    # =========================================================================
    "TPMT": {
        "deficient": {
            "markers": ["rs1800462", "rs1800460", "rs1142345"],
            "risk_genotypes": {
                "rs1800462": ["AA", "GA"],
                "rs1800460": ["AA", "GA"],
                "rs1142345": ["AA", "GA"]
            },
            "drugs": {
                "azathioprine": {
                    "severity": InteractionSeverity.CRITICAL,
                    "effect": "SEVERE myelosuppression - life-threatening",
                    "recommendation": "Reduce dose 90% if homozygous deficient. 50% if heterozygous.",
                    "pmid": ["21270794"],
                    "fda_warning": True
                },
                "mercaptopurine": {
                    "severity": InteractionSeverity.CRITICAL,
                    "effect": "SEVERE myelosuppression - life-threatening",
                    "recommendation": "Reduce dose 90% if homozygous deficient. 50% if heterozygous.",
                    "pmid": ["21270794"],
                    "fda_warning": True
                }
            }
        }
    },
    
    # =========================================================================
    # SLCO1B1 Interactions
    # =========================================================================
    "SLCO1B1": {
        "reduced_function": {
            "markers": ["rs4149056"],
            "risk_genotypes": {"rs4149056": ["CC", "CT"]},
            "drugs": {
                "simvastatin": {
                    "severity": InteractionSeverity.SERIOUS,
                    "effect": "Increased myopathy risk - 5-17x higher with CC genotype",
                    "recommendation": "Limit to 20mg/day or use alternative statin (pravastatin, rosuvastatin).",
                    "alternative": ["pravastatin", "rosuvastatin", "atorvastatin (lower risk)"],
                    "pmid": ["22617227"],
                    "fda_warning": True
                },
                "atorvastatin": {
                    "severity": InteractionSeverity.MODERATE,
                    "effect": "Increased myopathy risk (lower than simvastatin)",
                    "recommendation": "Monitor for muscle symptoms. Consider lower dose.",
                    "pmid": ["22617227"]
                },
                "lovastatin": {
                    "severity": InteractionSeverity.MODERATE,
                    "effect": "Increased myopathy risk",
                    "recommendation": "Consider alternative statin.",
                    "alternative": ["pravastatin", "rosuvastatin"],
                    "pmid": ["22617227"]
                }
            }
        }
    },
    
    # =========================================================================
    # UGT1A1 Interactions
    # =========================================================================
    "UGT1A1": {
        "reduced_function": {
            "markers": ["rs8175347"],  # *28 allele (TA repeat)
            "risk_genotypes": {"rs8175347": ["7/7"]},  # Homozygous *28
            "drugs": {
                "irinotecan": {
                    "severity": InteractionSeverity.SERIOUS,
                    "effect": "Reduced glucuronidation - increased neutropenia and diarrhea risk",
                    "recommendation": "Reduce initial dose by 25-30%.",
                    "pmid": ["26417955"],
                    "fda_warning": True
                }
            }
        }
    },
    
    # =========================================================================
    # HLA-B*57:01 Interaction
    # =========================================================================
    "HLA-B*57:01": {
        "positive": {
            "markers": ["rs2395029"],
            "risk_genotypes": {"rs2395029": ["GG", "GT"]},
            "drugs": {
                "abacavir": {
                    "severity": InteractionSeverity.CRITICAL,
                    "effect": "5-8% risk of hypersensitivity reaction - potentially FATAL",
                    "recommendation": "DO NOT USE abacavir. Contraindicated.",
                    "alternative": ["tenofovir", "other NRTIs"],
                    "pmid": ["18192772"],
                    "fda_warning": True
                }
            }
        }
    },
    
    # =========================================================================
    # HLA-B*15:02 Interaction (important in Asian populations)
    # =========================================================================
    "HLA-B*15:02": {
        "positive": {
            "markers": ["rs3909184"],
            "risk_genotypes": {"rs3909184": ["TT", "CT"]},
            "drugs": {
                "carbamazepine": {
                    "severity": InteractionSeverity.CRITICAL,
                    "effect": "High risk of Stevens-Johnson syndrome/TEN - potentially FATAL",
                    "recommendation": "Screen before prescribing in Asian ancestry. AVOID if positive.",
                    "alternative": ["levetiracetam", "lamotrigine with caution"],
                    "pmid": ["21412232"],
                    "fda_warning": True
                },
                "oxcarbazepine": {
                    "severity": InteractionSeverity.SERIOUS,
                    "effect": "Increased SJS/TEN risk",
                    "recommendation": "AVOID if HLA-B*15:02 positive.",
                    "pmid": ["21412232"]
                },
                "phenytoin": {
                    "severity": InteractionSeverity.SERIOUS,
                    "effect": "Increased SJS/TEN risk",
                    "recommendation": "Consider alternative if HLA-B*15:02 positive.",
                    "pmid": ["21412232"]
                }
            }
        }
    },
    
    # =========================================================================
    # HLA-B*58:01 Interaction
    # =========================================================================
    "HLA-B*58:01": {
        "positive": {
            "markers": ["rs9263726"],
            "risk_genotypes": {"rs9263726": ["CC", "CT"]},
            "drugs": {
                "allopurinol": {
                    "severity": InteractionSeverity.SERIOUS,
                    "effect": "Increased risk of severe cutaneous adverse reactions (SCAR)",
                    "recommendation": "Screen in at-risk populations. Use febuxostat if positive.",
                    "alternative": ["febuxostat"],
                    "pmid": ["26417955"],
                    "fda_warning": True
                }
            }
        }
    },
    
    # =========================================================================
    # CYP3A5 Interactions
    # =========================================================================
    "CYP3A5": {
        "expresser": {
            "markers": ["rs776746"],
            "risk_genotypes": {"rs776746": ["AA", "GA"]},  # *1 allele
            "drugs": {
                "tacrolimus": {
                    "severity": InteractionSeverity.MODERATE,
                    "effect": "Increased tacrolimus clearance - may need higher dose",
                    "recommendation": "May require 1.5-2x higher dose to achieve target levels.",
                    "pmid": ["26417955"]
                }
            }
        }
    }
}


# =============================================================================
# MEDICATION INTERACTION CHECKER FUNCTIONS
# =============================================================================

def normalize_drug_name(drug_name: str) -> Optional[str]:
    """
    Normalize drug name to generic name.
    Handles brand names, common misspellings, and variations.
    """
    drug_lower = drug_name.lower().strip()
    
    # Direct match to generic name
    if drug_lower in DRUG_DATABASE:
        return drug_lower
    
    # Search brand names
    for generic, info in DRUG_DATABASE.items():
        for brand in info.brand_names:
            if drug_lower == brand.lower():
                return generic
    
    # Handle common aliases and abbreviations
    aliases = {
        "5-fu": "5-fluorouracil",
        "5fu": "5-fluorouracil",
        "fluorouracil": "5-fluorouracil",
        "plavix": "clopidogrel",
        "coumadin": "warfarin",
        "tylenol 3": "codeine",
        "tylenol #3": "codeine",
        "vicodin": "hydrocodone",
        "norco": "hydrocodone",
        "percocet": "oxycodone",
        "prilosec": "omeprazole",
        "nexium": "esomeprazole",
        "lipitor": "atorvastatin",
        "zocor": "simvastatin",
        "crestor": "rosuvastatin",
        "prozac": "fluoxetine",
        "zoloft": "sertraline",
        "lexapro": "escitalopram",
        "celexa": "citalopram",
        "paxil": "paroxetine",
        "effexor": "venlafaxine",
        "cymbalta": "duloxetine",
        "xanax": "alprazolam",
        "valium": "diazepam",
        "advil": "ibuprofen",
        "motrin": "ibuprofen",
        "aleve": "naproxen",
    }
    
    return aliases.get(drug_lower)


def determine_metabolizer_status(gene: str, genotypes: Dict[str, str]) -> Dict[str, Any]:
    """Determine metabolizer status for a gene based on genotypes."""
    status_info = {
        "gene": gene,
        "status": "normal",
        "confidence": "low",
        "relevant_variants": []
    }
    
    gene_interactions = GENE_DRUG_INTERACTIONS.get(gene, {})
    
    for status_type, status_data in gene_interactions.items():
        markers = status_data.get("markers", [])
        risk_genotypes = status_data.get("risk_genotypes", {})
        
        for marker in markers:
            if marker in genotypes:
                geno = genotypes[marker]
                status_info["relevant_variants"].append({
                    "rsid": marker,
                    "genotype": geno
                })
                
                if marker in risk_genotypes:
                    if geno in risk_genotypes[marker]:
                        status_info["status"] = status_type
                        status_info["confidence"] = "high"
    
    if status_info["relevant_variants"]:
        status_info["confidence"] = "moderate" if status_info["confidence"] == "low" else "high"
    
    return status_info


def check_medication_interactions(
    medications: List[str],
    genotypes: Dict[str, str]
) -> Dict[str, Any]:
    """
    Check a list of medications against user's pharmacogenomic profile.
    
    Args:
        medications: List of medication names (generic or brand)
        genotypes: Dict of rsid -> genotype
    
    Returns:
        Comprehensive interaction report
    """
    results = {
        "medications_checked": [],
        "medications_not_found": [],
        "critical_interactions": [],
        "serious_interactions": [],
        "moderate_interactions": [],
        "minor_interactions": [],
        "safe_medications": [],
        "metabolizer_status": {},
        "summary": {},
        "recommendations": []
    }
    
    # First, determine metabolizer status for all relevant genes
    for gene in GENE_DRUG_INTERACTIONS.keys():
        status = determine_metabolizer_status(gene, genotypes)
        if status["relevant_variants"]:
            results["metabolizer_status"][gene] = status
    
    # Check each medication
    for med in medications:
        generic = normalize_drug_name(med)
        
        if not generic:
            results["medications_not_found"].append({
                "input": med,
                "note": "Drug not found in database. Manual review recommended."
            })
            continue
        
        drug_info = DRUG_DATABASE.get(generic)
        med_entry = {
            "input": med,
            "generic_name": generic,
            "brand_names": drug_info.brand_names if drug_info else [],
            "drug_class": drug_info.drug_class if drug_info else "Unknown",
            "interactions": []
        }
        
        # Check against all gene-drug interactions
        has_interaction = False
        for gene, gene_data in GENE_DRUG_INTERACTIONS.items():
            for status_type, status_data in gene_data.items():
                drugs = status_data.get("drugs", {})
                
                if generic in drugs:
                    # Check if user has the relevant genotype
                    status = results["metabolizer_status"].get(gene, {})
                    
                    if status.get("status") == status_type:
                        interaction = drugs[generic]
                        interaction_entry = {
                            "gene": gene,
                            "metabolizer_status": status_type,
                            "genotypes": status.get("relevant_variants", []),
                            "severity": interaction["severity"].value,
                            "effect": interaction["effect"],
                            "recommendation": interaction["recommendation"],
                            "alternatives": interaction.get("alternative", []),
                            "pmid": interaction.get("pmid", []),
                            "fda_warning": interaction.get("fda_warning", False)
                        }
                        
                        med_entry["interactions"].append(interaction_entry)
                        has_interaction = True
                        
                        # Categorize by severity
                        if interaction["severity"] == InteractionSeverity.CRITICAL:
                            results["critical_interactions"].append({
                                "medication": generic,
                                **interaction_entry
                            })
                        elif interaction["severity"] == InteractionSeverity.SERIOUS:
                            results["serious_interactions"].append({
                                "medication": generic,
                                **interaction_entry
                            })
                        elif interaction["severity"] == InteractionSeverity.MODERATE:
                            results["moderate_interactions"].append({
                                "medication": generic,
                                **interaction_entry
                            })
                        else:
                            results["minor_interactions"].append({
                                "medication": generic,
                                **interaction_entry
                            })
        
        if not has_interaction:
            results["safe_medications"].append({
                "medication": generic,
                "note": "No pharmacogenomic interactions detected based on available data"
            })
        
        results["medications_checked"].append(med_entry)
    
    # Generate summary
    results["summary"] = {
        "total_medications": len(medications),
        "medications_checked": len(results["medications_checked"]),
        "not_in_database": len(results["medications_not_found"]),
        "critical_count": len(results["critical_interactions"]),
        "serious_count": len(results["serious_interactions"]),
        "moderate_count": len(results["moderate_interactions"]),
        "minor_count": len(results["minor_interactions"]),
        "safe_count": len(results["safe_medications"]),
        "has_critical": len(results["critical_interactions"]) > 0,
        "requires_review": len(results["critical_interactions"]) + len(results["serious_interactions"]) > 0
    }
    
    # Generate top recommendations
    if results["critical_interactions"]:
        results["recommendations"].append({
            "priority": "critical",
            "message": f"⚠️ {len(results['critical_interactions'])} CRITICAL drug-gene interaction(s) detected. "
                      f"Share with healthcare provider IMMEDIATELY."
        })
        for interaction in results["critical_interactions"]:
            results["recommendations"].append({
                "priority": "critical",
                "message": f"🚫 {interaction['medication'].upper()}: {interaction['recommendation']}"
            })
    
    if results["serious_interactions"]:
        results["recommendations"].append({
            "priority": "high",
            "message": f"⚠️ {len(results['serious_interactions'])} serious interaction(s) detected. "
                      f"Discuss with prescriber."
        })
    
    return results


def get_drug_info(drug_name: str) -> Optional[Dict[str, Any]]:
    """Get information about a specific drug."""
    generic = normalize_drug_name(drug_name)
    if not generic:
        return None
    
    info = DRUG_DATABASE.get(generic)
    if not info:
        return None
    
    return {
        "generic_name": info.generic_name,
        "brand_names": info.brand_names,
        "drug_class": info.drug_class,
        "common_uses": info.common_uses,
        "pharmacogenomic_genes": _get_relevant_genes(generic)
    }


def _get_relevant_genes(drug_name: str) -> List[str]:
    """Get list of genes with known interactions for a drug."""
    relevant = []
    for gene, gene_data in GENE_DRUG_INTERACTIONS.items():
        for status_type, status_data in gene_data.items():
            if drug_name in status_data.get("drugs", {}):
                relevant.append(gene)
                break
    return relevant


def list_all_drugs() -> List[str]:
    """List all drugs in the database."""
    return sorted(DRUG_DATABASE.keys())


def search_drugs(query: str) -> List[Dict[str, str]]:
    """Search drugs by name (generic or brand)."""
    query_lower = query.lower()
    results = []
    
    for generic, info in DRUG_DATABASE.items():
        if query_lower in generic:
            results.append({"generic": generic, "brands": info.brand_names})
        else:
            for brand in info.brand_names:
                if query_lower in brand.lower():
                    results.append({"generic": generic, "brands": info.brand_names})
                    break
    
    return results
