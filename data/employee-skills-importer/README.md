# Employee Skills Importer - User Guide

## What is This?

This is a custom Claude skill that automates importing employee skills from CSV files into your Supabase database. It generates SQL scripts for you to execute.

## How to Use This Skill

This skill works **inside Claude.ai** - you don't need to install anything on your computer.

### Steps:

1. **Upload your CSV file** to Claude (drag & drop or use the upload button)
2. **Ask Claude to process it**, for example:
   - "Use the employee-skills-importer skill to process this CSV"
   - "Generate SQL scripts from this employee skills file"
   - "Parse this CSV and create SQL inserts for my SkillsSystem database"

3. **Claude will generate 3 SQL files**:
   - `1_insert_categories.sql` - Inserts missing skill categories
   - `2_insert_skills.sql` - Inserts missing skills with category mappings
   - `3_insert_employee_skills.sql` - Links employees to their skills

4. **Execute the scripts in order** (1 → 2 → 3) in your Supabase SQL editor

## CSV Format Required

Your CSV should have:
- **Row 1**: Metadata (ignored)
- **Row 2**: Skill category names (e.g., ".NET", "Front-end", "Java")
- **Row 3+**: Skill names (may span multiple rows)
- **Data rows**: First Name, Last Name, followed by years of experience for each skill

Example:
```
,,,,,,.NET,,,Front-end,,,Java
First Name,Last Name,Unit,C#,ASP.net,JavaScript,HTML,Java,Spring
John,Doe,Unit 1,5,4,6,5,3,2
Jane,Smith,Unit 2,0,0,7,8,0,0
```

## What the Skill Does

1. **Parses your CSV** - Extracts categories, skills, and employee data
2. **Checks your database** - Connects to your SkillsSystem Supabase project
3. **Generates idempotent SQL** - Scripts can be run multiple times safely
4. **Reports issues** - Lists employees not found, unmapped skills, etc.

## Database Configuration

The skill is pre-configured for:
- **Project Name**: SkillsSystem
- **Project ID**: ypibfhbklinkvybgotef
- **Region**: eu-central-1

It works with these tables:
- `skill_categories` (id, name)
- `skills` (id, name, category_id)
- `employees` (id, first_name, last_name)
- `employee_skills` (id, employee_id, skill_id, years_of_experience)

## Features

✅ **Idempotent** - Safe to run multiple times  
✅ **Smart lookups** - Uses subqueries instead of hardcoded IDs  
✅ **Data validation** - Skips zero/empty values, handles decimals  
✅ **Error reporting** - Lists employees not found in database  
✅ **Multi-line support** - Handles complex CSV formats

## Troubleshooting

**Q: Claude isn't using the skill**  
A: Make sure to explicitly mention "employee-skills-importer skill" or describe what you want to do (generate SQL from CSV)

**Q: Can I modify the skill?**  
A: Yes! You can edit the SKILL.md file and ask Claude to update it, or create a new version

**Q: What if my CSV format is different?**  
A: Describe your CSV structure to Claude and ask to modify the skill to match your format

## Support

Need help? Just ask Claude:
- "How do I use the employee-skills-importer skill?"
- "My CSV has a different format, can you update the skill?"
- "Can you explain what each SQL script does?"
