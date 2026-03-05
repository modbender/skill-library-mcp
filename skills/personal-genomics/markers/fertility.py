"""
Fertility and Reproductive Health Genetics Markers.
Markers for reproductive conditions, pregnancy outcomes, and fertility factors.
"""

FERTILITY_MARKERS = {
    # =========================================================================
    # FEMALE FERTILITY - OVARIAN RESERVE / MENOPAUSE
    # =========================================================================
    
    "rs16991615": {
        "gene": "MCM8",
        "name": "Primary ovarian insufficiency",
        "risk_allele": "A",
        "category": "ovarian",
        "conditions": ["Primary ovarian insufficiency", "Early menopause"],
        "evidence": "strong",
        "references": ["PMID:19098910"],
        "sex": "female",
        "actionable": {
            "priority": "medium",
            "action_type": "awareness",
            "recommendations": [
                "Consider AMH testing if planning delayed childbearing",
                "Discuss fertility preservation options if risk genotype",
                "Bone health monitoring post-menopause"
            ]
        }
    },
    
    "rs7246479": {
        "gene": "UIMC1",
        "name": "Age at menopause",
        "risk_allele": "T",
        "category": "ovarian",
        "conditions": ["Earlier menopause"],
        "evidence": "strong",
        "references": ["PMID:22367030"],
        "sex": "female",
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["One of many menopause timing variants"]
        }
    },
    
    "rs2303369": {
        "gene": "HELQ",
        "name": "HELQ ovarian",
        "risk_allele": "T",
        "category": "ovarian",
        "conditions": ["Ovarian reserve"],
        "evidence": "moderate",
        "references": ["PMID:22367030"],
        "sex": "female"
    },
    
    "rs4886238": {
        "gene": "PRRC2A",
        "name": "Menopause timing",
        "risk_allele": "G",
        "category": "ovarian",
        "conditions": ["Age at natural menopause"],
        "evidence": "strong",
        "references": ["PMID:22367030"],
        "sex": "female"
    },
    
    # =========================================================================
    # POLYCYSTIC OVARY SYNDROME (PCOS)
    # =========================================================================
    
    "rs13405728": {
        "gene": "LHCGR",
        "name": "PCOS LH receptor",
        "risk_allele": "A",
        "category": "pcos",
        "conditions": ["Polycystic ovary syndrome"],
        "evidence": "strong",
        "references": ["PMID:21151128"],
        "sex": "female",
        "actionable": {
            "priority": "medium",
            "action_type": "awareness",
            "recommendations": [
                "PCOS affects ~10% of women",
                "Characterized by irregular periods, excess androgens, ovarian cysts",
                "Weight management and metformin often helpful"
            ]
        }
    },
    
    "rs2479106": {
        "gene": "DENND1A",
        "name": "PCOS DENND1A",
        "risk_allele": "A",
        "category": "pcos",
        "conditions": ["PCOS"],
        "evidence": "strong",
        "references": ["PMID:21151128"],
        "sex": "female"
    },
    
    "rs13429458": {
        "gene": "THADA",
        "name": "PCOS THADA",
        "risk_allele": "A",
        "category": "pcos",
        "conditions": ["PCOS"],
        "evidence": "strong",
        "references": ["PMID:20581827"],
        "sex": "female"
    },
    
    "rs4385527": {
        "gene": "FSHR",
        "name": "FSH receptor PCOS",
        "risk_allele": "G",
        "category": "pcos",
        "conditions": ["PCOS", "FSH response"],
        "evidence": "moderate",
        "references": ["PMID:21151128"],
        "sex": "female",
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": ["May affect response to FSH in fertility treatment"]
        }
    },
    
    # =========================================================================
    # ENDOMETRIOSIS
    # =========================================================================
    
    "rs12700667": {
        "gene": "7p15.2",
        "name": "Endometriosis 7p15",
        "risk_allele": "A",
        "category": "endometriosis",
        "conditions": ["Endometriosis"],
        "evidence": "strong",
        "references": ["PMID:20935630"],
        "sex": "female",
        "actionable": {
            "priority": "medium",
            "action_type": "awareness",
            "recommendations": [
                "Endometriosis affects ~10% of women",
                "Can impact fertility",
                "Seek evaluation if severe menstrual pain"
            ]
        }
    },
    
    "rs7521902": {
        "gene": "WNT4",
        "name": "Endometriosis WNT4",
        "risk_allele": "A",
        "category": "endometriosis",
        "conditions": ["Endometriosis"],
        "evidence": "strong",
        "references": ["PMID:20935630"],
        "sex": "female"
    },
    
    "rs10859871": {
        "gene": "VEZT",
        "name": "Endometriosis VEZT",
        "risk_allele": "C",
        "category": "endometriosis",
        "conditions": ["Endometriosis"],
        "evidence": "strong",
        "references": ["PMID:21151128"],
        "sex": "female"
    },
    
    "rs1537377": {
        "gene": "CDKN2B-AS1",
        "name": "Endometriosis 9p21",
        "risk_allele": "T",
        "category": "endometriosis",
        "conditions": ["Endometriosis"],
        "evidence": "moderate",
        "references": ["PMID:22570617"],
        "sex": "female"
    },
    
    # =========================================================================
    # MALE FERTILITY
    # =========================================================================
    
    "rs10732516": {
        "gene": "H19",
        "name": "Male infertility H19",
        "risk_allele": "G",
        "category": "male_fertility",
        "conditions": ["Oligozoospermia", "Male infertility"],
        "evidence": "moderate",
        "references": ["PMID:25165108"],
        "sex": "male",
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": [
                "One of several male infertility risk variants",
                "Semen analysis is standard evaluation"
            ]
        }
    },
    
    "rs5934505": {
        "gene": "USP26",
        "name": "Spermatogenesis USP26",
        "risk_allele": "T",
        "category": "male_fertility",
        "conditions": ["Azoospermia", "Severe oligozoospermia"],
        "evidence": "moderate",
        "references": ["PMID:19843532"],
        "sex": "male"
    },
    
    "rs2066808": {
        "gene": "FSHB",
        "name": "FSH beta male",
        "risk_allele": "T",
        "category": "male_fertility",
        "conditions": ["FSH levels", "Testicular function"],
        "evidence": "moderate",
        "references": ["PMID:21685410"],
        "sex": "male"
    },
    
    "rs10966902": {
        "gene": "PIWIL1",
        "name": "Spermatogenesis PIWI",
        "risk_allele": "A",
        "category": "male_fertility",
        "conditions": ["Male infertility"],
        "evidence": "moderate",
        "references": ["PMID:24217693"],
        "sex": "male",
        "note": "PIWI pathway important for sperm development"
    },
    
    # Y-chromosome related (special handling needed)
    "SRY": {
        "gene": "SRY",
        "name": "Sex-determining region Y",
        "category": "male_fertility",
        "conditions": ["Y chromosome presence"],
        "note": "Y chromosome microdeletions require separate testing",
        "evidence": "strong"
    },
    
    # =========================================================================
    # PREGNANCY COMPLICATIONS
    # =========================================================================
    
    "rs6025": {
        "gene": "F5",
        "name": "Factor V Leiden pregnancy",
        "risk_allele": "A",
        "category": "pregnancy",
        "conditions": ["Pregnancy loss", "Preeclampsia", "VTE in pregnancy"],
        "evidence": "strong",
        "references": ["PMID:7989260"],
        "sex": "female",
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "Increased pregnancy loss risk (2-3x)",
                "VTE prophylaxis may be indicated in pregnancy",
                "Discuss with OB before pregnancy",
                "Avoid estrogen-containing contraceptives"
            ]
        }
    },
    
    "rs1799963": {
        "gene": "F2",
        "name": "Prothrombin pregnancy",
        "risk_allele": "A",
        "category": "pregnancy",
        "conditions": ["Pregnancy loss", "Thrombosis risk"],
        "evidence": "strong",
        "references": ["PMID:8872854"],
        "sex": "female",
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "Recurrent pregnancy loss association",
                "VTE risk in pregnancy elevated",
                "Anticoagulation may be recommended"
            ]
        }
    },
    
    "rs1801133": {
        "gene": "MTHFR",
        "name": "MTHFR pregnancy",
        "risk_allele": "A",
        "category": "pregnancy",
        "conditions": ["Neural tube defects", "Pregnancy loss"],
        "evidence": "moderate",
        "references": ["PMID:8630491"],
        "sex": "female",
        "actionable": {
            "priority": "medium",
            "action_type": "supplementation",
            "recommendations": [
                "Folate supplementation before and during pregnancy",
                "Consider methylfolate if homozygous TT",
                "400-800mcg daily; 4mg if previous NTD"
            ]
        }
    },
    
    "rs1800871": {
        "gene": "IL10",
        "name": "IL-10 pregnancy loss",
        "risk_allele": "T",
        "category": "pregnancy",
        "conditions": ["Recurrent pregnancy loss", "Preterm birth"],
        "evidence": "moderate",
        "references": ["PMID:21325614"],
        "sex": "female"
    },
    
    "rs3135388": {
        "gene": "HLA-DRA",
        "name": "Preeclampsia HLA",
        "risk_allele": "A",
        "category": "pregnancy",
        "conditions": ["Preeclampsia"],
        "evidence": "moderate",
        "references": ["PMID:21076409"],
        "sex": "female",
        "actionable": {
            "priority": "low",
            "action_type": "monitoring",
            "recommendations": [
                "Blood pressure monitoring in pregnancy important",
                "Low-dose aspirin may be recommended for high-risk women"
            ]
        }
    },
    
    # =========================================================================
    # MULTIPLE PREGNANCY
    # =========================================================================
    
    "rs11031006": {
        "gene": "FSHB",
        "name": "Dizygotic twinning FSH",
        "risk_allele": "G",
        "category": "twinning",
        "conditions": ["Dizygotic twinning"],
        "evidence": "strong",
        "references": ["PMID:26581573"],
        "sex": "female",
        "interpretation": {
            "AA": "Average twinning rate",
            "AG": "Slightly increased DZ twin probability",
            "GG": "Increased FSH, higher DZ twinning rate"
        },
        "note": "Naturally occurring fraternal twins"
    },
    
    "rs17293443": {
        "gene": "SMAD3",
        "name": "Dizygotic twinning SMAD3",
        "risk_allele": "C",
        "category": "twinning",
        "conditions": ["Dizygotic twinning"],
        "evidence": "strong",
        "references": ["PMID:26581573"],
        "sex": "female"
    },
    
    # =========================================================================
    # GESTATIONAL DIABETES
    # =========================================================================
    
    "rs7903146": {
        "gene": "TCF7L2",
        "name": "Gestational diabetes TCF7L2",
        "risk_allele": "T",
        "category": "gestational_diabetes",
        "conditions": ["Gestational diabetes"],
        "evidence": "strong",
        "references": ["PMID:18854181"],
        "sex": "female",
        "actionable": {
            "priority": "medium",
            "action_type": "monitoring",
            "recommendations": [
                "T allele increases gestational diabetes risk",
                "Glucose screening important in pregnancy",
                "Weight management before pregnancy helps"
            ]
        }
    },
    
    "rs10830963": {
        "gene": "MTNR1B",
        "name": "Gestational diabetes melatonin",
        "risk_allele": "G",
        "category": "gestational_diabetes",
        "conditions": ["Gestational diabetes", "Fasting glucose"],
        "evidence": "strong",
        "references": ["PMID:18711366"],
        "sex": "female"
    },
    
    # =========================================================================
    # PRETERM BIRTH
    # =========================================================================
    
    "rs17591250": {
        "gene": "WNT4",
        "name": "Preterm birth WNT4",
        "risk_allele": "T",
        "category": "preterm",
        "conditions": ["Spontaneous preterm birth"],
        "evidence": "moderate",
        "references": ["PMID:28267171"],
        "sex": "female",
        "actionable": {
            "priority": "low",
            "action_type": "awareness",
            "recommendations": [
                "Multiple factors affect preterm birth risk",
                "Progesterone supplementation may help in some cases"
            ]
        }
    },
    
    "rs1061170": {
        "gene": "CFH",
        "name": "Preterm preeclampsia CFH",
        "risk_allele": "C",
        "category": "preterm",
        "conditions": ["Preterm preeclampsia"],
        "evidence": "moderate",
        "references": ["PMID:18326827"],
        "sex": "female"
    },
    
    # =========================================================================
    # CONTRACEPTION RESPONSE
    # =========================================================================
    
    "rs6025_contraception": {
        "gene": "F5",
        "name": "Factor V Leiden contraception",
        "risk_allele": "A",
        "category": "contraception",
        "conditions": ["VTE with oral contraceptives"],
        "evidence": "strong",
        "references": ["PMID:7989260"],
        "sex": "female",
        "actionable": {
            "priority": "high",
            "action_type": "medical_alert",
            "recommendations": [
                "AVOID estrogen-containing contraceptives if carrier",
                "VTE risk 35x with Factor V + estrogen",
                "Progestin-only or non-hormonal methods preferred",
                "IUD, implant, progestin-only pill are options"
            ]
        }
    },
    
    # =========================================================================
    # CARRIER SCREENING RELEVANT TO REPRODUCTION
    # =========================================================================
    
    "rs75527207": {
        "gene": "CFTR",
        "name": "CF carrier reproductive",
        "risk_allele": "A",
        "category": "carrier_screening",
        "conditions": ["Cystic fibrosis carrier"],
        "evidence": "strong",
        "references": ["ClinVar:VCV000007105"],
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": [
                "1:25 carrier frequency in Europeans",
                "Partner testing recommended before pregnancy",
                "IVF with PGT-M available if both partners carriers"
            ]
        }
    },
    
    "rs334": {
        "gene": "HBB",
        "name": "Sickle cell reproductive",
        "risk_allele": "T",
        "category": "carrier_screening",
        "conditions": ["Sickle cell carrier"],
        "evidence": "strong",
        "references": ["ClinVar:VCV000015126"],
        "actionable": {
            "priority": "high",
            "action_type": "screening",
            "recommendations": [
                "1:12 carrier frequency in African Americans",
                "Partner testing essential",
                "Pregnancy in sickle cell disease is high-risk"
            ]
        }
    },
}

# Summary for reproductive health
REPRODUCTIVE_NOTES = """
REPRODUCTIVE GENETICS NOTES:

PRECONCEPTION COUNSELING:
- Carrier screening for common recessive conditions
- Thrombophilia testing if personal/family history of VTE
- MTHFR status - folate supplementation
- Assessment of ovarian reserve if older maternal age

KEY MARKERS FOR PREGNANCY PLANNING:
- Factor V Leiden (rs6025): VTE risk, pregnancy loss, contraception choice
- Prothrombin G20210A (rs1799963): VTE risk, pregnancy loss
- MTHFR C677T (rs1801133): Neural tube defect risk, folate needs

PCOS:
- ~10% of reproductive-age women
- LHCGR, DENND1A, THADA variants contribute
- Lifestyle modification often first-line treatment
- May need ovulation induction for conception

ENDOMETRIOSIS:
- ~10% prevalence
- Can significantly impact fertility
- Early diagnosis and treatment may preserve fertility

MALE FACTOR:
- ~50% of infertility cases have male component
- Y chromosome microdeletions not detected on consumer arrays
- Semen analysis standard first-line evaluation

IVF CONSIDERATIONS:
- FSH receptor variants may affect stimulation response
- AMH and antral follicle count better predictors than genetics
- PGT-M available for known single-gene disorders
"""
