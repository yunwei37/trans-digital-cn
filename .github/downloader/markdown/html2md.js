const fs = require('fs');
const TurndownService = require('turndown');

// Initialize turndown
const turndownService = new TurndownService({
  headingStyle: 'atx',
  hr: '---',
  bulletListMarker: '-',
  codeBlockStyle: 'fenced'
});

// Get input file from command line
const inputFile = process.argv[2];
if (!inputFile) {
  console.error('Please provide an input HTML file');
  process.exit(1);
}

// Create output filename by replacing extension with .md
const outputFile = inputFile.replace(/\.[^/.]+$/, '.md');

try {
  // Read HTML file
  const html = fs.readFileSync(inputFile, 'utf8');
  
  // Convert to markdown
  const markdown = turndownService.turndown(html);
  
  // Write markdown file
  fs.writeFileSync(outputFile, markdown);
  
  console.log(`Successfully converted ${inputFile} to ${outputFile}`);
} catch (err) {
  console.error('Error:', err.message);
  process.exit(1);
}
