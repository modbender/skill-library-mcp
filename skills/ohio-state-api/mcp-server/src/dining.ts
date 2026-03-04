import { Tool } from "@modelcontextprotocol/sdk/types.js";
import { addLocalTimeToResponse, getCurrentEasternTime } from "./utils.js";

const BASE_URL = "https://content.osu.edu/v2/api/v1/dining";

export const diningTools: Tool[] = [
  {
    name: "get_dining_locations",
    description: "Get all OSU dining locations with basic information",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },
  {
    name: "get_dining_locations_with_menus",
    description: "Get all OSU dining locations with menu section information",
    inputSchema: {
      type: "object", 
      properties: {},
      required: []
    }
  },
  {
    name: "get_dining_menu",
    description: "Get detailed menu items for a specific dining location section",
    inputSchema: {
      type: "object",
      properties: {
        section_id: {
          type: "number",
          description: "Section ID from the location menu (found in get_dining_locations_with_menus response)"
        }
      },
      required: ["section_id"]
    }
  }
];

export async function handleDiningTool(name: string, args: any): Promise<any> {
  try {
    switch (name) {
      case "get_dining_locations":
        const locationsResponse = await fetch(`${BASE_URL}/locations`);
        const locationsData = await locationsResponse.json();
        const processedLocationsData = addLocalTimeToResponse(locationsData);
        
        return {
          content: [{
            type: "text",
            text: `OSU Dining Locations (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedLocationsData, null, 2)}`
          }]
        };

      case "get_dining_locations_with_menus":
        const locationsMenusResponse = await fetch(`${BASE_URL}/locations/menus`);
        const locationsMenusData = await locationsMenusResponse.json();
        const processedLocationsMenusData = addLocalTimeToResponse(locationsMenusData);
        
        return {
          content: [{
            type: "text",
            text: `OSU Dining Locations with Menu Information (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedLocationsMenusData, null, 2)}`
          }]
        };

      case "get_dining_menu":
        const { section_id } = args;
        if (!section_id || typeof section_id !== 'number') {
          throw new Error('Section ID must be a valid number');
        }

        const menuResponse = await fetch(`${BASE_URL}/full/menu/section/${section_id}`);
        const menuData = await menuResponse.json();
        const processedMenuData = addLocalTimeToResponse(menuData);
        
        return {
          content: [{
            type: "text",
            text: `Menu for Section ${section_id} (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedMenuData, null, 2)}`
          }]
        };

      default:
        throw new Error(`Unknown dining tool: ${name}`);
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