import { Tool } from "@modelcontextprotocol/sdk/types.js";
import { addLocalTimeToResponse, getCurrentEasternTime } from "./utils.js";

const BASE_URL = "https://content.osu.edu/v3";

export const recsportsTools: Tool[] = [
  {
    name: "get_recsports_facilities",
    description: "Get information about all OSU recreation sports facilities including hours, availability, and events",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },
  {
    name: "search_recsports_facilities",
    description: "Search for recreation sports facilities by name or abbreviation",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search term for facility name or abbreviation"
        }
      },
      required: ["query"]
    }
  },
  {
    name: "get_facility_details",
    description: "Get detailed information about a specific recreation sports facility",
    inputSchema: {
      type: "object",
      properties: {
        facility_id: {
          type: "string",
          description: "Facility ID to get details for"
        }
      },
      required: ["facility_id"]
    }
  },
  {
    name: "get_facility_hours",
    description: "Get current operating hours and open/closed status for all recreation facilities",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },
  {
    name: "get_facility_events",
    description: "Get scheduled events for recreation sports facilities",
    inputSchema: {
      type: "object",
      properties: {
        facility_id: {
          type: "string",
          description: "Optional facility ID to filter events for a specific facility"
        }
      },
      required: []
    }
  }
];

export async function handleRecsportsTool(name: string, args: any): Promise<any> {
  try {
    switch (name) {
      case "get_recsports_facilities":
        const facilitiesResponse = await fetch(`${BASE_URL}/recsports`);
        const facilitiesData = await facilitiesResponse.json();
        const processedFacilitiesData = addLocalTimeToResponse(facilitiesData);
        
        return {
          content: [{
            type: "text",
            text: `OSU Recreation Sports Facilities (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedFacilitiesData, null, 2)}`
          }]
        };

      case "search_recsports_facilities":
        const { query } = args;
        const searchResponse = await fetch(`${BASE_URL}/recsports`);
        const searchData = await searchResponse.json();
        
        if (!searchData.data || !searchData.data.facilities) {
          throw new Error("Invalid response format from recsports API");
        }

        const filteredFacilities = searchData.data.facilities.filter((facility: any) => 
          facility.name?.toLowerCase().includes(query.toLowerCase()) ||
          facility.abbreviation?.toLowerCase().includes(query.toLowerCase())
        );

        const searchResult = {
          ...searchData,
          data: {
            ...searchData.data,
            facilities: filteredFacilities
          }
        };

        const processedSearchData = addLocalTimeToResponse(searchResult);
        
        return {
          content: [{
            type: "text",
            text: `Recreation facilities matching "${query}" (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedSearchData, null, 2)}`
          }]
        };

      case "get_facility_details":
        const { facility_id } = args;
        const detailsResponse = await fetch(`${BASE_URL}/recsports`);
        const detailsData = await detailsResponse.json();
        
        if (!detailsData.data || !detailsData.data.facilities) {
          throw new Error("Invalid response format from recsports API");
        }

        const facility = detailsData.data.facilities.find((f: any) => 
          f.id === facility_id
        );

        if (!facility) {
          throw new Error(`Facility with ID "${facility_id}" not found`);
        }

        const facilityResult = {
          ...detailsData,
          data: {
            ...detailsData.data,
            facilities: [facility]
          }
        };

        const processedFacilityData = addLocalTimeToResponse(facilityResult);
        
        return {
          content: [{
            type: "text",
            text: `Details for Facility ${facility_id} (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedFacilityData, null, 2)}`
          }]
        };

      case "get_facility_hours":
        const hoursResponse = await fetch(`${BASE_URL}/recsports`);
        const hoursData = await hoursResponse.json();
        
        if (!hoursData.data || !hoursData.data.facilities) {
          throw new Error("Invalid response format from recsports API");
        }

        const hoursInfo = hoursData.data.facilities.map((facility: any) => ({
          id: facility.id,
          name: facility.name,
          abbreviation: facility.abbreviation,
          hours: facility.hours,
          isOpen: facility.hours?.isOpen || false
        }));

        const hoursResult = {
          ...hoursData,
          data: {
            ...hoursData.data,
            facilities: hoursInfo
          }
        };

        const processedHoursData = addLocalTimeToResponse(hoursResult);
        
        return {
          content: [{
            type: "text",
            text: `Recreation facility hours (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedHoursData, null, 2)}`
          }]
        };

      case "get_facility_events":
        const { facility_id: eventsFacilityId } = args || {};
        const eventsResponse = await fetch(`${BASE_URL}/recsports`);
        const eventsData = await eventsResponse.json();
        
        if (!eventsData.data || !eventsData.data.facilities) {
          throw new Error("Invalid response format from recsports API");
        }

        let facilitiesWithEvents = eventsData.data.facilities;

        if (eventsFacilityId) {
          facilitiesWithEvents = facilitiesWithEvents.filter((facility: any) => 
            facility.id === eventsFacilityId
          );
          
          if (facilitiesWithEvents.length === 0) {
            throw new Error(`Facility with ID "${eventsFacilityId}" not found`);
          }
        }

        const eventsInfo = facilitiesWithEvents.map((facility: any) => ({
          id: facility.id,
          name: facility.name,
          events: facility.events || []
        })).filter((facility: any) => facility.events.length > 0);

        const eventsResult = {
          ...eventsData,
          data: {
            ...eventsData.data,
            facilities: eventsInfo
          }
        };

        const processedEventsData = addLocalTimeToResponse(eventsResult);
        
        return {
          content: [{
            type: "text",
            text: `Recreation facility events${eventsFacilityId ? ` for facility ${eventsFacilityId}` : ''} (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedEventsData, null, 2)}`
          }]
        };

      default:
        throw new Error(`Unknown recsports tool: ${name}`);
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