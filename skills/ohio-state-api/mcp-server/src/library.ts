import { Tool } from "@modelcontextprotocol/sdk/types.js";
import { addLocalTimeToResponse, getCurrentEasternTime } from "./utils.js";

const BASE_URL = "https://content.osu.edu/v2/library";

export const libraryTools: Tool[] = [
  {
    name: "get_library_locations",
    description: "Get information about all OSU library locations including addresses, hours, and contact details",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },
  {
    name: "search_library_locations",
    description: "Search for library locations by name",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search term for library name"
        }
      },
      required: ["query"]
    }
  },
  {
    name: "get_library_rooms",
    description: "Get information about all available library study rooms for reservation",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },
  {
    name: "search_library_rooms",
    description: "Search for library study rooms by name or location",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search term for room name or location"
        }
      },
      required: ["query"]
    }
  },
  {
    name: "get_rooms_by_capacity",
    description: "Find library study rooms that can accommodate a specific number of people",
    inputSchema: {
      type: "object",
      properties: {
        min_capacity: {
          type: "number",
          description: "Minimum number of people the room should accommodate"
        },
        max_capacity: {
          type: "number",
          description: "Maximum number of people (optional)"
        }
      },
      required: ["min_capacity"]
    }
  },
  {
    name: "get_rooms_with_amenities",
    description: "Find library study rooms that have specific amenities",
    inputSchema: {
      type: "object",
      properties: {
        amenities: {
          type: "array",
          items: {
            type: "string",
            enum: ["whiteboard", "HDTV", "video conferencing", "computer", "projector"]
          },
          description: "List of required amenities"
        }
      },
      required: ["amenities"]
    }
  }
];

export async function handleLibraryTool(name: string, args: any): Promise<any> {
  try {
    switch (name) {
      case "get_library_locations":
        const locationsResponse = await fetch(`${BASE_URL}/locations`);
        const locationsData = await locationsResponse.json();
        const processedLocationsData = addLocalTimeToResponse(locationsData);
        
        return {
          content: [{
            type: "text",
            text: `OSU Library Locations (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedLocationsData, null, 2)}`
          }]
        };

      case "search_library_locations":
        const { query } = args;
        const searchLocationsResponse = await fetch(`${BASE_URL}/locations`);
        const searchLocationsData = await searchLocationsResponse.json();
        
        if (!searchLocationsData.data || !searchLocationsData.data.locations) {
          throw new Error("Invalid response format from library locations API");
        }

        const filteredLocations = searchLocationsData.data.locations.filter((location: any) => 
          location.name?.toLowerCase().includes(query.toLowerCase())
        );

        const searchLocationsResult = {
          ...searchLocationsData,
          data: {
            ...searchLocationsData.data,
            locations: filteredLocations
          }
        };

        const processedSearchLocationsData = addLocalTimeToResponse(searchLocationsResult);
        
        return {
          content: [{
            type: "text",
            text: `Library locations matching "${query}" (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedSearchLocationsData, null, 2)}`
          }]
        };

      case "get_library_rooms":
        const roomsResponse = await fetch(`${BASE_URL}/roomreservation/api/v1/rooms`);
        const roomsData = await roomsResponse.json();
        const processedRoomsData = addLocalTimeToResponse(roomsData);
        
        return {
          content: [{
            type: "text",
            text: `OSU Library Study Rooms (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedRoomsData, null, 2)}`
          }]
        };

      case "search_library_rooms":
        const { query: roomQuery } = args;
        const searchRoomsResponse = await fetch(`${BASE_URL}/roomreservation/api/v1/rooms`);
        const searchRoomsData = await searchRoomsResponse.json();
        
        if (!searchRoomsData.data || !searchRoomsData.data.rooms) {
          throw new Error("Invalid response format from library rooms API");
        }

        const filteredRooms = searchRoomsData.data.rooms.filter((room: any) => 
          room.roomName?.toLowerCase().includes(roomQuery.toLowerCase()) ||
          room.location?.toLowerCase().includes(roomQuery.toLowerCase())
        );

        const searchRoomsResult = {
          ...searchRoomsData,
          data: {
            ...searchRoomsData.data,
            rooms: filteredRooms
          }
        };

        const processedSearchRoomsData = addLocalTimeToResponse(searchRoomsResult);
        
        return {
          content: [{
            type: "text",
            text: `Library rooms matching "${roomQuery}" (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedSearchRoomsData, null, 2)}`
          }]
        };

      case "get_rooms_by_capacity":
        const { min_capacity, max_capacity } = args;
        const capacityRoomsResponse = await fetch(`${BASE_URL}/roomreservation/api/v1/rooms`);
        const capacityRoomsData = await capacityRoomsResponse.json();
        
        if (!capacityRoomsData.data || !capacityRoomsData.data.rooms) {
          throw new Error("Invalid response format from library rooms API");
        }

        const roomsByCapacity = capacityRoomsData.data.rooms.filter((room: any) => {
          const roomMaxCapacity = room.capacity?.maximum || 0;
          const meetsMinCapacity = roomMaxCapacity >= min_capacity;
          const meetsMaxCapacity = max_capacity ? roomMaxCapacity <= max_capacity : true;
          return meetsMinCapacity && meetsMaxCapacity;
        });

        const capacityRoomsResult = {
          ...capacityRoomsData,
          data: {
            ...capacityRoomsData.data,
            rooms: roomsByCapacity
          }
        };

        const processedCapacityRoomsData = addLocalTimeToResponse(capacityRoomsResult);
        
        return {
          content: [{
            type: "text",
            text: `Library rooms with capacity ${min_capacity}${max_capacity ? `-${max_capacity}` : '+'} people (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedCapacityRoomsData, null, 2)}`
          }]
        };

      case "get_rooms_with_amenities":
        const { amenities } = args;
        const amenitiesRoomsResponse = await fetch(`${BASE_URL}/roomreservation/api/v1/rooms`);
        const amenitiesRoomsData = await amenitiesRoomsResponse.json();
        
        if (!amenitiesRoomsData.data || !amenitiesRoomsData.data.rooms) {
          throw new Error("Invalid response format from library rooms API");
        }

        const roomsWithAmenities = amenitiesRoomsData.data.rooms.filter((room: any) => {
          if (!room.amenities || !Array.isArray(room.amenities)) {
            return false;
          }
          
          return amenities.every((requiredAmenity: string) =>
            room.amenities.some((roomAmenity: any) =>
              roomAmenity.name?.toLowerCase().includes(requiredAmenity.toLowerCase()) ||
              roomAmenity.toLowerCase?.().includes(requiredAmenity.toLowerCase())
            )
          );
        });

        const amenitiesRoomsResult = {
          ...amenitiesRoomsData,
          data: {
            ...amenitiesRoomsData.data,
            rooms: roomsWithAmenities
          }
        };

        const processedAmenitiesRoomsData = addLocalTimeToResponse(amenitiesRoomsResult);
        
        return {
          content: [{
            type: "text",
            text: `Library rooms with amenities [${amenities.join(', ')}] (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedAmenitiesRoomsData, null, 2)}`
          }]
        };

      default:
        throw new Error(`Unknown library tool: ${name}`);
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