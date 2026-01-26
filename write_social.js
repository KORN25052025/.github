
const fs = require('fs');
const target = 'C:/Users/ahmet/Desktop/.github/adaptive-math-learning/backend/services/social_service.py';
const c = require('fs').readFileSync('C:/Users/ahmet/Desktop/.github/social_service_content.txt', 'utf8');
fs.writeFileSync(target, c, 'utf8');
console.log('Written', fs.statSync(target).size, 'bytes');
