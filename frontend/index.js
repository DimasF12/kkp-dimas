const express = require('express');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = 5000;

app.use(express.static(path.join(__dirname, '/')));

const apiPaths = ['/auth', '/calculator', '/dandur', '/danpen', '/barangimpian', '/transactions'];

apiPaths.forEach(route => {
  console.log('Setting proxy for:', route);
  app.use(route, createProxyMiddleware({
    target: 'http://127.0.0.1:8000',
    changeOrigin: true,
    cookieDomainRewrite: '127.0.0.1',
    secure: false,
    logLevel: 'debug',
  }));
});

app.get('*', (req, res) => {
  res.sendFile(path.resolve(__dirname, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Frontend berjalan di http://127.0.0.1:${PORT}`);
});
