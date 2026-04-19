const fs = require('fs');
const path = require('path');

const url = process.env.KETEMUIN_SUPABASE_URL || process.env.SUPABASE_URL || '';
const anonKey = process.env.KETEMUIN_SUPABASE_ANON_KEY || process.env.SUPABASE_ANON_KEY || '';

if (!url || !anonKey) {
  console.error('Missing Supabase env vars: KETEMUIN_SUPABASE_URL and KETEMUIN_SUPABASE_ANON_KEY');
  process.exit(1);
}

const outputPath = path.join(__dirname, '..', 'supabase-config.js');
const content = [
  `window.KETEMUIN_SUPABASE_URL = ${JSON.stringify(url)};`,
  `window.KETEMUIN_SUPABASE_ANON_KEY = ${JSON.stringify(anonKey)};`,
  ''
].join('\n');

fs.writeFileSync(outputPath, content, 'utf8');
console.log(`Generated ${outputPath}`);
