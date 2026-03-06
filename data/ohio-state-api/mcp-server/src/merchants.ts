import { Tool } from "@modelcontextprotocol/sdk/types.js";
import { addLocalTimeToResponse, getCurrentEasternTime } from "./utils.js";

const BASE_URL = "https://content.osu.edu/v2";

export const merchantTools: Tool[] = [
  {
    name: "get_buckid_merchants",
    description: "Get information about all merchants that accept BuckID",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },
  {
    name: "search_merchants",
    description: "Search for merchants by name or category",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search term for merchant name or category"
        }
      },
      required: ["query"]
    }
  },
  {
    name: "get_merchants_by_food_type",
    description: "Find merchants by food/cuisine type",
    inputSchema: {
      type: "object",
      properties: {
        food_type: {
          type: "string",
          description: "Food or cuisine type to search for"
        }
      },
      required: ["food_type"]
    }
  },
  {
    name: "get_merchants_with_meal_plan",
    description: "Find merchants that accept meal plans",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  }
];

export async function handleMerchantTool(name: string, args: any): Promise<any> {
  try {
    switch (name) {
      case "get_buckid_merchants":
        const merchantsResponse = await fetch(`${BASE_URL}/merchants`);
        const merchantsData = await merchantsResponse.json();
        const processedMerchantsData = addLocalTimeToResponse(merchantsData);
        
        return {
          content: [{
            type: "text",
            text: `BuckID Merchants (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedMerchantsData, null, 2)}`
          }]
        };

      case "search_merchants":
        const { query } = args;
        const searchResponse = await fetch(`${BASE_URL}/merchants`);
        const searchData = await searchResponse.json();
        
        if (!searchData.data || !searchData.data.merchants) {
          throw new Error("Invalid response format from merchants API");
        }

        const filteredMerchants = searchData.data.merchants.filter((merchant: any) => 
          merchant.title?.toLowerCase().includes(query.toLowerCase()) ||
          merchant.categories?.some((category: string) => 
            category.toLowerCase().includes(query.toLowerCase())
          )
        );

        const searchResult = {
          ...searchData,
          data: {
            ...searchData.data,
            merchants: filteredMerchants
          }
        };

        const processedSearchData = addLocalTimeToResponse(searchResult);
        
        return {
          content: [{
            type: "text",
            text: `Merchants matching "${query}" (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedSearchData, null, 2)}`
          }]
        };

      case "get_merchants_by_food_type":
        const { food_type } = args;
        const foodTypeResponse = await fetch(`${BASE_URL}/merchants`);
        const foodTypeData = await foodTypeResponse.json();
        
        if (!foodTypeData.data || !foodTypeData.data.merchants) {
          throw new Error("Invalid response format from merchants API");
        }

        const foodTypeMerchants = foodTypeData.data.merchants.filter((merchant: any) => 
          merchant.foodTypes?.some((type: string) => 
            type.toLowerCase().includes(food_type.toLowerCase())
          )
        );

        const foodTypeResult = {
          ...foodTypeData,
          data: {
            ...foodTypeData.data,
            merchants: foodTypeMerchants
          }
        };

        const processedFoodTypeData = addLocalTimeToResponse(foodTypeResult);
        
        return {
          content: [{
            type: "text",
            text: `Merchants with food type "${food_type}" (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedFoodTypeData, null, 2)}`
          }]
        };

      case "get_merchants_with_meal_plan":
        const mealPlanResponse = await fetch(`${BASE_URL}/merchants`);
        const mealPlanData = await mealPlanResponse.json();
        
        if (!mealPlanData.data || !mealPlanData.data.merchants) {
          throw new Error("Invalid response format from merchants API");
        }

        const mealPlanMerchants = mealPlanData.data.merchants.filter((merchant: any) => 
          merchant.hasMealPlan === true
        );

        const mealPlanResult = {
          ...mealPlanData,
          data: {
            ...mealPlanData.data,
            merchants: mealPlanMerchants
          }
        };

        const processedMealPlanData = addLocalTimeToResponse(mealPlanResult);
        
        return {
          content: [{
            type: "text",
            text: `Merchants accepting meal plans (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedMealPlanData, null, 2)}`
          }]
        };

      default:
        throw new Error(`Unknown merchant tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error: ${error instanceof Error ? error.message : String(error)}`
      }],
      isError: true
    };
  }
}