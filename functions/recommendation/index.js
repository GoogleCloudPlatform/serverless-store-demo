'use strict';

const {google} = require('googleapis');

// Cache the prepared recommendation lookup table in memory.
let lookup;

// Impose a lookup TTL.
let lookup_expire;

exports.recommendation = async (req, res) => {
  // Uncaught exceptions may lead to an "instance crash", presenting the next
  // request with a cold start delay.
  // https://cloud.google.com/functions/docs/monitoring/error-reporting
  try {
    if (!lookup || Date.now() > lookup_expire) {
      // Load the google sheet data.
      console.log(`Loading Google Sheet '${process.env.GOOGLE_SHEET_ID}'...`);
      const tab = process.env.GOOGLE_SHEET_TAB_ID || 'Recommend';
      const sheet = await initSheetData(
        process.env.GOOGLE_SHEET_ID, `${tab}!A2:B`);

      // Rearrange data into a lookup table.
      // @todo lookup = buildLookupTableFromSheet(sheet)
      lookup = buildLookupTableFromRows(sheet);
      // Add an expiration timestamp for this lookup cache.
      // @todo move expiration update into build function.
      const cache_ttl = process.env.CACHE_TTL_SECONDS || 3;
      lookup_expire = Date.now() + 1000 * cache_ttl;
      console.log(`Data ready with ${cache_ttl} second TTL`);
    }

    const recommendation = recommendFromIds(req.query.productId);
    // Cache for a few minutes to avoid unnecessary function invocations.
    res.set('Cache-Control', 'public, max-age=3000');
    res.status(200).send(recommendation);
  } catch (err) {
    console.error(`error: building recommendation: ${err}`);
    res.status(500).send({'error': 'Internal Server Error'});
  }
};

// Load data from the Google Sheet.
const initSheetData = async (spreadsheetId, range) => {
  const auth = await google.auth.getClient({
    scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
  });
  const client = google.sheets({version: 'v4', auth});
  const response = await client.spreadsheets.values.get({spreadsheetId, range});
  return response.data.values
};

// Build the lookup dictionary data structure. e.g., { col0: col1 }
const buildLookupTableFromRows = (rows) => {
  if (!rows) {
    throw new Error('empty sheet data')
  }

  const table = {}; 
  rows.forEach((row, index) => {
    // Marketing will definitely use valid product IDs ALL THE TIME.
    if (row[0] && row[1]) {
      table[row[0]] = row[1];
    } else {
      console.log(`warning: skipping incomplete mapping on row (${index+1})`);
    }
  });

  // Make sure we are able to load a recommendation.
  if (Object.keys(table).length === 0) {
    throw new Error(`no valid data found`);
  }

  return table;
};

// Create a list of recommendations to complement the provided products.
const recommendFromIds = (ids) => {
  // For each product ID from the request,
  // 1. Check for a specific recommendation
  // 2. Fall back to a default recommendation
  // 3. Empty response if neither are available
  const recommendWithDups = ids.map((id) => lookup[id] || lookup['*'] || '').filter(i => i);
  // Use the ES6 Set data structure to create a unique set of recommendations.
  return [...new Set(recommendWithDups)];
};
