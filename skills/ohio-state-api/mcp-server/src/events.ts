import { Tool } from "@modelcontextprotocol/sdk/types.js";
import { addLocalTimeToResponse, getCurrentEasternTime } from "./utils.js";

const BASE_URL = "https://content.osu.edu/v2";

export const eventsTools: Tool[] = [
  {
    name: "get_campus_events",
    description: "Get information about all campus events",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },
  {
    name: "search_campus_events",
    description: "Search for campus events by title or description",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search term for event title or description"
        }
      },
      required: ["query"]
    }
  },
  {
    name: "get_events_by_tag",
    description: "Find events by specific tags or categories",
    inputSchema: {
      type: "object",
      properties: {
        tag: {
          type: "string",
          description: "Tag or category to filter events by"
        }
      },
      required: ["tag"]
    }
  },
  {
    name: "get_events_by_location",
    description: "Find events at a specific location",
    inputSchema: {
      type: "object",
      properties: {
        location: {
          type: "string",
          description: "Location to search for events"
        }
      },
      required: ["location"]
    }
  },
  {
    name: "get_events_by_date_range",
    description: "Find events within a specific date range",
    inputSchema: {
      type: "object",
      properties: {
        start_date: {
          type: "string",
          description: "Start date in YYYY-MM-DD format"
        },
        end_date: {
          type: "string",
          description: "End date in YYYY-MM-DD format"
        }
      },
      required: ["start_date", "end_date"]
    }
  }
];

export async function handleEventsTool(name: string, args: any): Promise<any> {
  try {
    switch (name) {
      case "get_campus_events":
        const eventsResponse = await fetch(`${BASE_URL}/events`);
        const eventsData = await eventsResponse.json();
        const processedEventsData = addLocalTimeToResponse(eventsData);
        
        return {
          content: [{
            type: "text",
            text: `Campus Events (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedEventsData, null, 2)}`
          }]
        };

      case "search_campus_events":
        const { query } = args;
        const searchResponse = await fetch(`${BASE_URL}/events`);
        const searchData = await searchResponse.json();
        
        if (!searchData.data || !searchData.data.events) {
          throw new Error("Invalid response format from events API");
        }

        const filteredEvents = searchData.data.events.filter((event: any) => 
          event.title?.toLowerCase().includes(query.toLowerCase()) ||
          event.description?.toLowerCase().includes(query.toLowerCase()) ||
          event.content?.toLowerCase().includes(query.toLowerCase())
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
            text: `Events matching "${query}" (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedSearchData, null, 2)}`
          }]
        };

      case "get_events_by_tag":
        const { tag } = args;
        const tagResponse = await fetch(`${BASE_URL}/events`);
        const tagData = await tagResponse.json();
        
        if (!tagData.data || !tagData.data.events) {
          throw new Error("Invalid response format from events API");
        }

        const tagEvents = tagData.data.events.filter((event: any) => 
          event.tags?.some((eventTag: string) => 
            eventTag.toLowerCase().includes(tag.toLowerCase())
          )
        );

        const tagResult = {
          ...tagData,
          data: {
            ...tagData.data,
            events: tagEvents
          }
        };

        const processedTagData = addLocalTimeToResponse(tagResult);
        
        return {
          content: [{
            type: "text",
            text: `Events with tag "${tag}" (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedTagData, null, 2)}`
          }]
        };

      case "get_events_by_location":
        const { location } = args;
        const locationResponse = await fetch(`${BASE_URL}/events`);
        const locationData = await locationResponse.json();
        
        if (!locationData.data || !locationData.data.events) {
          throw new Error("Invalid response format from events API");
        }

        const locationEvents = locationData.data.events.filter((event: any) => 
          event.location?.toLowerCase().includes(location.toLowerCase())
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
            text: `Events at "${location}" (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedLocationData, null, 2)}`
          }]
        };

      case "get_events_by_date_range":
        const { start_date, end_date } = args;
        const dateResponse = await fetch(`${BASE_URL}/events`);
        const dateData = await dateResponse.json();
        
        if (!dateData.data || !dateData.data.events) {
          throw new Error("Invalid response format from events API");
        }

        const startDate = new Date(start_date);
        const endDate = new Date(end_date);

        const dateEvents = dateData.data.events.filter((event: any) => {
          if (!event.startDate) return false;
          
          const eventDate = new Date(event.startDate);
          return eventDate >= startDate && eventDate <= endDate;
        });

        const dateResult = {
          ...dateData,
          data: {
            ...dateData.data,
            events: dateEvents
          }
        };

        const processedDateData = addLocalTimeToResponse(dateResult);
        
        return {
          content: [{
            type: "text",
            text: `Events from ${start_date} to ${end_date} (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedDateData, null, 2)}`
          }]
        };

      default:
        throw new Error(`Unknown events tool: ${name}`);
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