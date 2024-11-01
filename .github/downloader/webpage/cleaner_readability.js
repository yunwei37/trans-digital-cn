const { Readability } = require('@mozilla/readability');
const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

async function cleanWebPage(filePath) {
    try {
        // Read the local HTML file
        const html = fs.readFileSync(filePath, 'utf-8');
        
        // Create DOM from HTML
        const dom = new JSDOM(html, {
            url: 'file://' + path.resolve(filePath) // Use file protocol for local files
        });
        
        // Create new readability object
        const reader = new Readability(dom.window.document);
        
        // Parse the content
        const article = reader.parse();
        
        if (!article) {
            throw new Error('Could not parse article content');
        }

        // Extract image URLs from the content
        const tempDiv = dom.window.document.createElement('div');
        tempDiv.innerHTML = article.content;
        const images = tempDiv.getElementsByTagName('img');
        const imageUrls = new Set();
        for (const img of images) {
            if (img.src) {
                imageUrls.add(img.src);
            }
        }

        // Create clean HTML with metadata
        const cleanHtml = `
<!DOCTYPE html>
<html lang="${article.lang || 'en'}" dir="${article.dir || 'ltr'}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${article.title}</title>
    <meta name="description" content="${article.excerpt || ''}">
    ${article.siteName ? `<meta name="site-name" content="${article.siteName}">` : ''}
    ${article.publishedTime ? `<meta name="published-time" content="${article.publishedTime}">` : ''}
    <meta name="image-count" content="${imageUrls.size}">
    <style>
        body {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
            line-height: 1.6;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        .metadata, .image-links {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 2em;
        }
        .image-links {
            border-top: 1px solid #eee;
            margin-top: 2em;
            padding-top: 1em;
        }
        .image-links ul {
            list-style: none;
            padding: 0;
        }
        .image-links li {
            margin-bottom: 0.5em;
            word-break: break-all;
        }
    </style>
</head>
<body>
    <h1>${article.title}</h1>
    <div class="metadata">
        ${article.byline ? `<p class="byline">By: ${article.byline}</p>` : ''}
        ${article.siteName ? `<p class="site-name">Source: ${article.siteName}</p>` : ''}
        ${article.publishedTime ? `<p class="published-time">Published: ${article.publishedTime}</p>` : ''}
        ${article.excerpt ? `<p class="excerpt">${article.excerpt}</p>` : ''}
        <p class="article-length">Article length: ${article.textContent.length} characters</p>
        <p class="image-count">Images found: ${imageUrls.size}</p>
    </div>
    ${article.content}
    ${imageUrls.size > 0 ? `
    <div class="image-links">
        <h2>Image URLs found in article</h2>
        <ul>
            ${[...imageUrls].map(url => `<li><a href="${url}">${url}</a></li>`).join('\n            ')}
        </ul>
    </div>` : ''}
</body>
</html>`;

        // Generate output filename
        const dirname = path.dirname(filePath);
        const basename = path.basename(filePath, '.html');
        const outputPath = path.join(dirname, `${basename}_clean.html`);

        // Save the file
        fs.writeFileSync(outputPath, cleanHtml);
        
        console.log(`Successfully cleaned webpage and saved to ${outputPath}`);
        console.log(`Title: ${article.title}`);
        console.log(`Site Name: ${article.siteName || 'N/A'}`);
        console.log(`Published Time: ${article.publishedTime || 'N/A'}`);
        console.log(`Language: ${article.lang || 'N/A'}`);
        console.log(`Direction: ${article.dir || 'ltr'}`);
        console.log(`Length: ${article.textContent.length} characters`);
        console.log(`Excerpt: ${article.excerpt || 'N/A'}`);
        console.log(`Images found: ${imageUrls.size}`);

    } catch (error) {
        console.error('Error processing webpage:', error);
    }
}

// Check if file path is provided as command line argument
if (process.argv.length < 3) {
    console.log('Usage: node webpage_cleaner.js <filepath>');
    process.exit(1);
}

const filePath = process.argv[2];
cleanWebPage(filePath);