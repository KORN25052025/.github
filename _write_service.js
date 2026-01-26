
const fs = require('fs');
const p = require('path');
const filePath = p.join('C:', 'Users', 'ahmet', 'Desktop', '.github', 'adaptive-math-learning', 'backend', 'services', 'enhanced_parent_teacher_service.py');

// Read the template from the companion .txt file
const txtPath = p.join('C:', 'Users', 'ahmet', 'Desktop', '.github', '_service_content.txt');
const content = fs.readFileSync(txtPath, 'utf8');
fs.writeFileSync(filePath, content, 'utf8');
console.log('File written, size:', content.length);
