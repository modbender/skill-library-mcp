import { Tool } from "@modelcontextprotocol/sdk/types.js";
import { addLocalTimeToResponse, getCurrentEasternTime } from "./utils.js";

const BASE_URL = "https://content.osu.edu";

export const directoryTools: Tool[] = [
  {
    name: "get_university_directory",
    description: "Get the university directory information",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },
  {
    name: "search_people",
    description: "Search for people in the OSU directory by first and/or last name",
    inputSchema: {
      type: "object",
      properties: {
        firstname: {
          type: "string",
          description: "First name to search for"
        },
        lastname: {
          type: "string",
          description: "Last name to search for"
        }
      },
      required: []
    }
  }
];

export async function handleDirectoryTool(name: string, args: any): Promise<any> {
  try {
    switch (name) {
      case "get_university_directory":
        const directoryResponse = await fetch(`${BASE_URL}/v3/managed-json/universityDirectory`);
        const directoryData = await directoryResponse.json();
        const processedDirectoryData = addLocalTimeToResponse(directoryData);
        
        return {
          content: [{
            type: "text",
            text: `University Directory (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedDirectoryData, null, 2)}`
          }]
        };

      case "search_people":
        const { firstname, lastname } = args;
        
        if (!firstname && !lastname) {
          throw new Error("At least one of firstname or lastname must be provided");
        }

        const searchParams = new URLSearchParams();
        if (firstname) searchParams.append('firstname', firstname);
        if (lastname) searchParams.append('lastname', lastname);
        
        const searchResponse = await fetch(`${BASE_URL}/v2/people/search?${searchParams.toString()}`);
        const searchData = await searchResponse.json();
        const processedSearchData = addLocalTimeToResponse(searchData);
        
        return {
          content: [{
            type: "text",
            text: `People search results${firstname ? ` (firstname: ${firstname})` : ''}${lastname ? ` (lastname: ${lastname})` : ''} (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedSearchData, null, 2)}`
          }]
        };

      default:
        throw new Error(`Unknown directory tool: ${name}`);
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