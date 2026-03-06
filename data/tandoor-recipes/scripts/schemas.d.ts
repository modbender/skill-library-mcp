import { z } from 'zod';
export declare const FoodSchema: z.ZodObject<{
    id: z.ZodNumber;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: number;
    name: string;
    description?: string | undefined;
}, {
    id: number;
    name: string;
    description?: string | undefined;
}>;
export type Food = z.infer<typeof FoodSchema>;
export declare const UnitSchema: z.ZodObject<{
    id: z.ZodNumber;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: number;
    name: string;
    description?: string | undefined;
}, {
    id: number;
    name: string;
    description?: string | undefined;
}>;
export type Unit = z.infer<typeof UnitSchema>;
export declare const KeywordSchema: z.ZodObject<{
    id: z.ZodNumber;
    name: z.ZodOptional<z.ZodString>;
    label: z.ZodOptional<z.ZodString>;
    description: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: number;
    name?: string | undefined;
    description?: string | undefined;
    label?: string | undefined;
}, {
    id: number;
    name?: string | undefined;
    description?: string | undefined;
    label?: string | undefined;
}>;
export type Keyword = z.infer<typeof KeywordSchema>;
export declare const MealTypeSchema: z.ZodObject<{
    id: z.ZodNumber;
    name: z.ZodString;
}, "strip", z.ZodTypeAny, {
    id: number;
    name: string;
}, {
    id: number;
    name: string;
}>;
export type MealType = z.infer<typeof MealTypeSchema>;
export declare const IngredientSchema: z.ZodObject<{
    id: z.ZodOptional<z.ZodNumber>;
    food: z.ZodOptional<z.ZodObject<{
        id: z.ZodOptional<z.ZodNumber>;
        name: z.ZodOptional<z.ZodString>;
        description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    }, "strip", z.ZodTypeAny, {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    }, {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    }>>;
    unit: z.ZodOptional<z.ZodObject<{
        id: z.ZodOptional<z.ZodNumber>;
        name: z.ZodOptional<z.ZodString>;
        description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    }, "strip", z.ZodTypeAny, {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    }, {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    }>>;
    amount: z.ZodUnion<[z.ZodString, z.ZodNumber]>;
    note: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    amount: string | number;
    id?: number | undefined;
    food?: {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    } | undefined;
    unit?: {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    } | undefined;
    note?: string | undefined;
}, {
    amount: string | number;
    id?: number | undefined;
    food?: {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    } | undefined;
    unit?: {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    } | undefined;
    note?: string | undefined;
}>;
export type Ingredient = z.infer<typeof IngredientSchema>;
export declare const StepSchema: z.ZodObject<{
    id: z.ZodOptional<z.ZodNumber>;
    instruction: z.ZodString;
    ingredients: z.ZodOptional<z.ZodArray<z.ZodObject<{
        id: z.ZodOptional<z.ZodNumber>;
        food: z.ZodOptional<z.ZodObject<{
            id: z.ZodOptional<z.ZodNumber>;
            name: z.ZodOptional<z.ZodString>;
            description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
        }, "strip", z.ZodTypeAny, {
            id?: number | undefined;
            name?: string | undefined;
            description?: string | undefined;
        }, {
            id?: number | undefined;
            name?: string | undefined;
            description?: string | undefined;
        }>>;
        unit: z.ZodOptional<z.ZodObject<{
            id: z.ZodOptional<z.ZodNumber>;
            name: z.ZodOptional<z.ZodString>;
            description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
        }, "strip", z.ZodTypeAny, {
            id?: number | undefined;
            name?: string | undefined;
            description?: string | undefined;
        }, {
            id?: number | undefined;
            name?: string | undefined;
            description?: string | undefined;
        }>>;
        amount: z.ZodUnion<[z.ZodString, z.ZodNumber]>;
        note: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        amount: string | number;
        id?: number | undefined;
        food?: {
            id?: number | undefined;
            name?: string | undefined;
            description?: string | undefined;
        } | undefined;
        unit?: {
            id?: number | undefined;
            name?: string | undefined;
            description?: string | undefined;
        } | undefined;
        note?: string | undefined;
    }, {
        amount: string | number;
        id?: number | undefined;
        food?: {
            id?: number | undefined;
            name?: string | undefined;
            description?: string | undefined;
        } | undefined;
        unit?: {
            id?: number | undefined;
            name?: string | undefined;
            description?: string | undefined;
        } | undefined;
        note?: string | undefined;
    }>, "many">>;
    order: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    instruction: string;
    id?: number | undefined;
    ingredients?: {
        amount: string | number;
        id?: number | undefined;
        food?: {
            id?: number | undefined;
            name?: string | undefined;
            description?: string | undefined;
        } | undefined;
        unit?: {
            id?: number | undefined;
            name?: string | undefined;
            description?: string | undefined;
        } | undefined;
        note?: string | undefined;
    }[] | undefined;
    order?: number | undefined;
}, {
    instruction: string;
    id?: number | undefined;
    ingredients?: {
        amount: string | number;
        id?: number | undefined;
        food?: {
            id?: number | undefined;
            name?: string | undefined;
            description?: string | undefined;
        } | undefined;
        unit?: {
            id?: number | undefined;
            name?: string | undefined;
            description?: string | undefined;
        } | undefined;
        note?: string | undefined;
    }[] | undefined;
    order?: number | undefined;
}>;
export type Step = z.infer<typeof StepSchema>;
export declare const RecipeSchema: z.ZodObject<{
    id: z.ZodNumber;
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    servings: z.ZodOptional<z.ZodNumber>;
    rating: z.ZodOptional<z.ZodNullable<z.ZodNumber>>;
    keywords: z.ZodOptional<z.ZodArray<z.ZodObject<{
        id: z.ZodNumber;
        name: z.ZodOptional<z.ZodString>;
        label: z.ZodOptional<z.ZodString>;
        description: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        id: number;
        name?: string | undefined;
        description?: string | undefined;
        label?: string | undefined;
    }, {
        id: number;
        name?: string | undefined;
        description?: string | undefined;
        label?: string | undefined;
    }>, "many">>;
    steps: z.ZodOptional<z.ZodArray<z.ZodObject<{
        id: z.ZodOptional<z.ZodNumber>;
        instruction: z.ZodString;
        ingredients: z.ZodOptional<z.ZodArray<z.ZodObject<{
            id: z.ZodOptional<z.ZodNumber>;
            food: z.ZodOptional<z.ZodObject<{
                id: z.ZodOptional<z.ZodNumber>;
                name: z.ZodOptional<z.ZodString>;
                description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
            }, "strip", z.ZodTypeAny, {
                id?: number | undefined;
                name?: string | undefined;
                description?: string | undefined;
            }, {
                id?: number | undefined;
                name?: string | undefined;
                description?: string | undefined;
            }>>;
            unit: z.ZodOptional<z.ZodObject<{
                id: z.ZodOptional<z.ZodNumber>;
                name: z.ZodOptional<z.ZodString>;
                description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
            }, "strip", z.ZodTypeAny, {
                id?: number | undefined;
                name?: string | undefined;
                description?: string | undefined;
            }, {
                id?: number | undefined;
                name?: string | undefined;
                description?: string | undefined;
            }>>;
            amount: z.ZodUnion<[z.ZodString, z.ZodNumber]>;
            note: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            amount: string | number;
            id?: number | undefined;
            food?: {
                id?: number | undefined;
                name?: string | undefined;
                description?: string | undefined;
            } | undefined;
            unit?: {
                id?: number | undefined;
                name?: string | undefined;
                description?: string | undefined;
            } | undefined;
            note?: string | undefined;
        }, {
            amount: string | number;
            id?: number | undefined;
            food?: {
                id?: number | undefined;
                name?: string | undefined;
                description?: string | undefined;
            } | undefined;
            unit?: {
                id?: number | undefined;
                name?: string | undefined;
                description?: string | undefined;
            } | undefined;
            note?: string | undefined;
        }>, "many">>;
        order: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        instruction: string;
        id?: number | undefined;
        ingredients?: {
            amount: string | number;
            id?: number | undefined;
            food?: {
                id?: number | undefined;
                name?: string | undefined;
                description?: string | undefined;
            } | undefined;
            unit?: {
                id?: number | undefined;
                name?: string | undefined;
                description?: string | undefined;
            } | undefined;
            note?: string | undefined;
        }[] | undefined;
        order?: number | undefined;
    }, {
        instruction: string;
        id?: number | undefined;
        ingredients?: {
            amount: string | number;
            id?: number | undefined;
            food?: {
                id?: number | undefined;
                name?: string | undefined;
                description?: string | undefined;
            } | undefined;
            unit?: {
                id?: number | undefined;
                name?: string | undefined;
                description?: string | undefined;
            } | undefined;
            note?: string | undefined;
        }[] | undefined;
        order?: number | undefined;
    }>, "many">>;
}, "strip", z.ZodTypeAny, {
    id: number;
    name: string;
    description?: string | undefined;
    servings?: number | undefined;
    rating?: number | null | undefined;
    keywords?: {
        id: number;
        name?: string | undefined;
        description?: string | undefined;
        label?: string | undefined;
    }[] | undefined;
    steps?: {
        instruction: string;
        id?: number | undefined;
        ingredients?: {
            amount: string | number;
            id?: number | undefined;
            food?: {
                id?: number | undefined;
                name?: string | undefined;
                description?: string | undefined;
            } | undefined;
            unit?: {
                id?: number | undefined;
                name?: string | undefined;
                description?: string | undefined;
            } | undefined;
            note?: string | undefined;
        }[] | undefined;
        order?: number | undefined;
    }[] | undefined;
}, {
    id: number;
    name: string;
    description?: string | undefined;
    servings?: number | undefined;
    rating?: number | null | undefined;
    keywords?: {
        id: number;
        name?: string | undefined;
        description?: string | undefined;
        label?: string | undefined;
    }[] | undefined;
    steps?: {
        instruction: string;
        id?: number | undefined;
        ingredients?: {
            amount: string | number;
            id?: number | undefined;
            food?: {
                id?: number | undefined;
                name?: string | undefined;
                description?: string | undefined;
            } | undefined;
            unit?: {
                id?: number | undefined;
                name?: string | undefined;
                description?: string | undefined;
            } | undefined;
            note?: string | undefined;
        }[] | undefined;
        order?: number | undefined;
    }[] | undefined;
}>;
export type Recipe = z.infer<typeof RecipeSchema>;
export declare const RecipeListResponseSchema: z.ZodObject<{
    count: z.ZodNumber;
    next: z.ZodNullable<z.ZodString>;
    previous: z.ZodNullable<z.ZodString>;
    results: z.ZodArray<z.ZodObject<{
        id: z.ZodNumber;
        name: z.ZodString;
        description: z.ZodOptional<z.ZodString>;
        servings: z.ZodOptional<z.ZodNumber>;
        rating: z.ZodOptional<z.ZodNullable<z.ZodNumber>>;
        keywords: z.ZodOptional<z.ZodArray<z.ZodObject<{
            id: z.ZodNumber;
            name: z.ZodOptional<z.ZodString>;
            label: z.ZodOptional<z.ZodString>;
            description: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            id: number;
            name?: string | undefined;
            description?: string | undefined;
            label?: string | undefined;
        }, {
            id: number;
            name?: string | undefined;
            description?: string | undefined;
            label?: string | undefined;
        }>, "many">>;
        steps: z.ZodOptional<z.ZodArray<z.ZodObject<{
            id: z.ZodOptional<z.ZodNumber>;
            instruction: z.ZodString;
            ingredients: z.ZodOptional<z.ZodArray<z.ZodObject<{
                id: z.ZodOptional<z.ZodNumber>;
                food: z.ZodOptional<z.ZodObject<{
                    id: z.ZodOptional<z.ZodNumber>;
                    name: z.ZodOptional<z.ZodString>;
                    description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
                }, "strip", z.ZodTypeAny, {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                }, {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                }>>;
                unit: z.ZodOptional<z.ZodObject<{
                    id: z.ZodOptional<z.ZodNumber>;
                    name: z.ZodOptional<z.ZodString>;
                    description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
                }, "strip", z.ZodTypeAny, {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                }, {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                }>>;
                amount: z.ZodUnion<[z.ZodString, z.ZodNumber]>;
                note: z.ZodOptional<z.ZodString>;
            }, "strip", z.ZodTypeAny, {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }, {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }>, "many">>;
            order: z.ZodOptional<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            instruction: string;
            id?: number | undefined;
            ingredients?: {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }[] | undefined;
            order?: number | undefined;
        }, {
            instruction: string;
            id?: number | undefined;
            ingredients?: {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }[] | undefined;
            order?: number | undefined;
        }>, "many">>;
    }, "strip", z.ZodTypeAny, {
        id: number;
        name: string;
        description?: string | undefined;
        servings?: number | undefined;
        rating?: number | null | undefined;
        keywords?: {
            id: number;
            name?: string | undefined;
            description?: string | undefined;
            label?: string | undefined;
        }[] | undefined;
        steps?: {
            instruction: string;
            id?: number | undefined;
            ingredients?: {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }[] | undefined;
            order?: number | undefined;
        }[] | undefined;
    }, {
        id: number;
        name: string;
        description?: string | undefined;
        servings?: number | undefined;
        rating?: number | null | undefined;
        keywords?: {
            id: number;
            name?: string | undefined;
            description?: string | undefined;
            label?: string | undefined;
        }[] | undefined;
        steps?: {
            instruction: string;
            id?: number | undefined;
            ingredients?: {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }[] | undefined;
            order?: number | undefined;
        }[] | undefined;
    }>, "many">;
}, "strip", z.ZodTypeAny, {
    count: number;
    next: string | null;
    previous: string | null;
    results: {
        id: number;
        name: string;
        description?: string | undefined;
        servings?: number | undefined;
        rating?: number | null | undefined;
        keywords?: {
            id: number;
            name?: string | undefined;
            description?: string | undefined;
            label?: string | undefined;
        }[] | undefined;
        steps?: {
            instruction: string;
            id?: number | undefined;
            ingredients?: {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }[] | undefined;
            order?: number | undefined;
        }[] | undefined;
    }[];
}, {
    count: number;
    next: string | null;
    previous: string | null;
    results: {
        id: number;
        name: string;
        description?: string | undefined;
        servings?: number | undefined;
        rating?: number | null | undefined;
        keywords?: {
            id: number;
            name?: string | undefined;
            description?: string | undefined;
            label?: string | undefined;
        }[] | undefined;
        steps?: {
            instruction: string;
            id?: number | undefined;
            ingredients?: {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }[] | undefined;
            order?: number | undefined;
        }[] | undefined;
    }[];
}>;
export type RecipeListResponse = z.infer<typeof RecipeListResponseSchema>;
export declare const MealPlanSchema: z.ZodObject<{
    id: z.ZodNumber;
    title: z.ZodOptional<z.ZodString>;
    recipe: z.ZodOptional<z.ZodObject<{
        id: z.ZodOptional<z.ZodNumber>;
        name: z.ZodOptional<z.ZodString>;
        description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
        servings: z.ZodOptional<z.ZodOptional<z.ZodNumber>>;
        rating: z.ZodOptional<z.ZodOptional<z.ZodNullable<z.ZodNumber>>>;
        keywords: z.ZodOptional<z.ZodOptional<z.ZodArray<z.ZodObject<{
            id: z.ZodNumber;
            name: z.ZodOptional<z.ZodString>;
            label: z.ZodOptional<z.ZodString>;
            description: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            id: number;
            name?: string | undefined;
            description?: string | undefined;
            label?: string | undefined;
        }, {
            id: number;
            name?: string | undefined;
            description?: string | undefined;
            label?: string | undefined;
        }>, "many">>>;
        steps: z.ZodOptional<z.ZodOptional<z.ZodArray<z.ZodObject<{
            id: z.ZodOptional<z.ZodNumber>;
            instruction: z.ZodString;
            ingredients: z.ZodOptional<z.ZodArray<z.ZodObject<{
                id: z.ZodOptional<z.ZodNumber>;
                food: z.ZodOptional<z.ZodObject<{
                    id: z.ZodOptional<z.ZodNumber>;
                    name: z.ZodOptional<z.ZodString>;
                    description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
                }, "strip", z.ZodTypeAny, {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                }, {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                }>>;
                unit: z.ZodOptional<z.ZodObject<{
                    id: z.ZodOptional<z.ZodNumber>;
                    name: z.ZodOptional<z.ZodString>;
                    description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
                }, "strip", z.ZodTypeAny, {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                }, {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                }>>;
                amount: z.ZodUnion<[z.ZodString, z.ZodNumber]>;
                note: z.ZodOptional<z.ZodString>;
            }, "strip", z.ZodTypeAny, {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }, {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }>, "many">>;
            order: z.ZodOptional<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            instruction: string;
            id?: number | undefined;
            ingredients?: {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }[] | undefined;
            order?: number | undefined;
        }, {
            instruction: string;
            id?: number | undefined;
            ingredients?: {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }[] | undefined;
            order?: number | undefined;
        }>, "many">>>;
    }, "strip", z.ZodTypeAny, {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
        servings?: number | undefined;
        rating?: number | null | undefined;
        keywords?: {
            id: number;
            name?: string | undefined;
            description?: string | undefined;
            label?: string | undefined;
        }[] | undefined;
        steps?: {
            instruction: string;
            id?: number | undefined;
            ingredients?: {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }[] | undefined;
            order?: number | undefined;
        }[] | undefined;
    }, {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
        servings?: number | undefined;
        rating?: number | null | undefined;
        keywords?: {
            id: number;
            name?: string | undefined;
            description?: string | undefined;
            label?: string | undefined;
        }[] | undefined;
        steps?: {
            instruction: string;
            id?: number | undefined;
            ingredients?: {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }[] | undefined;
            order?: number | undefined;
        }[] | undefined;
    }>>;
    meal_type: z.ZodOptional<z.ZodObject<{
        id: z.ZodNumber;
        name: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        id: number;
        name: string;
    }, {
        id: number;
        name: string;
    }>>;
    from_date: z.ZodString;
    to_date: z.ZodOptional<z.ZodString>;
    servings: z.ZodUnion<[z.ZodString, z.ZodNumber]>;
    note: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: number;
    servings: string | number;
    from_date: string;
    note?: string | undefined;
    title?: string | undefined;
    recipe?: {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
        servings?: number | undefined;
        rating?: number | null | undefined;
        keywords?: {
            id: number;
            name?: string | undefined;
            description?: string | undefined;
            label?: string | undefined;
        }[] | undefined;
        steps?: {
            instruction: string;
            id?: number | undefined;
            ingredients?: {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }[] | undefined;
            order?: number | undefined;
        }[] | undefined;
    } | undefined;
    meal_type?: {
        id: number;
        name: string;
    } | undefined;
    to_date?: string | undefined;
}, {
    id: number;
    servings: string | number;
    from_date: string;
    note?: string | undefined;
    title?: string | undefined;
    recipe?: {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
        servings?: number | undefined;
        rating?: number | null | undefined;
        keywords?: {
            id: number;
            name?: string | undefined;
            description?: string | undefined;
            label?: string | undefined;
        }[] | undefined;
        steps?: {
            instruction: string;
            id?: number | undefined;
            ingredients?: {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }[] | undefined;
            order?: number | undefined;
        }[] | undefined;
    } | undefined;
    meal_type?: {
        id: number;
        name: string;
    } | undefined;
    to_date?: string | undefined;
}>;
export type MealPlan = z.infer<typeof MealPlanSchema>;
export declare const MealPlanListResponseSchema: z.ZodArray<z.ZodObject<{
    id: z.ZodNumber;
    title: z.ZodOptional<z.ZodString>;
    recipe: z.ZodOptional<z.ZodObject<{
        id: z.ZodOptional<z.ZodNumber>;
        name: z.ZodOptional<z.ZodString>;
        description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
        servings: z.ZodOptional<z.ZodOptional<z.ZodNumber>>;
        rating: z.ZodOptional<z.ZodOptional<z.ZodNullable<z.ZodNumber>>>;
        keywords: z.ZodOptional<z.ZodOptional<z.ZodArray<z.ZodObject<{
            id: z.ZodNumber;
            name: z.ZodOptional<z.ZodString>;
            label: z.ZodOptional<z.ZodString>;
            description: z.ZodOptional<z.ZodString>;
        }, "strip", z.ZodTypeAny, {
            id: number;
            name?: string | undefined;
            description?: string | undefined;
            label?: string | undefined;
        }, {
            id: number;
            name?: string | undefined;
            description?: string | undefined;
            label?: string | undefined;
        }>, "many">>>;
        steps: z.ZodOptional<z.ZodOptional<z.ZodArray<z.ZodObject<{
            id: z.ZodOptional<z.ZodNumber>;
            instruction: z.ZodString;
            ingredients: z.ZodOptional<z.ZodArray<z.ZodObject<{
                id: z.ZodOptional<z.ZodNumber>;
                food: z.ZodOptional<z.ZodObject<{
                    id: z.ZodOptional<z.ZodNumber>;
                    name: z.ZodOptional<z.ZodString>;
                    description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
                }, "strip", z.ZodTypeAny, {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                }, {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                }>>;
                unit: z.ZodOptional<z.ZodObject<{
                    id: z.ZodOptional<z.ZodNumber>;
                    name: z.ZodOptional<z.ZodString>;
                    description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
                }, "strip", z.ZodTypeAny, {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                }, {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                }>>;
                amount: z.ZodUnion<[z.ZodString, z.ZodNumber]>;
                note: z.ZodOptional<z.ZodString>;
            }, "strip", z.ZodTypeAny, {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }, {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }>, "many">>;
            order: z.ZodOptional<z.ZodNumber>;
        }, "strip", z.ZodTypeAny, {
            instruction: string;
            id?: number | undefined;
            ingredients?: {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }[] | undefined;
            order?: number | undefined;
        }, {
            instruction: string;
            id?: number | undefined;
            ingredients?: {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }[] | undefined;
            order?: number | undefined;
        }>, "many">>>;
    }, "strip", z.ZodTypeAny, {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
        servings?: number | undefined;
        rating?: number | null | undefined;
        keywords?: {
            id: number;
            name?: string | undefined;
            description?: string | undefined;
            label?: string | undefined;
        }[] | undefined;
        steps?: {
            instruction: string;
            id?: number | undefined;
            ingredients?: {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }[] | undefined;
            order?: number | undefined;
        }[] | undefined;
    }, {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
        servings?: number | undefined;
        rating?: number | null | undefined;
        keywords?: {
            id: number;
            name?: string | undefined;
            description?: string | undefined;
            label?: string | undefined;
        }[] | undefined;
        steps?: {
            instruction: string;
            id?: number | undefined;
            ingredients?: {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }[] | undefined;
            order?: number | undefined;
        }[] | undefined;
    }>>;
    meal_type: z.ZodOptional<z.ZodObject<{
        id: z.ZodNumber;
        name: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        id: number;
        name: string;
    }, {
        id: number;
        name: string;
    }>>;
    from_date: z.ZodString;
    to_date: z.ZodOptional<z.ZodString>;
    servings: z.ZodUnion<[z.ZodString, z.ZodNumber]>;
    note: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: number;
    servings: string | number;
    from_date: string;
    note?: string | undefined;
    title?: string | undefined;
    recipe?: {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
        servings?: number | undefined;
        rating?: number | null | undefined;
        keywords?: {
            id: number;
            name?: string | undefined;
            description?: string | undefined;
            label?: string | undefined;
        }[] | undefined;
        steps?: {
            instruction: string;
            id?: number | undefined;
            ingredients?: {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }[] | undefined;
            order?: number | undefined;
        }[] | undefined;
    } | undefined;
    meal_type?: {
        id: number;
        name: string;
    } | undefined;
    to_date?: string | undefined;
}, {
    id: number;
    servings: string | number;
    from_date: string;
    note?: string | undefined;
    title?: string | undefined;
    recipe?: {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
        servings?: number | undefined;
        rating?: number | null | undefined;
        keywords?: {
            id: number;
            name?: string | undefined;
            description?: string | undefined;
            label?: string | undefined;
        }[] | undefined;
        steps?: {
            instruction: string;
            id?: number | undefined;
            ingredients?: {
                amount: string | number;
                id?: number | undefined;
                food?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                unit?: {
                    id?: number | undefined;
                    name?: string | undefined;
                    description?: string | undefined;
                } | undefined;
                note?: string | undefined;
            }[] | undefined;
            order?: number | undefined;
        }[] | undefined;
    } | undefined;
    meal_type?: {
        id: number;
        name: string;
    } | undefined;
    to_date?: string | undefined;
}>, "many">;
export type MealPlanListResponse = z.infer<typeof MealPlanListResponseSchema>;
export declare const ShoppingListItemSchema: z.ZodObject<{
    id: z.ZodNumber;
    food: z.ZodOptional<z.ZodObject<{
        id: z.ZodOptional<z.ZodNumber>;
        name: z.ZodOptional<z.ZodString>;
        description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    }, "strip", z.ZodTypeAny, {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    }, {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    }>>;
    unit: z.ZodOptional<z.ZodObject<{
        id: z.ZodOptional<z.ZodNumber>;
        name: z.ZodOptional<z.ZodString>;
        description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    }, "strip", z.ZodTypeAny, {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    }, {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    }>>;
    amount: z.ZodUnion<[z.ZodString, z.ZodNumber]>;
    checked: z.ZodOptional<z.ZodBoolean>;
    note: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: number;
    amount: string | number;
    food?: {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    } | undefined;
    unit?: {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    } | undefined;
    note?: string | undefined;
    checked?: boolean | undefined;
}, {
    id: number;
    amount: string | number;
    food?: {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    } | undefined;
    unit?: {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    } | undefined;
    note?: string | undefined;
    checked?: boolean | undefined;
}>;
export type ShoppingListItem = z.infer<typeof ShoppingListItemSchema>;
export declare const ShoppingListResponseSchema: z.ZodArray<z.ZodObject<{
    id: z.ZodNumber;
    food: z.ZodOptional<z.ZodObject<{
        id: z.ZodOptional<z.ZodNumber>;
        name: z.ZodOptional<z.ZodString>;
        description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    }, "strip", z.ZodTypeAny, {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    }, {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    }>>;
    unit: z.ZodOptional<z.ZodObject<{
        id: z.ZodOptional<z.ZodNumber>;
        name: z.ZodOptional<z.ZodString>;
        description: z.ZodOptional<z.ZodOptional<z.ZodString>>;
    }, "strip", z.ZodTypeAny, {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    }, {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    }>>;
    amount: z.ZodUnion<[z.ZodString, z.ZodNumber]>;
    checked: z.ZodOptional<z.ZodBoolean>;
    note: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    id: number;
    amount: string | number;
    food?: {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    } | undefined;
    unit?: {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    } | undefined;
    note?: string | undefined;
    checked?: boolean | undefined;
}, {
    id: number;
    amount: string | number;
    food?: {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    } | undefined;
    unit?: {
        id?: number | undefined;
        name?: string | undefined;
        description?: string | undefined;
    } | undefined;
    note?: string | undefined;
    checked?: boolean | undefined;
}>, "many">;
export type ShoppingListResponse = z.infer<typeof ShoppingListResponseSchema>;
export declare const PaginatedResponseSchema: <T extends z.ZodTypeAny>(itemSchema: T) => z.ZodObject<{
    count: z.ZodOptional<z.ZodNumber>;
    next: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    previous: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    results: z.ZodArray<T, "many">;
}, "strip", z.ZodTypeAny, {
    results: T["_output"][];
    count?: number | undefined;
    next?: string | null | undefined;
    previous?: string | null | undefined;
}, {
    results: T["_input"][];
    count?: number | undefined;
    next?: string | null | undefined;
    previous?: string | null | undefined;
}>;
export declare const FoodListResponseSchema: z.ZodObject<{
    count: z.ZodOptional<z.ZodNumber>;
    next: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    previous: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    results: z.ZodArray<z.ZodObject<{
        id: z.ZodNumber;
        name: z.ZodString;
        description: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        id: number;
        name: string;
        description?: string | undefined;
    }, {
        id: number;
        name: string;
        description?: string | undefined;
    }>, "many">;
}, "strip", z.ZodTypeAny, {
    results: {
        id: number;
        name: string;
        description?: string | undefined;
    }[];
    count?: number | undefined;
    next?: string | null | undefined;
    previous?: string | null | undefined;
}, {
    results: {
        id: number;
        name: string;
        description?: string | undefined;
    }[];
    count?: number | undefined;
    next?: string | null | undefined;
    previous?: string | null | undefined;
}>;
export declare const UnitListResponseSchema: z.ZodObject<{
    count: z.ZodOptional<z.ZodNumber>;
    next: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    previous: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    results: z.ZodArray<z.ZodObject<{
        id: z.ZodNumber;
        name: z.ZodString;
        description: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        id: number;
        name: string;
        description?: string | undefined;
    }, {
        id: number;
        name: string;
        description?: string | undefined;
    }>, "many">;
}, "strip", z.ZodTypeAny, {
    results: {
        id: number;
        name: string;
        description?: string | undefined;
    }[];
    count?: number | undefined;
    next?: string | null | undefined;
    previous?: string | null | undefined;
}, {
    results: {
        id: number;
        name: string;
        description?: string | undefined;
    }[];
    count?: number | undefined;
    next?: string | null | undefined;
    previous?: string | null | undefined;
}>;
export declare const KeywordListResponseSchema: z.ZodObject<{
    count: z.ZodOptional<z.ZodNumber>;
    next: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    previous: z.ZodOptional<z.ZodNullable<z.ZodString>>;
    results: z.ZodArray<z.ZodObject<{
        id: z.ZodNumber;
        name: z.ZodOptional<z.ZodString>;
        label: z.ZodOptional<z.ZodString>;
        description: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        id: number;
        name?: string | undefined;
        description?: string | undefined;
        label?: string | undefined;
    }, {
        id: number;
        name?: string | undefined;
        description?: string | undefined;
        label?: string | undefined;
    }>, "many">;
}, "strip", z.ZodTypeAny, {
    results: {
        id: number;
        name?: string | undefined;
        description?: string | undefined;
        label?: string | undefined;
    }[];
    count?: number | undefined;
    next?: string | null | undefined;
    previous?: string | null | undefined;
}, {
    results: {
        id: number;
        name?: string | undefined;
        description?: string | undefined;
        label?: string | undefined;
    }[];
    count?: number | undefined;
    next?: string | null | undefined;
    previous?: string | null | undefined;
}>;
export declare const CreateRecipePayloadSchema: z.ZodObject<{
    name: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    servings: z.ZodOptional<z.ZodNumber>;
    steps: z.ZodArray<z.ZodObject<{
        instruction: z.ZodString;
        ingredients: z.ZodArray<z.ZodObject<{
            food: z.ZodObject<{
                name: z.ZodString;
            }, "strip", z.ZodTypeAny, {
                name: string;
            }, {
                name: string;
            }>;
            unit: z.ZodObject<{
                name: z.ZodString;
            }, "strip", z.ZodTypeAny, {
                name: string;
            }, {
                name: string;
            }>;
            amount: z.ZodString;
        }, "strip", z.ZodTypeAny, {
            food: {
                name: string;
            };
            unit: {
                name: string;
            };
            amount: string;
        }, {
            food: {
                name: string;
            };
            unit: {
                name: string;
            };
            amount: string;
        }>, "many">;
    }, "strip", z.ZodTypeAny, {
        instruction: string;
        ingredients: {
            food: {
                name: string;
            };
            unit: {
                name: string;
            };
            amount: string;
        }[];
    }, {
        instruction: string;
        ingredients: {
            food: {
                name: string;
            };
            unit: {
                name: string;
            };
            amount: string;
        }[];
    }>, "many">;
}, "strip", z.ZodTypeAny, {
    name: string;
    steps: {
        instruction: string;
        ingredients: {
            food: {
                name: string;
            };
            unit: {
                name: string;
            };
            amount: string;
        }[];
    }[];
    description?: string | undefined;
    servings?: number | undefined;
}, {
    name: string;
    steps: {
        instruction: string;
        ingredients: {
            food: {
                name: string;
            };
            unit: {
                name: string;
            };
            amount: string;
        }[];
    }[];
    description?: string | undefined;
    servings?: number | undefined;
}>;
export type CreateRecipePayload = z.infer<typeof CreateRecipePayloadSchema>;
export declare const CreateMealPlanPayloadSchema: z.ZodObject<{
    recipe: z.ZodObject<{
        id: z.ZodNumber;
        name: z.ZodString;
        keywords: z.ZodArray<z.ZodUnknown, "many">;
    }, "strip", z.ZodTypeAny, {
        id: number;
        name: string;
        keywords: unknown[];
    }, {
        id: number;
        name: string;
        keywords: unknown[];
    }>;
    meal_type: z.ZodObject<{
        id: z.ZodNumber;
        name: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        id: number;
        name: string;
    }, {
        id: number;
        name: string;
    }>;
    from_date: z.ZodString;
    servings: z.ZodString;
    title: z.ZodOptional<z.ZodString>;
    note: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    servings: string;
    recipe: {
        id: number;
        name: string;
        keywords: unknown[];
    };
    meal_type: {
        id: number;
        name: string;
    };
    from_date: string;
    note?: string | undefined;
    title?: string | undefined;
}, {
    servings: string;
    recipe: {
        id: number;
        name: string;
        keywords: unknown[];
    };
    meal_type: {
        id: number;
        name: string;
    };
    from_date: string;
    note?: string | undefined;
    title?: string | undefined;
}>;
export type CreateMealPlanPayload = z.infer<typeof CreateMealPlanPayloadSchema>;
export declare const AddShoppingItemPayloadSchema: z.ZodObject<{
    food: z.ZodObject<{
        id: z.ZodNumber;
        name: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        id: number;
        name: string;
    }, {
        id: number;
        name: string;
    }>;
    unit: z.ZodObject<{
        id: z.ZodNumber;
        name: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        id: number;
        name: string;
    }, {
        id: number;
        name: string;
    }>;
    amount: z.ZodString;
    note: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    food: {
        id: number;
        name: string;
    };
    unit: {
        id: number;
        name: string;
    };
    amount: string;
    note?: string | undefined;
}, {
    food: {
        id: number;
        name: string;
    };
    unit: {
        id: number;
        name: string;
    };
    amount: string;
    note?: string | undefined;
}>;
export type AddShoppingItemPayload = z.infer<typeof AddShoppingItemPayloadSchema>;
export declare const UpdateShoppingItemPayloadSchema: z.ZodObject<{
    checked: z.ZodOptional<z.ZodBoolean>;
    amount: z.ZodOptional<z.ZodString>;
    unit: z.ZodOptional<z.ZodNumber>;
    note: z.ZodOptional<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    unit?: number | undefined;
    amount?: string | undefined;
    note?: string | undefined;
    checked?: boolean | undefined;
}, {
    unit?: number | undefined;
    amount?: string | undefined;
    note?: string | undefined;
    checked?: boolean | undefined;
}>;
export type UpdateShoppingItemPayload = z.infer<typeof UpdateShoppingItemPayloadSchema>;
//# sourceMappingURL=schemas.d.ts.map