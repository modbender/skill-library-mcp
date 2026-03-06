"""
Vision and Hearing Genetics Markers.
Markers for eye diseases, hearing conditions, and sensory traits.
"""

VISION_MARKERS = {
    # =========================================================================
    # AGE-RELATED MACULAR DEGENERATION (AMD)
    # =========================================================================
    
    "rs1061170": {
        "gene": "CFH",
        "name": "Complement Factor H Y402H",
        "variant": "Y402H",
        "risk_allele": "C",
        "category": "amd",
        "conditions": ["Age-related macular degeneration"],
        "evidence": "strong",
        "references": ["PMID:15761122", "PMID:15870199"],
        "interpretation": {
            "TT": "Lower AMD risk",
            "TC": "~2.5x AMD risk",
            "CC": "~5-7x AMD risk"
        },
        "clinical_notes": "Strongest genetic risk factor for AMD",
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": [
                "Annual comprehensive eye exams after age 50",
                "AREDS2 supplements may slow progression if AMD develops",
                "Don't smoke (dramatically increases risk)",
                "Protect eyes from UV light",
                "Leafy greens, fish may be protective"
            ]
        }
    },
    
    "rs10490924": {
        "gene": "ARMS2",
        "name": "ARMS2 A69S",
        "variant": "A69S",
        "risk_allele": "T",
        "category": "amd",
        "conditions": ["Age-related macular degeneration"],
        "evidence": "strong",
        "references": ["PMID:16174643", "PMID:17053108"],
        "interpretation": {
            "GG": "Lower AMD risk",
            "GT": "~2.5x risk",
            "TT": "~8x AMD risk"
        },
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": [
                "Second strongest AMD genetic risk factor",
                "Combined with CFH: very high risk if both risk genotypes",
                "Smoking cessation critical"
            ]
        }
    },
    
    "rs9332739": {
        "gene": "C2",
        "name": "Complement C2 AMD protective",
        "risk_allele": "G",
        "category": "amd",
        "conditions": ["Age-related macular degeneration"],
        "evidence": "strong",
        "references": ["PMID:16518403"],
        "note": "Protective variant - reduces AMD risk"
    },
    
    "rs641153": {
        "gene": "CFB",
        "name": "Complement Factor B",
        "risk_allele": "A",
        "category": "amd",
        "conditions": ["AMD protection"],
        "evidence": "strong",
        "references": ["PMID:16518403"],
        "note": "Protective variant"
    },
    
    # =========================================================================
    # GLAUCOMA
    # =========================================================================
    
    "rs2165241": {
        "gene": "LOXL1",
        "name": "LOXL1 exfoliation glaucoma",
        "risk_allele": "T",
        "category": "glaucoma",
        "conditions": ["Exfoliation glaucoma", "Pseudoexfoliation syndrome"],
        "evidence": "strong",
        "references": ["PMID:17690259"],
        "note": "Strongest genetic risk for exfoliation glaucoma",
        "actionable": {
            "priority": "medium",
            "action_type": "screening",
            "recommendations": [
                "Regular intraocular pressure monitoring",
                "Annual comprehensive eye exams",
                "Especially important after age 50"
            ]
        }
    },
    
    "rs3825942": {
        "gene": "LOXL1",
        "name": "LOXL1 G153D",
        "variant": "G153D",
        "risk_allele": "G",
        "category": "glaucoma",
        "conditions": ["Exfoliation glaucoma"],
        "evidence": "strong",
        "references": ["PMID:17690259"],
        "note": "Population-specific risk direction"
    },
    
    "rs1048661": {
        "gene": "LOXL1",
        "name": "LOXL1 R141L",
        "risk_allele": "G",
        "category": "glaucoma",
        "conditions": ["Exfoliation syndrome"],
        "evidence": "strong",
        "references": ["PMID:17690259"]
    },
    
    "rs4236601": {
        "gene": "CAV1-CAV2",
        "name": "Primary open-angle glaucoma",
        "risk_allele": "A",
        "category": "glaucoma",
        "conditions": ["Primary open-angle glaucoma"],
        "evidence": "strong",
        "references": ["PMID:20835238"],
        "actionable": {
            "priority": "medium",
            "action_type": "screening",
            "recommendations": [
                "Baseline eye pressure measurement",
                "Visual field testing if elevated IOP",
                "Family history increases importance"
            ]
        }
    },
    
    "rs10483727": {
        "gene": "SIX1-SIX6",
        "name": "POAG SIX6",
        "risk_allele": "A",
        "category": "glaucoma",
        "conditions": ["Primary open-angle glaucoma"],
        "evidence": "strong",
        "references": ["PMID:22570617"]
    },
    
    "rs7555523": {
        "gene": "TMCO1",
        "name": "TMCO1 glaucoma",
        "risk_allele": "A",
        "category": "glaucoma",
        "conditions": ["Primary open-angle glaucoma"],
        "evidence": "strong",
        "references": ["PMID:21532571"]
    },
    
    # =========================================================================
    # MYOPIA (NEARSIGHTEDNESS)
    # =========================================================================
    
    "rs524952": {
        "gene": "GJD2",
        "name": "Myopia GJD2",
        "risk_allele": "A",
        "category": "myopia",
        "conditions": ["Myopia", "Nearsightedness"],
        "evidence": "strong",
        "references": ["PMID:20835236"],
        "actionable": {
            "priority": "low",
            "action_type": "lifestyle",
            "recommendations": [
                "Outdoor time in childhood is protective",
                "Limit excessive near work/screen time",
                "Regular eye exams for prescription updates"
            ]
        }
    },
    
    "rs8015152": {
        "gene": "RASGRF1",
        "name": "Myopia RASGRF1",
        "risk_allele": "T",
        "category": "myopia",
        "conditions": ["Myopia"],
        "evidence": "moderate",
        "references": ["PMID:20054397"]
    },
    
    "rs2137277": {
        "gene": "KCNQ5",
        "name": "Refractive error KCNQ5",
        "risk_allele": "A",
        "category": "myopia",
        "conditions": ["Refractive error", "Myopia"],
        "evidence": "moderate",
        "references": ["PMID:23474815"]
    },
    
    # =========================================================================
    # CATARACTS
    # =========================================================================
    
    "rs2289917": {
        "gene": "EPHA2",
        "name": "Age-related cataracts",
        "risk_allele": "A",
        "category": "cataracts",
        "conditions": ["Age-related cataracts"],
        "evidence": "moderate",
        "references": ["PMID:19503088"],
        "actionable": {
            "priority": "low",
            "action_type": "lifestyle",
            "recommendations": [
                "UV protective sunglasses",
                "Don't smoke",
                "Control blood sugar if diabetic"
            ]
        }
    },
    
    "rs3754334": {
        "gene": "KCNAB1",
        "name": "Nuclear cataracts",
        "risk_allele": "T",
        "category": "cataracts",
        "conditions": ["Nuclear cataracts"],
        "evidence": "moderate",
        "references": ["PMID:22384026"]
    },
    
    # =========================================================================
    # RETINITIS PIGMENTOSA (RP)
    # =========================================================================
    
    "rs1800553": {
        "gene": "RHO",
        "name": "Rhodopsin P23H",
        "variant": "P23H",
        "risk_allele": "A",
        "category": "retinitis_pigmentosa",
        "conditions": ["Retinitis pigmentosa"],
        "inheritance": "autosomal_dominant",
        "evidence": "strong",
        "references": ["PMID:2358456", "ClinVar:VCV000004636"],
        "note": "Most common RP mutation in North America",
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": [
                "Referral to retinal specialist",
                "Regular dark adaptation and visual field testing",
                "Genetic counseling for family members",
                "Emerging gene therapy options"
            ]
        }
    },
    
    "rs28935490": {
        "gene": "USH2A",
        "name": "Usher syndrome type 2",
        "risk_allele": "T",
        "category": "retinitis_pigmentosa",
        "conditions": ["Usher syndrome type 2", "RP with hearing loss"],
        "inheritance": "autosomal_recessive",
        "evidence": "strong",
        "references": ["ClinVar:VCV000003873"],
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": [
                "Hearing assessment",
                "Night vision and peripheral vision monitoring",
                "Genetic counseling"
            ]
        }
    },
    
    # =========================================================================
    # COLOR VISION
    # =========================================================================
    
    "rs1800441": {
        "gene": "OPN1MW/OPN1LW",
        "name": "Red-green color vision",
        "risk_allele": "C",
        "category": "color_vision",
        "conditions": ["Color vision deficiency"],
        "inheritance": "X-linked_recessive",
        "evidence": "moderate",
        "references": ["PMID:1303172"],
        "note": "Common color blindness marker",
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": [
                "~8% of males affected",
                "Career considerations for color-critical jobs",
                "Color-blind accessible interfaces helpful"
            ]
        }
    },
    
    # =========================================================================
    # EYE COLOR
    # =========================================================================
    
    "rs12913832": {
        "gene": "HERC2-OCA2",
        "name": "Eye color primary",
        "risk_allele": "G",
        "category": "eye_color",
        "trait": "Eye color",
        "evidence": "strong",
        "references": ["PMID:18172690"],
        "interpretation": {
            "AA": "Brown eyes (dominant)",
            "AG": "Brown/hazel/green possible",
            "GG": "Blue/gray eyes"
        },
        "note": "Explains ~80% of blue vs brown eye color variation"
    },
    
    "rs1129038": {
        "gene": "HERC2",
        "name": "Eye color secondary",
        "risk_allele": "G",
        "category": "eye_color",
        "trait": "Eye color",
        "evidence": "strong",
        "references": ["PMID:18252222"]
    },
}

HEARING_MARKERS = {
    # =========================================================================
    # AGE-RELATED HEARING LOSS
    # =========================================================================
    
    "rs1800532": {
        "gene": "TPH1",
        "name": "Age-related hearing loss",
        "risk_allele": "A",
        "category": "hearing_loss",
        "conditions": ["Presbycusis", "Age-related hearing loss"],
        "evidence": "moderate",
        "references": ["PMID:20200933"],
        "actionable": {
            "priority": "low",
            "action_type": "lifestyle",
            "recommendations": [
                "Protect hearing from loud noise exposure",
                "Annual hearing tests after age 60",
                "Don't delay hearing aids if needed"
            ]
        }
    },
    
    "rs161927": {
        "gene": "GRM7",
        "name": "GRM7 hearing",
        "risk_allele": "A",
        "category": "hearing_loss",
        "conditions": ["Age-related hearing loss"],
        "evidence": "moderate",
        "references": ["PMID:19339252"],
        "note": "Glutamate receptor - may affect susceptibility to noise damage"
    },
    
    "rs7907687": {
        "gene": "NAT2",
        "name": "NAT2 ototoxicity",
        "risk_allele": "T",
        "category": "hearing_loss",
        "conditions": ["Drug-induced hearing loss"],
        "evidence": "moderate",
        "references": ["PMID:23575430"],
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["Metabolizer status may affect ototoxic drug risk"]
        }
    },
    
    # =========================================================================
    # NOISE-INDUCED HEARING LOSS
    # =========================================================================
    
    "rs2227956": {
        "gene": "KCNMA1",
        "name": "Noise susceptibility",
        "risk_allele": "T",
        "category": "noise_hearing_loss",
        "conditions": ["Noise-induced hearing loss"],
        "evidence": "moderate",
        "references": ["PMID:22065868"],
        "actionable": {
            "priority": "medium",
            "action_type": "lifestyle",
            "recommendations": [
                "Use hearing protection in noisy environments",
                "Some individuals more susceptible to noise damage",
                "Avoid prolonged exposure to >85dB"
            ]
        }
    },
    
    "rs3751385": {
        "gene": "DFNA5",
        "name": "DFNA5 hearing",
        "risk_allele": "T",
        "category": "hearing_loss",
        "conditions": ["Progressive hearing loss"],
        "evidence": "moderate",
        "references": ["PMID:23575428"]
    },
    
    # =========================================================================
    # AMINOGLYCOSIDE-INDUCED DEAFNESS
    # =========================================================================
    
    "rs267606617": {
        "gene": "MT-RNR1",
        "name": "Aminoglycoside deafness m.1555A>G",
        "variant": "m.1555A>G",
        "risk_allele": "G",
        "category": "ototoxicity",
        "conditions": ["Aminoglycoside-induced deafness"],
        "inheritance": "mitochondrial",
        "evidence": "strong",
        "references": ["PMID:8020937", "ClinVar:VCV000009546"],
        "critical": True,
        "actionable": {
            "priority": "critical",
            "action_type": "medical_alert",
            "recommendations": [
                "CRITICAL: Avoid aminoglycoside antibiotics",
                "Drugs to avoid: gentamicin, streptomycin, amikacin, tobramycin",
                "Maternally inherited - all maternal relatives at risk",
                "Alert all healthcare providers",
                "Consider medical alert bracelet"
            ]
        }
    },
    
    "rs267606618": {
        "gene": "MT-RNR1",
        "name": "Aminoglycoside deafness m.1494C>T",
        "variant": "m.1494C>T",
        "risk_allele": "T",
        "category": "ototoxicity",
        "conditions": ["Aminoglycoside-induced deafness"],
        "inheritance": "mitochondrial",
        "evidence": "strong",
        "references": ["PMID:16287161"],
        "actionable": {
            "priority": "critical",
            "action_type": "medical_alert",
            "recommendations": [
                "CRITICAL: Avoid aminoglycoside antibiotics",
                "Maternal inheritance pattern"
            ]
        }
    },
    
    # =========================================================================
    # CONGENITAL HEARING LOSS
    # =========================================================================
    
    "rs72474224": {
        "gene": "GJB2",
        "name": "Connexin 26 35delG carrier",
        "variant": "35delG",
        "risk_allele": "deletion",
        "category": "congenital_hearing",
        "conditions": ["Congenital nonsyndromic hearing loss"],
        "inheritance": "autosomal_recessive",
        "population_frequency": "1:30 carrier in Europeans",
        "evidence": "strong",
        "references": ["PMID:9382091", "ClinVar:VCV000017023"],
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": [
                "Most common cause of genetic hearing loss",
                "Partner testing recommended if carrier",
                "Newborn hearing screening will detect affected infants"
            ]
        }
    },
    
    "rs80338940": {
        "gene": "GJB2",
        "name": "Connexin 26 167delT",
        "variant": "167delT",
        "risk_allele": "deletion",
        "category": "congenital_hearing",
        "conditions": ["Nonsyndromic hearing loss"],
        "inheritance": "autosomal_recessive",
        "population_frequency": "Common in Ashkenazi Jewish",
        "evidence": "strong",
        "references": ["ClinVar:VCV000017024"]
    },
    
    "rs111033304": {
        "gene": "MYO7A",
        "name": "Usher syndrome 1B",
        "risk_allele": "T",
        "category": "syndromic_hearing",
        "conditions": ["Usher syndrome type 1B", "Deafness with RP"],
        "inheritance": "autosomal_recessive",
        "evidence": "strong",
        "references": ["ClinVar:VCV000004577"],
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": [
                "Combined deafness and progressive vision loss",
                "Vestibular dysfunction",
                "Early intervention critical"
            ]
        }
    },
    
    "rs121908362": {
        "gene": "OTOF",
        "name": "Auditory neuropathy OTOF",
        "risk_allele": "T",
        "category": "congenital_hearing",
        "conditions": ["Auditory neuropathy spectrum disorder"],
        "inheritance": "autosomal_recessive",
        "evidence": "strong",
        "references": ["ClinVar:VCV000003959"],
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": [
                "Cochlear implant often beneficial",
                "Hearing aids less effective in auditory neuropathy"
            ]
        }
    },
    
    # =========================================================================
    # TINNITUS
    # =========================================================================
    
    "rs2053747": {
        "gene": "8q24",
        "name": "Tinnitus susceptibility",
        "risk_allele": "T",
        "category": "tinnitus",
        "conditions": ["Tinnitus"],
        "evidence": "moderate",
        "references": ["PMID:30093638"],
        "note": "One of few genetic associations with tinnitus",
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": [
                "Hearing protection important",
                "Manage stress (can worsen tinnitus)",
                "Cognitive behavioral therapy can help"
            ]
        }
    },
    
    # =========================================================================
    # MÉNIÈRE'S DISEASE
    # =========================================================================
    
    "rs7598802": {
        "gene": "DTNA",
        "name": "Ménière's disease",
        "risk_allele": "A",
        "category": "vestibular",
        "conditions": ["Ménière's disease"],
        "evidence": "moderate",
        "references": ["PMID:25697799"],
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": [
                "Characterized by vertigo, hearing loss, tinnitus",
                "Low sodium diet may help some patients"
            ]
        }
    },
}

# Combine both categories
VISION_HEARING_MARKERS = {**VISION_MARKERS, **HEARING_MARKERS}

# Clinical notes for vision and hearing
CLINICAL_NOTES = """
VISION AND HEARING GENETIC TESTING NOTES:

AMD (Age-related Macular Degeneration):
- CFH Y402H + ARMS2 A69S explain ~50% of AMD heritability
- Smoking + risk genotypes = dramatically elevated risk
- AREDS2 supplementation (vitamins C, E, zinc, lutein, zeaxanthin) 
  reduces progression risk by ~25% in intermediate AMD

GLAUCOMA:
- Primary open-angle glaucoma: CAV1, TMCO1, SIX1-SIX6
- Exfoliation glaucoma: LOXL1 variants (population-specific risk direction)
- Angle-closure more common in Asian populations (hyperopic eyes)

HEARING LOSS:
- GJB2 (Connexin 26): Most common cause of genetic hearing loss
- Mitochondrial m.1555A>G: CRITICAL - aminoglycoside sensitivity
- Noise susceptibility varies genetically - protection important for all

CARRIER SCREENING RELEVANCE:
- GJB2 (35delG): 1:30 carriers in Europeans
- Usher syndrome: Combined deafness + vision loss
- Early identification enables intervention

ACTION ITEMS BY RISK LEVEL:
- CFH CC + ARMS2 TT: Very high AMD risk - annual dilated exams, don't smoke
- MT-RNR1 variants: Medical alert - no aminoglycosides
- GJB2 carrier: Partner testing before pregnancy
"""
