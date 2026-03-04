import { Tool } from "@modelcontextprotocol/sdk/types.js";
import { addLocalTimeToResponse, getCurrentEasternTime } from "./utils.js";

const BASE_URL = "https://content.osu.edu/v3/athletics";

export const athleticsTools: Tool[] = [
  {
    name: "get_athletics_all",
    description: "Get information about all OSU athletics programs and schedules",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },
  {
    name: "search_sports",
    description: "Search for specific sports or teams",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search term for sport name or team"
        }
      },
      required: ["query"]
    }
  },
  {
    name: "get_sport_by_gender",
    description: "Find sports programs by gender",
    inputSchema: {
      type: "object",
      properties: {
        gender: {
          type: "string",
          description: "Gender category: men, women, or mixed",
          enum: ["men", "women", "mixed"]
        }
      },
      required: ["gender"]
    }
  },
  {
    name: "get_upcoming_games",
    description: "Get upcoming games and events across all sports",
    inputSchema: {
      type: "object",
      properties: {
        sport: {
          type: "string",
          description: "Optional: filter by specific sport name"
        }
      },
      required: []
    }
  }
];

export async function handleAthleticsTool(name: string, args: any): Promise<any> {
  try {
    switch (name) {
      case "get_athletics_all":
        const athleticsResponse = await fetch(`${BASE_URL}/all`);
        const athleticsData = await athleticsResponse.json();
        const processedAthleticsData = addLocalTimeToResponse(athleticsData);
        
        return {
          content: [{
            type: "text",
            text: `OSU Athletics (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedAthleticsData, null, 2)}`
          }]
        };

      case "search_sports":
        const { query } = args;
        const searchResponse = await fetch(`${BASE_URL}/all`);
        const searchData = await searchResponse.json();
        
        if (!searchData.data) {
          throw new Error("Invalid response format from athletics API");
        }

        const filteredSports = Object.entries(searchData.data).reduce((acc: any, [key, sport]: [string, any]) => {
          if (sport.title?.toLowerCase().includes(query.toLowerCase()) ||
              sport.abbreviation?.toLowerCase().includes(query.toLowerCase())) {
            acc[key] = sport;
          }
          return acc;
        }, {});

        const searchResult = {
          ...searchData,
          data: filteredSports
        };

        const processedSearchData = addLocalTimeToResponse(searchResult);
        
        return {
          content: [{
            type: "text",
            text: `Sports matching "${query}" (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedSearchData, null, 2)}`
          }]
        };

      case "get_sport_by_gender":
        const { gender } = args;
        const genderResponse = await fetch(`${BASE_URL}/all`);
        const genderData = await genderResponse.json();
        
        if (!genderData.data) {
          throw new Error("Invalid response format from athletics API");
        }

        const genderSports = Object.entries(genderData.data).reduce((acc: any, [key, sport]: [string, any]) => {
          if (sport.gender?.toLowerCase() === gender.toLowerCase()) {
            acc[key] = sport;
          }
          return acc;
        }, {});

        const genderResult = {
          ...genderData,
          data: genderSports
        };

        const processedGenderData = addLocalTimeToResponse(genderResult);
        
        return {
          content: [{
            type: "text",
            text: `${gender} sports (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedGenderData, null, 2)}`
          }]
        };

      case "get_upcoming_games":
        const { sport } = args;
        const gamesResponse = await fetch(`${BASE_URL}/all`);
        const gamesData = await gamesResponse.json();
        
        if (!gamesData.data) {
          throw new Error("Invalid response format from athletics API");
        }

        const upcomingGames: any[] = [];
        
        Object.entries(gamesData.data).forEach(([key, sportData]: [string, any]) => {
          if (sport && !sportData.title?.toLowerCase().includes(sport.toLowerCase())) {
            return;
          }
          
          if (sportData.upcomingEvents && Array.isArray(sportData.upcomingEvents)) {
            sportData.upcomingEvents.forEach((event: any) => {
              upcomingGames.push({
                sport: sportData.title,
                gender: sportData.gender,
                ...event
              });
            });
          }
        });

        const gamesResult = {
          ...gamesData,
          data: {
            upcomingGames: upcomingGames.slice(0, 50) // Limit to first 50 games
          }
        };

        const processedGamesData = addLocalTimeToResponse(gamesResult);
        
        return {
          content: [{
            type: "text",
            text: `Upcoming games${sport ? ` for ${sport}` : ''} (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedGamesData, null, 2)}`
          }]
        };

      default:
        throw new Error(`Unknown athletics tool: ${name}`);
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