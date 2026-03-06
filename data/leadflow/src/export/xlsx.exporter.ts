/**
 * XLSX export using ExcelJS
 */

import ExcelJS from 'exceljs';
import { mkdir } from 'fs/promises';
import { dirname, resolve } from 'path';
import { existsSync } from 'fs';
import { config } from '../config/index.js';
import { createLogger } from '../utils/logger.js';
import { formatPhoneDisplay, formatFullAddress } from '../utils/formatters.js';
import { LeadStatus, type Lead, type ExportLead, type LeadFilters } from '../types/index.js';
import { findLeads, updateLead } from '../storage/lead.repository.js';

const logger = createLogger('xlsx-exporter');

/**
 * Export leads to XLSX format
 */
export async function exportToXlsx(
  outputPath?: string,
  filters?: LeadFilters
): Promise<{ path: string; count: number }> {
  // Determine output path
  const finalPath = outputPath ?? getDefaultOutputPath();

  // Ensure directory exists
  const dir = dirname(finalPath);
  if (!existsSync(dir)) {
    await mkdir(dir, { recursive: true });
  }

  // Get leads to export
  const leads = findLeads(filters);

  if (leads.length === 0) {
    logger.info('No leads to export');
    return { path: finalPath, count: 0 };
  }

  logger.info(`Exporting ${leads.length} leads to ${finalPath}`);

  // Create workbook
  const workbook = new ExcelJS.Workbook();
  workbook.creator = 'OnCall Automation Lead Scraper';
  workbook.created = new Date();

  // Create worksheet
  const worksheet = workbook.addWorksheet('Leads', {
    properties: { tabColor: { argb: '00D4FF' } },
    views: [{ state: 'frozen', xSplit: 0, ySplit: 1 }],
  });

  // Define columns matching OnCall template
  worksheet.columns = [
    { header: 'Company Name', key: 'companyName', width: 30 },
    { header: 'Contact Name', key: 'contactName', width: 25 },
    { header: 'Email', key: 'email', width: 30 },
    { header: 'Phone', key: 'phone', width: 15 },
    { header: 'Website', key: 'website', width: 35 },
    { header: 'Address', key: 'address', width: 40 },
    { header: 'Trade', key: 'trade', width: 15 },
    { header: 'Source', key: 'source', width: 15 },
    { header: 'Notes', key: 'notes', width: 40 },
    { header: 'Status', key: 'status', width: 12 },
  ];

  // Style header row
  const headerRow = worksheet.getRow(1);
  headerRow.font = { bold: true, color: { argb: 'FFFFFFFF' } };
  headerRow.fill = {
    type: 'pattern',
    pattern: 'solid',
    fgColor: { argb: 'FF0A1628' }, // Dark blue matching OnCall theme
  };
  headerRow.alignment = { vertical: 'middle', horizontal: 'center' };
  headerRow.height = 25;

  // Add data rows
  for (const lead of leads) {
    const row = worksheet.addRow(leadToExportRow(lead));
    row.alignment = { vertical: 'middle', wrapText: true };

    // Color code by status
    const statusColor = getStatusColor(lead.status);
    if (statusColor) {
      row.getCell('status').fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: statusColor },
      };
    }
  }

  // Add alternating row colors
  worksheet.eachRow((row, rowNumber) => {
    if (rowNumber > 1 && rowNumber % 2 === 0) {
      row.eachCell((cell) => {
        if (!cell.fill || (cell.fill as ExcelJS.FillPattern).pattern !== 'solid') {
          cell.fill = {
            type: 'pattern',
            pattern: 'solid',
            fgColor: { argb: 'FFF5F5F5' },
          };
        }
      });
    }
  });

  // Add borders
  worksheet.eachRow((row) => {
    row.eachCell((cell) => {
      cell.border = {
        top: { style: 'thin', color: { argb: 'FFE0E0E0' } },
        left: { style: 'thin', color: { argb: 'FFE0E0E0' } },
        bottom: { style: 'thin', color: { argb: 'FFE0E0E0' } },
        right: { style: 'thin', color: { argb: 'FFE0E0E0' } },
      };
    });
  });

  // Add auto-filter
  worksheet.autoFilter = {
    from: { row: 1, column: 1 },
    to: { row: leads.length + 1, column: 10 },
  };

  // Save file
  await workbook.xlsx.writeFile(finalPath);

  // Update leads status to Exported
  for (const lead of leads) {
    if (lead.status !== LeadStatus.EXPORTED) {
      updateLead(lead.id, { status: LeadStatus.EXPORTED });
    }
  }

  logger.info(`Successfully exported ${leads.length} leads to ${finalPath}`);
  return { path: finalPath, count: leads.length };
}

/**
 * Convert Lead to export row format
 */
function leadToExportRow(lead: Lead): ExportLead {
  return {
    'Company Name': lead.companyName,
    'Contact Name': lead.contactName ?? '',
    Email: lead.email ?? '',
    Phone: formatPhoneDisplay(lead.phone),
    Website: lead.website ?? '',
    Address: formatFullAddress({
      address: lead.address,
      city: lead.city,
      state: lead.state,
      zipCode: lead.zipCode,
    }),
    Trade: lead.trade,
    Source: lead.source,
    Notes: lead.notes ?? '',
    Status: lead.status,
  };
}

/**
 * Get color for status cell
 */
function getStatusColor(status: string): string | undefined {
  const colors: Record<string, string> = {
    New: 'FFE3F2FD', // Light blue
    Enriched: 'FFF3E5F5', // Light purple
    Verified: 'FFE8F5E9', // Light green
    Exported: 'FFFFF3E0', // Light orange
    Invalid: 'FFFFEBEE', // Light red
    Duplicate: 'FFECEFF1', // Light gray
  };
  return colors[status];
}

/**
 * Get default output path with timestamp
 */
function getDefaultOutputPath(): string {
  const timestamp = new Date().toISOString().slice(0, 10);
  return resolve(config.EXPORT_PATH, `leads-${timestamp}.xlsx`);
}

/**
 * Export to CSV as fallback
 */
export async function exportToCsv(
  outputPath?: string,
  filters?: LeadFilters
): Promise<{ path: string; count: number }> {
  const finalPath = outputPath ?? getDefaultOutputPath().replace('.xlsx', '.csv');

  // Ensure directory exists
  const dir = dirname(finalPath);
  if (!existsSync(dir)) {
    await mkdir(dir, { recursive: true });
  }

  // Get leads
  const leads = findLeads(filters);

  if (leads.length === 0) {
    logger.info('No leads to export');
    return { path: finalPath, count: 0 };
  }

  // Build CSV
  const headers = [
    'Company Name',
    'Contact Name',
    'Email',
    'Phone',
    'Website',
    'Address',
    'Trade',
    'Source',
    'Notes',
    'Status',
  ];

  const rows = leads.map((lead) => {
    const exportLead = leadToExportRow(lead);
    return headers
      .map((header) => {
        const value = exportLead[header as keyof ExportLead];
        // Escape quotes and wrap in quotes if contains comma
        if (value.includes(',') || value.includes('"') || value.includes('\n')) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      })
      .join(',');
  });

  const csv = [headers.join(','), ...rows].join('\n');

  // Write file
  const { writeFile } = await import('fs/promises');
  await writeFile(finalPath, csv, 'utf-8');

  logger.info(`Successfully exported ${leads.length} leads to ${finalPath}`);
  return { path: finalPath, count: leads.length };
}

/**
 * Export to Instantly-compatible CSV format
 * Instantly requires: email (required), first_name, last_name, company_name, phone, website
 * Custom variables can be added as custom1, custom2, etc.
 */
export async function exportToInstantly(
  outputPath?: string,
  filters?: LeadFilters
): Promise<{ path: string; count: number; skipped: number }> {
  const finalPath = outputPath ?? getDefaultOutputPath().replace('.xlsx', '-instantly.csv');

  // Ensure directory exists
  const dir = dirname(finalPath);
  if (!existsSync(dir)) {
    await mkdir(dir, { recursive: true });
  }

  // Get leads - only those with email addresses
  const allLeads = findLeads(filters);
  const leads = allLeads.filter((lead) => lead.email && lead.email.trim().length > 0);
  const skipped = allLeads.length - leads.length;

  if (leads.length === 0) {
    logger.info('No leads with email addresses to export');
    return { path: finalPath, count: 0, skipped };
  }

  logger.info(`Exporting ${leads.length} leads to Instantly format (skipped ${skipped} without email)`);

  // Instantly CSV headers
  const instantlyHeaders = [
    'email',
    'first_name',
    'last_name',
    'company_name',
    'phone',
    'website',
    'city',
    'state',
    'trade',        // custom variable {{trade}}
    'source',       // custom variable {{source}}
    'rating',       // custom variable {{rating}}
  ];

  const instantlyRows = leads.map((lead) => {
    // Try to split contact name into first/last
    const nameParts = splitName(lead.contactName);

    return [
      lead.email ?? '',
      nameParts.firstName,
      nameParts.lastName,
      lead.companyName,
      formatPhoneDisplay(lead.phone),
      lead.website ?? '',
      lead.city ?? '',
      lead.state ?? '',
      lead.trade,
      lead.source,
      lead.rating?.toString() ?? '',
    ]
      .map((value) => {
        // Escape quotes and wrap if contains comma/quote/newline
        if (value.includes(',') || value.includes('"') || value.includes('\n')) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      })
      .join(',');
  });

  const instantlyCsv = [instantlyHeaders.join(','), ...instantlyRows].join('\n');

  // Write file
  const { writeFile } = await import('fs/promises');
  await writeFile(finalPath, instantlyCsv, 'utf-8');

  logger.info(`Successfully exported ${leads.length} leads to Instantly format at ${finalPath}`);
  return { path: finalPath, count: leads.length, skipped };
}

/**
 * Split a full name into first and last name
 */
function splitName(fullName?: string): { firstName: string; lastName: string } {
  if (!fullName || fullName.trim().length === 0) {
    return { firstName: '', lastName: '' };
  }

  const parts = fullName.trim().split(/\s+/);
  if (parts.length === 1) {
    return { firstName: parts[0] ?? '', lastName: '' };
  }

  // First word is first name, rest is last name
  const firstName = parts[0] ?? '';
  const lastName = parts.slice(1).join(' ');
  return { firstName, lastName };
}

// ============================================================================
// CRM-Native Export Formats
// ============================================================================

function csvEscape(value: string): string {
  if (value.includes(',') || value.includes('"') || value.includes('\n')) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

async function writeCsvFile(path: string, headers: string[], rows: string[][]): Promise<void> {
  const dir = dirname(path);
  if (!existsSync(dir)) {
    await mkdir(dir, { recursive: true });
  }
  const csv = [
    headers.join(','),
    ...rows.map(row => row.map(csvEscape).join(',')),
  ].join('\n');
  const { writeFile } = await import('fs/promises');
  await writeFile(path, csv, 'utf-8');
}

/**
 * Export to HubSpot-compatible CSV
 * Fields: firstname, lastname, email, company, phone, website, city, state, zip, jobtitle, lead_score
 */
export async function exportToHubspot(
  outputPath?: string,
  filters?: LeadFilters
): Promise<{ path: string; count: number; skipped: number }> {
  const finalPath = outputPath ?? getDefaultOutputPath().replace('.xlsx', '-hubspot.csv');
  const allLeads = findLeads(filters);
  const leads = allLeads.filter(l => l.email && l.email.trim().length > 0);
  const skipped = allLeads.length - leads.length;

  if (leads.length === 0) {
    return { path: finalPath, count: 0, skipped };
  }

  const headers = [
    'firstname', 'lastname', 'email', 'company', 'phone',
    'website', 'city', 'state', 'zip', 'jobtitle',
    'hs_lead_status', 'leadscore',
  ];

  const rows = leads.map(lead => {
    const name = splitName(lead.contactName);
    const position = (lead.metadata?.enrichmentPosition as string) ?? '';
    return [
      name.firstName, name.lastName, lead.email ?? '', lead.companyName,
      formatPhoneDisplay(lead.phone), lead.website ?? '',
      lead.city ?? '', lead.state ?? '', lead.zipCode ?? '',
      position, lead.status, lead.leadScore?.toString() ?? '',
    ];
  });

  await writeCsvFile(finalPath, headers, rows);
  logger.info(`Exported ${leads.length} leads to HubSpot format: ${finalPath}`);
  return { path: finalPath, count: leads.length, skipped };
}

/**
 * Export to Salesforce-compatible CSV
 * Fields: FirstName, LastName, Email, Company, Phone, Website, Street, City, State, PostalCode, LeadSource, Status, Rating
 */
export async function exportToSalesforce(
  outputPath?: string,
  filters?: LeadFilters
): Promise<{ path: string; count: number; skipped: number }> {
  const finalPath = outputPath ?? getDefaultOutputPath().replace('.xlsx', '-salesforce.csv');
  const allLeads = findLeads(filters);
  const leads = allLeads.filter(l => l.email && l.email.trim().length > 0);
  const skipped = allLeads.length - leads.length;

  if (leads.length === 0) {
    return { path: finalPath, count: 0, skipped };
  }

  const headers = [
    'FirstName', 'LastName', 'Email', 'Company', 'Phone',
    'Website', 'Street', 'City', 'State', 'PostalCode',
    'LeadSource', 'Status', 'Rating', 'Description',
  ];

  const rows = leads.map(lead => {
    const name = splitName(lead.contactName);
    return [
      name.firstName, name.lastName, lead.email ?? '', lead.companyName,
      formatPhoneDisplay(lead.phone), lead.website ?? '',
      lead.address ?? '', lead.city ?? '', lead.state ?? '', lead.zipCode ?? '',
      lead.source, mapToSalesforceStatus(lead.status),
      lead.rating?.toString() ?? '', lead.notes ?? '',
    ];
  });

  await writeCsvFile(finalPath, headers, rows);
  logger.info(`Exported ${leads.length} leads to Salesforce format: ${finalPath}`);
  return { path: finalPath, count: leads.length, skipped };
}

function mapToSalesforceStatus(status: string): string {
  const map: Record<string, string> = {
    New: 'Open - Not Contacted',
    Enriched: 'Open - Not Contacted',
    Verified: 'Working - Contacted',
    Exported: 'Working - Contacted',
    Invalid: 'Closed - Not Converted',
  };
  return map[status] ?? 'Open - Not Contacted';
}

/**
 * Export to Pipedrive-compatible CSV
 * Fields: Name, Email, Phone, Organization, Address, Note, Label
 */
export async function exportToPipedrive(
  outputPath?: string,
  filters?: LeadFilters
): Promise<{ path: string; count: number; skipped: number }> {
  const finalPath = outputPath ?? getDefaultOutputPath().replace('.xlsx', '-pipedrive.csv');
  const allLeads = findLeads(filters);
  const leads = allLeads.filter(l => l.email && l.email.trim().length > 0);
  const skipped = allLeads.length - leads.length;

  if (leads.length === 0) {
    return { path: finalPath, count: 0, skipped };
  }

  const headers = [
    'Name', 'Email', 'Phone', 'Organization', 'Address',
    'Note', 'Label', 'Website',
  ];

  const rows = leads.map(lead => {
    const fullAddress = formatFullAddress({
      address: lead.address, city: lead.city,
      state: lead.state, zipCode: lead.zipCode,
    });
    return [
      lead.contactName || lead.companyName,
      lead.email ?? '', formatPhoneDisplay(lead.phone),
      lead.companyName, fullAddress,
      lead.notes ?? '', lead.trade, lead.website ?? '',
    ];
  });

  await writeCsvFile(finalPath, headers, rows);
  logger.info(`Exported ${leads.length} leads to Pipedrive format: ${finalPath}`);
  return { path: finalPath, count: leads.length, skipped };
}

/**
 * Export to Airtable-compatible CSV
 * Matches OnCall aaa-website CRM field mapping:
 *   Name, Email, Phone, Source, Status, Lead Score, AI Summary, Message
 * Plus extra columns: Company, Website, Trade, City, State, Rating, Reviews
 */
export async function exportToAirtable(
  outputPath?: string,
  filters?: LeadFilters
): Promise<{ path: string; count: number; skipped: number }> {
  const finalPath = outputPath ?? getDefaultOutputPath().replace('.xlsx', '-airtable.csv');
  const leads = findLeads(filters);

  if (leads.length === 0) {
    return { path: finalPath, count: 0, skipped: 0 };
  }

  // Core fields match the aaa-website CRMIntegrationPanel field_mapping
  const headers = [
    'Name', 'Email', 'Phone', 'Company', 'Website',
    'Source', 'Status', 'Lead Score', 'Trade',
    'City', 'State', 'Address', 'Rating', 'Reviews',
    'AI Summary', 'Message',
  ];

  const rows = leads.map(lead => {
    const contactName = lead.contactName || '';
    const score = lead.leadScore ?? 0;

    // Build an AI summary from available data
    const summaryParts: string[] = [];
    summaryParts.push(`${lead.trade} business in ${lead.city || 'unknown city'}${lead.state ? ', ' + lead.state : ''}`);
    if (lead.rating) summaryParts.push(`${lead.rating} stars`);
    if (lead.reviewCount) summaryParts.push(`${lead.reviewCount} reviews`);
    if (lead.emailVerified) summaryParts.push('email verified');
    if (lead.phoneType === 'mobile') summaryParts.push('mobile phone');
    if (score >= 60) summaryParts.push('high-quality lead');
    else if (score >= 30) summaryParts.push('medium-quality lead');
    const aiSummary = summaryParts.join('. ') + '.';

    return [
      contactName, lead.email ?? '', formatPhoneDisplay(lead.phone),
      lead.companyName, lead.website ?? '',
      lead.source, lead.status, score.toString(), lead.trade,
      lead.city ?? '', lead.state ?? '',
      formatFullAddress({ address: lead.address, city: lead.city, state: lead.state, zipCode: lead.zipCode }),
      lead.rating?.toString() ?? '', lead.reviewCount?.toString() ?? '',
      aiSummary, lead.notes ?? '',
    ];
  });

  await writeCsvFile(finalPath, headers, rows);
  logger.info(`Exported ${leads.length} leads to Airtable format: ${finalPath}`);
  return { path: finalPath, count: leads.length, skipped: 0 };
}
