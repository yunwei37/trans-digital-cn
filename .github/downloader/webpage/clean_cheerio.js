#!/usr/bin/env node

const cheerio = require('cheerio');
const fs = require('fs');
const path = require('path');

function cleanHTML(htmlContent) {
    const $ = cheerio.load(htmlContent);

    // Remove common unwanted elements
    const selectorsToRemove = [
        'nav',
        'header',
        'footer',
        'script',
        'style',
        'iframe',
        'ads',
        '.advertisement',
        '.ad-container',
        '#ad-section',
        '.social-share',
        '.comments-section',
        '.sidebar',
        '.related-articles',
        '.newsletter-signup',
        'ins',
        '[class*="ad-"]',
        '[id*="ad-"]',
        '[class*="advertisement"]',
        '[class*="popup"]',
        // paywall
        '[class*="paywall"]',
        // recommended
        '[class*="recommend"]',
        // Add more unwanted elements
        '[class*="cookie"]',
        '[class*="banner"]',
        '[id*="cookie"]',
        '[class*="notification"]',
        '[class*="subscribe"]',
        '.share-buttons',
    ];

    // Remove all matched elements
    selectorsToRemove.forEach(selector => {
        $(selector).remove();
    });

    // Remove empty paragraphs and divs
    $('p:empty, div:empty').remove();

    // Remove all HTML comments
    $('*').contents().each(function () {
        if (this.type === 'comment') {
            $(this).remove();
        }
    });

    // Remove all inline scripts and event handlers
    $('*').removeAttr('onclick')
        .removeAttr('onload')
        .removeAttr('onunload')
        .removeAttr('onabort')
        .removeAttr('onerror')
        .removeAttr('onresize')
        .removeAttr('onscroll')
        .removeAttr('onmouseover')
        .removeAttr('onmouseout');

    // Clean attributes from remaining elements
    $('*').each(function () {
        const element = $(this);
        const attrsToKeep = ['href', 'src', 'alt', 'title'];
        const attrs = element.attr();

        if (attrs) {
            Object.keys(attrs).forEach(attr => {
                if (!attrsToKeep.includes(attr)) {
                    element.removeAttr(attr);
                }
            });
        }
    });

    // Enhanced empty element cleaning
    $('*').each(function () {
        const $el = $(this);
        // Skip if element is an image or contains an image
        if ($el.is('img') || $el.find('img').length > 0) {
            return;
        }
        // Remove if element is empty or only contains whitespace/newlines
        if (!$el.text().trim() && !$el.find('video').length) {
            $el.remove();
        }
    });

    return $.html();
}

function processFile(filePath) {
    try {
        // Check if file exists
        if (!fs.existsSync(filePath)) {
            console.error(`Error: File "${filePath}" does not exist`);
            return;
        }

        // Check if file is HTML
        if (!filePath.toLowerCase().endsWith('.html')) {
            console.error(`Error: File "${filePath}" is not an HTML file`);
            return;
        }

        // Read the file
        const htmlContent = fs.readFileSync(filePath, 'utf8');

        // Clean the HTML
        const cleanedHTML = cleanHTML(htmlContent);

        // Generate output filename
        const dir = path.dirname(filePath);
        const filename = path.basename(filePath, '.html');
        const outputPath = path.join(dir, `${filename}_clean.html`);

        // Write the cleaned HTML to new file
        fs.writeFileSync(outputPath, cleanedHTML);
        console.log(`Successfully cleaned HTML. Saved to: ${outputPath}`);

    } catch (error) {
        console.error(`Error processing file: ${error.message}`);
    }
}

// Handle command line arguments
const args = process.argv.slice(2);

if (args.length === 0) {
    console.log(`
Usage: html-cleaner <file.html>
    
Example: html-cleaner page.html
    
This will create a cleaned version named 'page_clean.html'
    `);
} else {
    args.forEach(processFile);
}