import { Tool } from "@modelcontextprotocol/sdk/types.js";
import { addLocalTimeToResponse, getCurrentEasternTime } from "./utils.js";

const BASE_URL = "https://content.osu.edu/v2/foodtruck";

export const foodtruckTools: Tool[] = [
  {
    name: "get_foodtruck_events",
    description: "Get information about all food truck events on campus",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },
  {
    name: "search_foodtrucks",
    description: "Search for food trucks by name or cuisine type",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search term for food truck name or cuisine type"
        }
      },
      required: ["query"]
    }
  },
  {
    name: "get_foodtrucks_by_location",
    description: "Find food trucks at a specific location",
    inputSchema: {
      type: "object",
      properties: {
        location: {
          type: "string",
          description: "Location to search for food trucks"
        }
      },
      required: ["location"]
    }
  }
];

export async function handleFoodtruckTool(name: string, args: any): Promise<any> {
  try {
    switch (name) {
      case "get_foodtruck_events":
        const eventsResponse = await fetch(`${BASE_URL}/events`);
        const eventsData = await eventsResponse.json();
        const processedEventsData = addLocalTimeToResponse(eventsData);
        
        return {
          content: [{
            type: "text",
            text: `Food Truck Events (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedEventsData, null, 2)}`
          }]
        };

      case "search_foodtrucks":
        const { query } = args;
        const searchResponse = await fetch(`${BASE_URL}/events`);
        const searchData = await searchResponse.json();
        
        if (!searchData.data || !searchData.data.events) {
          throw new Error("Invalid response format from foodtruck events API");
        }

        const filteredEvents = searchData.data.events.filter((event: any) => 
          event.name?.toLowerCase().includes(query.toLowerCase()) ||
          event.cuisineTypes?.some((cuisine: string) => 
            cuisine.toLowerCase().includes(query.toLowerCase())
          )
        );

        const searchResult = {
          ...searchData,
          data: {
            ...searchData.data,
            events: filteredEvents
          }
        };

        const processedSearchData = addLocalTimeToResponse(searchResult);
        
        return {
          content: [{
            type: "text",
            text: `Food trucks matching "${query}" (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedSearchData, null, 2)}`
          }]
        };

      case "get_foodtrucks_by_location":
        const { location } = args;
        const locationResponse = await fetch(`${BASE_URL}/events`);
        const locationData = await locationResponse.json();
        
        if (!locationData.data || !locationData.data.events) {
          throw new Error("Invalid response format from foodtruck events API");
        }

        const locationEvents = locationData.data.events.filter((event: any) => 
          event.location?.address?.toLowerCase().includes(location.toLowerCase()) ||
          event.location?.name?.toLowerCase().includes(location.toLowerCase())
        );

        const locationResult = {
          ...locationData,
          data: {
            ...locationData.data,
            events: locationEvents
          }
        };

        const processedLocationData = addLocalTimeToResponse(locationResult);
        
        return {
          content: [{
            type: "text",
            text: `Food trucks at "${location}" (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedLocationData, null, 2)}`
          }]
        };

      default:
        throw new Error(`Unknown foodtruck tool: ${name}`);
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