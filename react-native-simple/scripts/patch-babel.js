const fs = require("fs");
console.log("Babel patches...");
const files = [
  ["node_modules/@babel/traverse/lib/hub.js", "addHelper() {", "addHelper(name) {"],
];
files.forEach(([f, old, nu]) => { if (fs.existsSync(f)) { let c=fs.readFileSync(f,"utf8"); if(c.includes(old)) { fs.writeFileSync(f,c.replace(old,nu)); console.log("Patched",f); } } });
console.log("Done");
