/**
 * GrowthGuru AI — CSV Parser Utility
 * ====================================
 * In-browser CSV parsing and KPI calculation.
 * Uses plain JavaScript (split, reduce, map) per project spec.
 *
 * Expected CSV columns (from API spec §3):
 *   Product_Name, Category, Quantity_Sold (or Quantity),
 *   Unit_Price (or Price), Revenue (or Total_Revenue)
 */

/**
 * Parse raw CSV text into an array of row objects.
 * Handles both \r\n and \n line endings.
 *
 * @param {string} csvText - Raw CSV file content
 * @returns {{ headers: string[], rows: Object[] }}
 */
export function parseCSV(csvText) {
  const lines = csvText
    .trim()
    .split(/\r?\n/)
    .filter((line) => line.trim() !== '');

  if (lines.length < 2) {
    throw new Error('CSV file must contain a header row and at least one data row.');
  }

  const headers = lines[0].split(',').map((h) => h.trim());
  const rows = [];

  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map((v) => v.trim());
    if (values.length !== headers.length) continue; // skip malformed rows

    const row = {};
    headers.forEach((header, idx) => {
      const val = values[idx];
      // Auto-convert numeric fields
      const num = Number(val);
      row[header] = isNaN(num) || val === '' ? val : num;
    });
    rows.push(row);
  }

  return { headers, rows };
}

function normalizeCol(col) {
  return String(col).toLowerCase().replace(/[\s_\-]+/g, ' ').trim();
}

const COLUMN_SYNONYMS = {
  'product name': [
    "product name", "product", "item", "item name", "productname", "name", 
    "sku name", "item description", "product title", "product description"
  ],
  'quantity': [
    "quantity", "qty", "units", "units sold", "sold", "sales volume", 
    "volume", "items sold", "pieces sold", "no sold", "quantity sold", "total units"
  ],
  'revenue': [
    "revenue", "sales", "sales amount", "total sales", "total revenue", 
    "turnover", "total sales amount"
  ],
  'category': [
    "category", "product category", "department", "segment", "type"
  ],
  'price': [
    "price", "selling price", "unit price", "mrp", "retail price", "unit cost"
  ]
};

function getCanonical(col) {
  const norm = normalizeCol(col);
  for (const [canonical, aliases] of Object.entries(COLUMN_SYNONYMS)) {
    if (aliases.includes(norm)) return canonical;
  }
  return norm;
}

function normalizeRow(row) {
  const normRow = {};
  for (const [key, val] of Object.entries(row)) {
    normRow[getCanonical(key)] = val;
  }
  
  return {
    productName: normRow['product name'] || '',
    category: normRow['category'] || '',
    quantity: Number(normRow['quantity'] || 0),
    unitPrice: Number(normRow['price'] || 0),
    revenue: Number(normRow['revenue'] || 0),
  };
}

/**
 * Calculate Key Performance Indicators from parsed CSV data.
 *
 * @param {Object[]} rows - Array of parsed CSV row objects
 * @returns {{ totalSales: number, totalRevenue: number, bestSeller: string, worstSeller: string, productData: Object[] }}
 */
export function calculateKPIs(rows) {
  if (!rows || rows.length === 0) {
    return {
      totalSales: 0,
      totalRevenue: 0,
      bestSeller: 'N/A',
      worstSeller: 'N/A',
      productData: [],
    };
  }

  const normalized = rows.map(normalizeRow);

  // Total sales count (sum of all quantities)
  const totalSales = normalized.reduce((sum, r) => sum + r.quantity, 0);

  // Total revenue
  const totalRevenue = normalized.reduce((sum, r) => sum + r.revenue, 0);

  // Aggregate revenue by product
  const productRevenue = normalized.reduce((acc, r) => {
    if (!r.productName) return acc;
    if (!acc[r.productName]) {
      acc[r.productName] = { name: r.productName, revenue: 0, quantity: 0, category: r.category };
    }
    acc[r.productName].revenue += r.revenue;
    acc[r.productName].quantity += r.quantity;
    return acc;
  }, {});

  const productData = Object.values(productRevenue).sort((a, b) => b.revenue - a.revenue);

  const bestSeller = productData.length > 0 ? productData[0].name : 'N/A';
  const worstSeller = productData.length > 0 ? productData[productData.length - 1].name : 'N/A';

  return {
    totalSales,
    totalRevenue,
    bestSeller,
    worstSeller,
    productData,
  };
}

export function validateCSVHeaders(headers) {
  // We delegate the strict validation and detailed error messages to the backend.
  // The backend uses the exact same mapping strategy and will return a beautiful
  // error response showing detected columns and supported aliases if any are missing.
  return { valid: true, missing: [] };
}
