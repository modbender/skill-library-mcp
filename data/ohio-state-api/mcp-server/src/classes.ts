import { Tool } from "@modelcontextprotocol/sdk/types.js";

const BASE_URL = "https://content.osu.edu/v2/classes";

export const classTools: Tool[] = [
  {
    name: "search_classes",
    description: "Search for OSU classes by keyword, subject, instructor, etc.",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search query - can be course title, subject, instructor name, building, etc."
        },
        term: {
          type: "string",
          description: "Term code (e.g. 1162 for Spring 2016, 1164 for Summer 2016, 1168 for Autumn 2016)",
          pattern: "^\\d{4}$"
        },
        campus: {
          type: "string", 
          description: "Campus code (e.g. COL for Columbus, LMA for Lima)",
          enum: ["COL", "LMA", "MAN", "MRN", "NWK"]
        },
        subject: {
          type: "string",
          description: "Subject code (e.g. CSE, MATH, ENGR)"
        },
        academic_career: {
          type: "string",
          description: "Academic career level",
          enum: ["UGRD", "GRAD", "DENT", "LAW", "MED", "VET"]
        },
        academic_program: {
          type: "string",
          description: "Academic program code (e.g. ENG, ASC, AGR)"
        },
        component: {
          type: "string",
          description: "Class component type",
          enum: ["LEC", "LAB", "REC", "SEM", "IND", "CLN", "FLD"]
        },
        catalog_number: {
          type: "string",
          description: "Catalog number range (e.g. 1xxx, 2xxx, 3xxx, 4xxx, 5xxx+)"
        },
        instruction_mode: {
          type: "string",
          description: "Instruction mode",
          enum: ["P", "DL", "BL"]
        },
        page: {
          type: "number",
          description: "Page number for pagination (default: 1)",
          minimum: 1
        }
      },
      required: ["query"]
    }
  }
];

export async function handleClassTool(name: string, args: any): Promise<any> {
  try {
    switch (name) {
      case "search_classes":
        const {
          query,
          term,
          campus,
          subject,
          academic_career,
          academic_program, 
          component,
          catalog_number,
          instruction_mode,
          page = 1
        } = args;

        const params = new URLSearchParams();
        params.append("q", query);
        params.append("p", page.toString());
        
        if (term) params.append("term", term);
        if (campus) params.append("campus", campus);
        if (subject) params.append("subject", subject);
        if (academic_career) params.append("academic-career", academic_career);
        if (academic_program) params.append("academic-program", academic_program);
        if (component) params.append("component", component);
        if (catalog_number) params.append("catalog-number", catalog_number);
        if (instruction_mode) params.append("instruction-mode", instruction_mode);

        const response = await fetch(`${BASE_URL}/search?${params}`);
        const data = await response.json();
        
        return {
          content: [{
            type: "text",
            text: `Class search results for "${query}":\n${JSON.stringify(data, null, 2)}`
          }]
        };

      default:
        throw new Error(`Unknown class tool: ${name}`);
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