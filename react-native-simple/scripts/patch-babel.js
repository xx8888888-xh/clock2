const fs = require('fs');
const path = require('path');

function patchFile(filePath, oldCode, newCode) {
  if (fs.existsSync(filePath)) {
    let content = fs.readFileSync(filePath, 'utf8');
    if (content.includes(oldCode)) {
      content = content.replace(oldCode, newCode);
      fs.writeFileSync(filePath, content);
      console.log(`✅ Patched ${path.basename(filePath)}`);
      return true;
    }
  }
  return false;
}

// Patch 1: @babel/traverse Hub.addHelper() - return Identifier instead of throwing
const hubFile = 'node_modules/@babel/traverse/lib/hub.js';
if (fs.existsSync(hubFile)) {
  let content = fs.readFileSync(hubFile, 'utf8');
  if (content.includes('throw new Error("Helpers are not supported by the default hub.")')) {
    content = content.replace(
      'addHelper() { throw new Error("Helpers are not supported by the default hub."); }',
      'addHelper(name) { return { type: "Identifier", name: name }; }'
    );
    fs.writeFileSync(hubFile, content);
    console.log('✅ Patched @babel/traverse Hub.addHelper()');
  }
}

// Patch 2: @babel/core File._addHelper() - handle null scope
const file = 'node_modules/@babel/core/lib/transformation/file/file.js';
if (fs.existsSync(file)) {
  let content = fs.readFileSync(file, 'utf8');
  let patched = false;
  
  if (content.includes('this.declarations[name] = this.scope.generateUidIdentifier(name)')) {
    content = content.replace(
      'this.declarations[name] = this.scope.generateUidIdentifier(name);',
      'const _s=this.scope||{}; const _g=_s.generateUidIdentifier||((n)=>({type:"Identifier",name:n})); this.declarations[name] = _g(name);'
    );
    patched = true;
  }
  
  if (content.includes('Object.keys(this.scope.getAllBindings())')) {
    content = content.replace(
      'Object.keys(this.scope.getAllBindings())',
      '(this.scope?Object.keys(this.scope.getAllBindings()):[])'
    );
    patched = true;
  }
  
  if (content.includes('if (this.path.scope.hasBinding(name, true))')) {
    content = content.replace(
      'if (this.path.scope.hasBinding(name, true))',
      'if (this.path&&this.path.scope&&this.path.scope.hasBinding(name, true))'
    );
    patched = true;
  }
  
  if (content.includes('this.path.unshiftContainer("body", nodes)')) {
    content = content.replace(
      'this.path.unshiftContainer("body", nodes);\n    this.path.get("body").forEach(path => {\n      if (nodes.indexOf(path.node) === -1) return;\n      if (path.isVariableDeclaration()) this.scope.registerDeclaration(path);\n    });',
      'if (this.path) { this.path.unshiftContainer("body", nodes); this.path.get("body").forEach(path => { if (nodes.indexOf(path.node) === -1) return; if (this.scope && path.isVariableDeclaration()) this.scope.registerDeclaration(path); }); }'
    );
    patched = true;
  }
  
  if (patched) fs.writeFileSync(file, content);
  console.log(patched ? '✅ Patched @babel/core File._addHelper()' : 'ℹ️  @babel/core already patched or not needed');
}

// Patch 3: @babel/plugin-transform-classes inline-callSuper-helpers.js
const icsFile = 'node_modules/@babel/plugin-transform-classes/lib/inline-callSuper-helpers.js';
if (fs.existsSync(icsFile)) {
  let content = fs.readFileSync(icsFile, 'utf8');
  if (content.includes('file.scope.generateUidIdentifier("callSuper")')) {
    content = content.replace(
      'file.scope.generateUidIdentifier("callSuper")',
      '(file.scope||(file.path&&file.path.scope)||{}).generateUidIdentifier?.("callSuper")||{type:"Identifier",name:"callSuper"}'
    );
    fs.writeFileSync(icsFile, content);
    console.log('✅ Patched @babel/plugin-transform-classes inline-callSuper-helpers');
  }
}

console.log('✨ Babel patches complete');
