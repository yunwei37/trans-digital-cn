# download webpage

chromium --headless --window-size=1920,1080 --no-sandbox --run-all-compositor-stages-before-draw --virtual-time-budget=9000 --incognito --dump-dom https://news.sina.cn/sa/2011-09-07/detail-ikftssap4071717.d.html > original.html
node .github/downloader/webpage/clean_cheerio.js original.html
cat original_clean.html | monolith - -I  -fF --no-js -a --no-video -o res.html

node .github/downloader/markdown/html2md.js res.html > res.md
