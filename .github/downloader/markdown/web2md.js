const puppeteer = require('puppeteer');
const TurndownService = require('turndown');
const fs = require('fs').promises;

async function html2markdown(url) {
    console.log('Starting conversion process for:', url);
    // Initialize turndown with custom options
    const turndownService = new TurndownService({
        headingStyle: 'atx',
        codeBlockStyle: 'fenced',
        bulletListMarker: '*',
        strongDelimiter: '**'
    });

    // Define elements to remove
    const removeSelectors = [
        'script',
        'style',
        'iframe',
        'noscript',
        '.advertisement',
        '#footer',
        '#header',
        '.nav',
        '.share-btn',
        '.comment-section',
        '.related-articles'
    ];

    // Custom rules to handle Chinese content better and preserve structure
    turndownService.addRule('preserveFigures', {
        filter: 'figure',
        replacement: (content, node) => {
            const img = node.querySelector('img');
            const caption = node.querySelector('figcaption');
            return `<figure>\n${img ? img.outerHTML : ''}\n${caption ? caption.outerHTML : ''}\n</figure>\n\n`;
        }
    });

    turndownService.addRule('preserveReferences', {
        filter: ['cite', 'blockquote'],
        replacement: (content, node) => {
            return `\n\n<${node.tagName.toLowerCase()}>${content}</${node.tagName.toLowerCase()}>\n\n`;
        }
    });

    try {
        const browser = await puppeteer.launch({
            headless: 'new',
            args: [
                '--no-sandbox',
                '--window-size=1920,1080',
                '--incognito'
            ],
            defaultViewport: {
                width: 1920,
                height: 1080
            }
        });

        const page = await browser.newPage();
        
        // 设置图片捕获，增加过滤条件
        console.log('Setting up image capture...');
        const resources = new Map();
        await page.setRequestInterception(true);
        
        page.on('request', request => {
            // 只允许主要资源类型
            const resourceType = request.resourceType();
            if (['document', 'script', 'xhr', 'fetch', 'image'].includes(resourceType)) {
                request.continue();
            } else {
                request.abort();
            }
        });
        
        page.on('response', async response => {
            const url = response.url();
            const resourceType = response.request().resourceType();
            
            // 只捕获实际的文章图片，排除广告和跟踪器
            if (resourceType === 'image' && 
                !url.includes('google') && 
                !url.includes('analytics') && 
                !url.includes('advertisement')) {
                try {
                    const buffer = await response.buffer();
                    const contentType = response.headers()['content-type'];
                    if (buffer && contentType) {
                        resources.set(url, `data:${contentType};base64,${buffer.toString('base64')}`);
                        console.log(`Captured image: ${url}`);
                    }
                } catch (e) {
                    console.warn(`Failed to capture image: ${url}`, e.message);
                }
            }
        });

        // 增加页面加载超时时间，添加更多等待条件
        console.log('Loading page...');
        await page.goto(url, { 
            waitUntil: ['load', 'domcontentloaded', 'networkidle0'], 
            timeout: 60000  // 增加到60秒
        });
        
        // 等待主要内容加载
        try {
            await page.waitForSelector('article, .article, .content, main', { timeout: 10000 });
        } catch (e) {
            console.warn('Could not find main content selector, continuing anyway');
        }

        console.log('Page loaded successfully');

        // 保存原始HTML
        console.log('Saving original HTML...');
        const originalHtml = await page.content();
        await fs.writeFile('original.html', originalHtml);
        console.log('Original HTML saved');
        
        // 清理内容
        console.log('Cleaning content...');
        await page.evaluate((selectors) => {
            let removedCount = 0;
            for (const selector of selectors) {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => {
                    el.remove();
                    removedCount++;
                });
            }
            console.log(`Removed ${removedCount} elements`);
        }, removeSelectors);
        console.log('Content cleaned');

        // 嵌入图片
        console.log(`Attempting to embed ${resources.size} images...`);
        const monolithicContent = await page.evaluate((resourceMap) => {
            const images = document.getElementsByTagName('img');
            let embedded = 0;
            let skipped = 0;
            let failed = 0;

            for (const img of images) {
                try {
                    const originalSrc = img.src;
                    if (resourceMap[originalSrc]) {
                        img.src = resourceMap[originalSrc];
                        embedded++;
                    } else {
                        skipped++;
                    }
                } catch (e) {
                    failed++;
                }
            }
            console.log(`Image embedding results: ${embedded} embedded, ${skipped} skipped, ${failed} failed`);
            return document.documentElement.outerHTML;
        }, Object.fromEntries(resources));

        // 保存嵌入图片后的版本
        console.log('Saving monolithic version...');
        await fs.writeFile('monolithic.html', monolithicContent);
        console.log('Monolithic version saved');

        // 转换为markdown
        console.log('Converting to markdown...');
        const markdown = turndownService.turndown(monolithicContent);
        await fs.writeFile('output.md', markdown);
        console.log('Markdown conversion completed');

        await browser.close();
        
        console.log('\nFinal Summary:');
        console.log('---------------');
        console.log(`Total images captured: ${resources.size}`);
        console.log('Files saved:');
        console.log('- original.html');
        console.log('- monolithic.html');
        console.log('- output.md');
        console.log('---------------');

    } catch (error) {
        console.error('Error during conversion:', error);
        throw error;
    }
}

// Usage
const url = 'https://www.zaobao.com.sg/entertainment/story20241002-4905086';
html2markdown(url);
