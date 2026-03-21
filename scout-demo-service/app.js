const express = require('express');

const app = express();
const port = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', service: 'scout-demo-service' });
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
