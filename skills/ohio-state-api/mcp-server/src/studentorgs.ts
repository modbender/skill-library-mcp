import { Tool } from "@modelcontextprotocol/sdk/types.js";
import { addLocalTimeToResponse, getCurrentEasternTime } from "./utils.js";

const BASE_URL = "https://content.osu.edu/v2/student-org";

export const studentorgTools: Tool[] = [
  {
    name: "get_student_organizations",
    description: "Get information about all student organizations",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },
  {
    name: "search_student_orgs",
    description: "Search for student organizations by name or keywords",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search term for organization name or keywords"
        }
      },
      required: ["query"]
    }
  },
  {
    name: "get_orgs_by_type",
    description: "Find student organizations by type or category",
    inputSchema: {
      type: "object",
      properties: {
        org_type: {
          type: "string",
          description: "Organization type or category to search for"
        }
      },
      required: ["org_type"]
    }
  },
  {
    name: "get_orgs_by_career_level",
    description: "Find organizations for specific career levels (undergraduate, graduate, professional)",
    inputSchema: {
      type: "object",
      properties: {
        career_level: {
          type: "string",
          description: "Career level: undergraduate, graduate, or professional",
          enum: ["undergraduate", "graduate", "professional"]
        }
      },
      required: ["career_level"]
    }
  }
];

export async function handleStudentorgTool(name: string, args: any): Promise<any> {
  try {
    switch (name) {
      case "get_student_organizations":
        const orgsResponse = await fetch(`${BASE_URL}/all`);
        const orgsData = await orgsResponse.json();
        const processedOrgsData = addLocalTimeToResponse(orgsData);
        
        return {
          content: [{
            type: "text",
            text: `Student Organizations (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedOrgsData, null, 2)}`
          }]
        };

      case "search_student_orgs":
        const { query } = args;
        const searchResponse = await fetch(`${BASE_URL}/all`);
        const searchData = await searchResponse.json();
        
        if (!searchData.data || !searchData.data.organizations) {
          throw new Error("Invalid response format from student organizations API");
        }

        const filteredOrgs = searchData.data.organizations.filter((org: any) => 
          org.name?.toLowerCase().includes(query.toLowerCase()) ||
          org.purposeStatement?.toLowerCase().includes(query.toLowerCase()) ||
          org.keywords?.some((keyword: string) => 
            keyword.toLowerCase().includes(query.toLowerCase())
          )
        );

        const searchResult = {
          ...searchData,
          data: {
            ...searchData.data,
            organizations: filteredOrgs
          }
        };

        const processedSearchData = addLocalTimeToResponse(searchResult);
        
        return {
          content: [{
            type: "text",
            text: `Student organizations matching "${query}" (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedSearchData, null, 2)}`
          }]
        };

      case "get_orgs_by_type":
        const { org_type } = args;
        const typeResponse = await fetch(`${BASE_URL}/all`);
        const typeData = await typeResponse.json();
        
        if (!typeData.data || !typeData.data.organizations) {
          throw new Error("Invalid response format from student organizations API");
        }

        const typeOrgs = typeData.data.organizations.filter((org: any) => 
          org.makeUp?.toLowerCase().includes(org_type.toLowerCase()) ||
          org.secondaryMakeUp?.toLowerCase().includes(org_type.toLowerCase())
        );

        const typeResult = {
          ...typeData,
          data: {
            ...typeData.data,
            organizations: typeOrgs
          }
        };

        const processedTypeData = addLocalTimeToResponse(typeResult);
        
        return {
          content: [{
            type: "text",
            text: `Student organizations of type "${org_type}" (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedTypeData, null, 2)}`
          }]
        };

      case "get_orgs_by_career_level":
        const { career_level } = args;
        const careerResponse = await fetch(`${BASE_URL}/all`);
        const careerData = await careerResponse.json();
        
        if (!careerData.data || !careerData.data.organizations) {
          throw new Error("Invalid response format from student organizations API");
        }

        const careerOrgs = careerData.data.organizations.filter((org: any) => 
          org.career?.toLowerCase().includes(career_level.toLowerCase())
        );

        const careerResult = {
          ...careerData,
          data: {
            ...careerData.data,
            organizations: careerOrgs
          }
        };

        const processedCareerData = addLocalTimeToResponse(careerResult);
        
        return {
          content: [{
            type: "text",
            text: `Student organizations for ${career_level} students (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedCareerData, null, 2)}`
          }]
        };

      default:
        throw new Error(`Unknown student organization tool: ${name}`);
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