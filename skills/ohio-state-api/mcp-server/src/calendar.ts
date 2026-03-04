import { Tool } from "@modelcontextprotocol/sdk/types.js";
import { addLocalTimeToResponse, getCurrentEasternTime } from "./utils.js";

const BASE_URL = "https://content.osu.edu/v2/calendar";

export const calendarTools: Tool[] = [
  {
    name: "get_academic_calendar",
    description: "Get the academic calendar with important dates",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },
  {
    name: "get_university_holidays",
    description: "Get university holidays",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },
  {
    name: "search_calendar_events",
    description: "Search for specific events in the academic calendar",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search term for calendar events"
        }
      },
      required: ["query"]
    }
  },
  {
    name: "get_holidays_by_year",
    description: "Get holidays for a specific year",
    inputSchema: {
      type: "object",
      properties: {
        year: {
          type: "number",
          description: "Year to get holidays for"
        }
      },
      required: ["year"]
    }
  }
];

export async function handleCalendarTool(name: string, args: any): Promise<any> {
  try {
    switch (name) {
      case "get_academic_calendar":
        const calendarResponse = await fetch(`${BASE_URL}/academic`);
        const calendarData = await calendarResponse.json();
        const processedCalendarData = addLocalTimeToResponse(calendarData);
        
        return {
          content: [{
            type: "text",
            text: `Academic Calendar (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedCalendarData, null, 2)}`
          }]
        };

      case "get_university_holidays":
        const holidaysResponse = await fetch(`${BASE_URL}/holidays`);
        const holidaysData = await holidaysResponse.json();
        const processedHolidaysData = addLocalTimeToResponse(holidaysData);
        
        return {
          content: [{
            type: "text",
            text: `University Holidays (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedHolidaysData, null, 2)}`
          }]
        };

      case "search_calendar_events":
        const { query } = args;
        const searchResponse = await fetch(`${BASE_URL}/academic`);
        const searchData = await searchResponse.json();
        
        if (!searchData.data) {
          throw new Error("Invalid response format from academic calendar API");
        }

        const filteredEvents = searchData.data.filter((event: any) => 
          event.title?.toLowerCase().includes(query.toLowerCase()) ||
          event.text?.toLowerCase().includes(query.toLowerCase()) ||
          event.description?.toLowerCase().includes(query.toLowerCase())
        );

        const searchResult = {
          ...searchData,
          data: filteredEvents
        };

        const processedSearchData = addLocalTimeToResponse(searchResult);
        
        return {
          content: [{
            type: "text",
            text: `Calendar events matching "${query}" (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedSearchData, null, 2)}`
          }]
        };

      case "get_holidays_by_year":
        const { year } = args;
        const yearHolidaysResponse = await fetch(`${BASE_URL}/holidays`);
        const yearHolidaysData = await yearHolidaysResponse.json();
        
        if (!yearHolidaysData.data || !yearHolidaysData.data.holidays) {
          throw new Error("Invalid response format from holidays API");
        }

        const yearHolidays = yearHolidaysData.data.holidays.filter((holiday: any) => {
          const holidayYear = new Date(holiday.date).getFullYear();
          return holidayYear === year;
        });

        const yearResult = {
          ...yearHolidaysData,
          data: {
            ...yearHolidaysData.data,
            holidays: yearHolidays
          }
        };

        const processedYearData = addLocalTimeToResponse(yearResult);
        
        return {
          content: [{
            type: "text",
            text: `University holidays for ${year} (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedYearData, null, 2)}`
          }]
        };

      default:
        throw new Error(`Unknown calendar tool: ${name}`);
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