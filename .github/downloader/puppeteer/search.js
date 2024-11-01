const puppeteer = require('puppeteer');

// Add this array at the top of the file, after the require statement
const userAgents = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
];

async function googleSearch(searchQuery, maxPages = 0) {
    console.log(`searchQuery: ${searchQuery}, maxPages: ${maxPages === 0 ? 'unlimited' : maxPages}`);
  try {
    // Launch browser
    const browser = await puppeteer.launch({
      headless: "new",  // Use new headless mode
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    // Create new page
    const page = await browser.newPage();
    // 
    const randomUserAgent = userAgents[Math.floor(Math.random() * userAgents.length)];
    await page.setUserAgent(randomUserAgent);
    console.log(`Using User-Agent: ${randomUserAgent}`);
    // Set viewport
    await page.setViewport({ width: 2560, height: 1440 });

    // Navigate to Google
    await page.goto('https://www.google.com');

    // Type search query
    await page.type('textarea[name="q"]', searchQuery);
    
    // Press Enter
    await page.keyboard.press('Enter');

    // Wait for results to load
    await page.waitForSelector('div#search');

    let allResults = [];
    let hasNextPage = true;
    let pageNum = 1;

    while (hasNextPage && (maxPages === 0 || pageNum <= maxPages)) {
      console.log(`Scraping page ${pageNum}${maxPages === 0 ? '' : `/${maxPages}`}...`);
      
      // Extract search results
      const pageResults = await page.evaluate((startIndex) => {
        console.log(`startIndex: ${startIndex}`);
        const results = [];
        const items = document.querySelectorAll('div.g');
        
        items.forEach((item, idx) => {
          const title = item.querySelector('h3')?.textContent;
          const link = item.querySelector('a')?.href;
          const snippet = item.querySelector('div.VwiC3b')?.textContent;

          if (title && link) {
            results.push({ 
              index: startIndex + idx,
              title, 
              link, 
              snippet 
            });
          }
        });

        return results;
      }, allResults.length); // Pass the current total results length as startIndex
      console.log(`pageResults: ${pageResults.length}`);
      allResults = [...allResults, ...pageResults];

      // Save results after each page
      const fs = require('fs');
      const sanitizedQuery = searchQuery.replace(/[^a-z0-9]/gi, '_').toLowerCase();
      const filePath = `${sanitizedQuery}.json`;
      
      // Read existing data if file exists
      let existingData = [];
      if (fs.existsSync(filePath)) {
        try {
          existingData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
          console.log(`existingData: ${existingData.length}`);
        } catch (err) {
          console.warn('Error reading existing file:', err);
        }
      }
      
      // Combine existing data with new results
      const combinedResults = [...existingData, ...pageResults];
      
      // Write combined results back to file
      fs.writeFileSync(
        filePath,
        JSON.stringify(combinedResults, null, 2)
      );
      console.log(`combinedResults: ${combinedResults.length} saved`);

      const sleepTime = Math.floor(Math.random() * 8000) + 1000;
      console.log(`sleep ${sleepTime}ms`);
      await new Promise(resolve => setTimeout(resolve, sleepTime));

      // Check and click next page button if it exists and we haven't hit the limit
      const nextButton = await page.$('a#pnnext');
      if (nextButton && (maxPages === 0 || pageNum < maxPages)) {
        console.log(`click next button`);
        await nextButton.click();
        await page.waitForSelector('div#search');
        pageNum++;
      } else {
        hasNextPage = false;
      }
      // sleep random time
      const sleepTime_after_next = Math.floor(Math.random() * 4000) + 1000;
      console.log(`sleep ${sleepTime_after_next}ms`);
      await new Promise(resolve => setTimeout(resolve, sleepTime_after_next));
    }

    // Close browser
    await browser.close();
    console.log(`browser closed`);

    return allResults;

  } catch (error) {
    console.error('An error occurred:', error);
    throw error;
  }
}

// Example usage
async function main() {
  try {
    const searchQuery = process.env.QUERY;
    const maxPages = 0;

    if (!searchQuery) {
      throw new Error('SEARCH_QUERY environment variable is required');
    }

    console.log(`Starting search for: "${searchQuery}" with maxPages: ${maxPages || 'unlimited'}`);
    const results = await googleSearch(searchQuery, maxPages);
    console.log(`Total results saved: ${results.length}`);
  } catch (error) {
    console.error('Error in main:', error);
    process.exit(1);
  }
}

main();
