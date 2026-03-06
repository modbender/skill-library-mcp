import { z } from 'zod';
// ============================================
// Base Types
// ============================================
export const FoodSchema = z.object({
    id: z.number(),
    name: z.string(),
    description: z.string().optional(),
});
export const UnitSchema = z.object({
    id: z.number(),
    name: z.string(),
    description: z.string().optional(),
});
export const KeywordSchema = z.object({
    id: z.number(),
    name: z.string().optional(),
    label: z.string().optional(),
    description: z.string().optional(),
});
export const MealTypeSchema = z.object({
    id: z.number(),
    name: z.string(),
});
// ============================================
// Recipe Types
// ============================================
export const IngredientSchema = z.object({
    id: z.number().optional(),
    food: FoodSchema.partial().optional(),
    unit: UnitSchema.partial().optional(),
    amount: z.union([z.string(), z.number()]),
    note: z.string().optional(),
});
export const StepSchema = z.object({
    id: z.number().optional(),
    instruction: z.string(),
    ingredients: z.array(IngredientSchema).optional(),
    order: z.number().optional(),
});
export const RecipeSchema = z.object({
    id: z.number(),
    name: z.string(),
    description: z.string().optional(),
    servings: z.number().optional(),
    rating: z.number().nullable().optional(),
    keywords: z.array(KeywordSchema).optional(),
    steps: z.array(StepSchema).optional(),
});
export const RecipeListResponseSchema = z.object({
    count: z.number(),
    next: z.string().nullable(),
    previous: z.string().nullable(),
    results: z.array(RecipeSchema),
});
// ============================================
// Meal Plan Types
// ============================================
export const MealPlanSchema = z.object({
    id: z.number(),
    title: z.string().optional(),
    recipe: RecipeSchema.partial().optional(),
    meal_type: MealTypeSchema.optional(),
    from_date: z.string(),
    to_date: z.string().optional(),
    servings: z.union([z.string(), z.number()]),
    note: z.string().optional(),
});
export const MealPlanListResponseSchema = z.array(MealPlanSchema);
// ============================================
// Shopping List Types
// ============================================
export const ShoppingListItemSchema = z.object({
    id: z.number(),
    food: FoodSchema.partial().optional(),
    unit: UnitSchema.partial().optional(),
    amount: z.union([z.string(), z.number()]),
    checked: z.boolean().optional(),
    note: z.string().optional(),
});
export const ShoppingListResponseSchema = z.array(ShoppingListItemSchema);
// ============================================
// Paginated List Response (generic)
// ============================================
export const PaginatedResponseSchema = (itemSchema) => z.object({
    count: z.number().optional(),
    next: z.string().nullable().optional(),
    previous: z.string().nullable().optional(),
    results: z.array(itemSchema),
});
export const FoodListResponseSchema = PaginatedResponseSchema(FoodSchema);
export const UnitListResponseSchema = PaginatedResponseSchema(UnitSchema);
export const KeywordListResponseSchema = PaginatedResponseSchema(KeywordSchema);
// ============================================
// Request Payload Types
// ============================================
export const CreateRecipePayloadSchema = z.object({
    name: z.string(),
    description: z.string().optional(),
    servings: z.number().optional(),
    steps: z.array(z.object({
        instruction: z.string(),
        ingredients: z.array(z.object({
            food: z.object({ name: z.string() }),
            unit: z.object({ name: z.string() }),
            amount: z.string(),
        })),
    })),
});
export const CreateMealPlanPayloadSchema = z.object({
    recipe: z.object({
        id: z.number(),
        name: z.string(),
        keywords: z.array(z.unknown()),
    }),
    meal_type: z.object({
        id: z.number(),
        name: z.string(),
    }),
    from_date: z.string(),
    servings: z.string(),
    title: z.string().optional(),
    note: z.string().optional(),
});
export const AddShoppingItemPayloadSchema = z.object({
    food: z.object({ id: z.number(), name: z.string() }),
    unit: z.object({ id: z.number(), name: z.string() }),
    amount: z.string(),
    note: z.string().optional(),
});
export const UpdateShoppingItemPayloadSchema = z.object({
    checked: z.boolean().optional(),
    amount: z.string().optional(),
    unit: z.number().optional(),
    note: z.string().optional(),
});
//# sourceMappingURL=schemas.js.map