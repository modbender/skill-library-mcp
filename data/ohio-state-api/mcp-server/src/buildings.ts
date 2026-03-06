import { Tool } from "@modelcontextprotocol/sdk/types.js";
import { addLocalTimeToResponse, getCurrentEasternTime } from "./utils.js";

const BASE_URL = "https://content.osu.edu/v2/api";

export const buildingTools: Tool[] = [
  {
    name: "get_buildings",
    description: "Get information about all OSU buildings including addresses, locations, departments, and room details",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },
  {
    name: "search_buildings",
    description: "Search for buildings by name or building number",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search term for building name or building number"
        }
      },
      required: ["query"]
    }
  },
  {
    name: "get_building_details",
    description: "Get detailed information about a specific building including rooms, departments, and special spaces",
    inputSchema: {
      type: "object",
      properties: {
        building_number: {
          type: "string",
          description: "Building number to get details for"
        }
      },
      required: ["building_number"]
    }
  },
  {
    name: "find_room_type",
    description: "Find buildings that contain specific room types (lactation rooms, sanctuaries, wellness spaces, gender inclusive restrooms)",
    inputSchema: {
      type: "object",
      properties: {
        room_type: {
          type: "string",
          description: "Type of room to search for",
          enum: ["lactation", "sanctuary", "wellness", "gender_inclusive_restroom"]
        }
      },
      required: ["room_type"]
    }
  }
];

export async function handleBuildingTool(name: string, args: any): Promise<any> {
  try {
    switch (name) {
      case "get_buildings":
        const buildingsResponse = await fetch(`${BASE_URL}/buildings`);
        const buildingsData = await buildingsResponse.json();
        const processedBuildingsData = addLocalTimeToResponse(buildingsData);
        
        return {
          content: [{
            type: "text",
            text: `OSU Buildings (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedBuildingsData, null, 2)}`
          }]
        };

      case "search_buildings":
        const { query } = args;
        const searchResponse = await fetch(`${BASE_URL}/buildings`);
        const searchData = await searchResponse.json();
        
        if (!searchData.data || !searchData.data.buildings) {
          throw new Error("Invalid response format from buildings API");
        }

        const filteredBuildings = searchData.data.buildings.filter((building: any) => 
          building.name?.toLowerCase().includes(query.toLowerCase()) ||
          building.buildingNumber?.toLowerCase().includes(query.toLowerCase())
        );

        const searchResult = {
          ...searchData,
          data: {
            ...searchData.data,
            buildings: filteredBuildings
          }
        };

        const processedSearchData = addLocalTimeToResponse(searchResult);
        
        return {
          content: [{
            type: "text",
            text: `Buildings matching "${query}" (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedSearchData, null, 2)}`
          }]
        };

      case "get_building_details":
        const { building_number } = args;
        const detailsResponse = await fetch(`${BASE_URL}/buildings`);
        const detailsData = await detailsResponse.json();
        
        if (!detailsData.data || !detailsData.data.buildings) {
          throw new Error("Invalid response format from buildings API");
        }

        const building = detailsData.data.buildings.find((b: any) => 
          b.buildingNumber === building_number
        );

        if (!building) {
          throw new Error(`Building with number "${building_number}" not found`);
        }

        const buildingResult = {
          ...detailsData,
          data: {
            ...detailsData.data,
            buildings: [building]
          }
        };

        const processedBuildingData = addLocalTimeToResponse(buildingResult);
        
        return {
          content: [{
            type: "text",
            text: `Details for Building ${building_number} (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedBuildingData, null, 2)}`
          }]
        };

      case "find_room_type":
        const { room_type } = args;
        const roomTypeResponse = await fetch(`${BASE_URL}/buildings`);
        const roomTypeData = await roomTypeResponse.json();
        
        if (!roomTypeData.data || !roomTypeData.data.buildings) {
          throw new Error("Invalid response format from buildings API");
        }

        const roomTypeMap = {
          "lactation": "lactationRooms",
          "sanctuary": "sanctuaries", 
          "wellness": "wellnessSpaceRooms",
          "gender_inclusive_restroom": "genderInclusiveRestrooms"
        };

        const roomField = roomTypeMap[room_type as keyof typeof roomTypeMap];
        if (!roomField) {
          throw new Error(`Invalid room type: ${room_type}`);
        }

        const buildingsWithRooms = roomTypeData.data.buildings.filter((building: any) => 
          building[roomField] && building[roomField].length > 0
        );

        const roomTypeResult = {
          ...roomTypeData,
          data: {
            ...roomTypeData.data,
            buildings: buildingsWithRooms
          }
        };

        const processedRoomTypeData = addLocalTimeToResponse(roomTypeResult);
        
        return {
          content: [{
            type: "text",
            text: `Buildings with ${room_type.replace('_', ' ')} rooms (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedRoomTypeData, null, 2)}`
          }]
        };

      default:
        throw new Error(`Unknown building tool: ${name}`);
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