const fs = require('fs');
const path = require('path');

function patchFile(filePath, oldContent, newContent) {
  if (fs.existsSync(filePath)) {
    let content = fs.readFileSync(filePath, 'utf8');
    if (content.includes(oldContent)) {
      content = content.replace(oldContent, newContent);
      fs.writeFileSync(filePath, content);
      return true;
    }
  }
  return false;
}

console.log('🔧 Applying Babel patches...\n');

// Patch 1: @babel/traverse Hub.addHelper() - multi-line format
const hubFile = 'node_modules/@babel/traverse/lib/hub.js';
const hubOld = `addHelper() {
    throw new Error("Helpers are not supported by the default hub.");
  }`;
const hubNew = `addHelper(name) {
    return { type: "Identifier", name: name };
  }`;
if (patchFile(hubFile, hubOld, hubNew)) {
  console.log('✅ Patched @babel/traverse Hub.addHelper()');
} else {
  console.log('⚠️  @babel/traverse Hub.addHelper() - not patched (already patched or not found)');
}

// Patch 2: @babel/core File._addHelper() - handle null scope
const file = 'node_modules/@babel/core/lib/transformation/file/file.js';
if (fs.existsSync(file)) {
  let content = fs.readFileSync(file, 'utf8');
  let patched = false;

  // Fix corrupted patch first (from previous broken patch)
  const corrupted = 'const uid = const _s=this.scope||{}; const _g=_s.generateUidIdentifier||((n)=>({type:"Identifier",name:n})); this.declarations[name] = _g(name);';
  if (content.includes(corrupted)) {
    content = content.replace(corrupted,
      'const _s=this.scope||{}; const _g=_s.generateUidIdentifier?.bind(_s)||((n)=>({type:"Identifier",name:n})); const uid = _g(name); this.declarations[name] = uid;');
    patched = true;
    console.log('✅ Fixed corrupted @babel/core patch');
  }

  // Patch generateUidIdentifier - full statement
  const oldGen = 'const uid = this.scope.generateUidIdentifier(name);';
  const newGen = 'const _s=this.scope||{}; const _g=_s.generateUidIdentifier?.bind(_s)||((n)=>({type:"Identifier",name:n})); const uid = _g(name);';
  if (content.includes(oldGen) && !content.includes(newGen)) {
    content = content.replace(oldGen, newGen);
    patched = true;
  }

  // Patch getAllBindings
  if (content.includes('Object.keys(this.scope.getAllBindings())')) {
    content = content.replace(
      'Object.keys(this.scope.getAllBindings())',
      '(this.scope?Object.keys(this.scope.getAllBindings()):[])'
    );
    patched = true;
  }

  // Patch hasBinding
  if (content.includes('if (this.path.scope.hasBinding(name, true))')) {
    content = content.replace(
      'if (this.path.scope.hasBinding(name, true))',
      'if (this.path&&this.path.scope&&this.path.scope.hasBinding(name, true))'
    );
    patched = true;
  }

  // Patch unshiftContainer
  if (content.includes('this.path.unshiftContainer("body", nodes);')) {
    content = content.replace(
      `this.path.unshiftContainer("body", nodes);
    this.path.get("body").forEach(path => {
      if (nodes.indexOf(path.node) === -1) return;
      if (path.isVariableDeclaration()) this.scope.registerDeclaration(path);
    });`,
      `if (this.path) { this.path.unshiftContainer("body", nodes); this.path.get("body").forEach(path => { if (nodes.indexOf(path.node) === -1) return; if (this.scope && path.isVariableDeclaration()) this.scope.registerDeclaration(path); }); }`
    );
    patched = true;
  }

  if (patched) {
    fs.writeFileSync(file, content);
    console.log('✅ Patched @babel/core File._addHelper()');
  } else {
    console.log('⚠️  @babel/core - not patched (already patched or not found)');
  }
} else {
  console.log('⚠️  @babel/core file not found');
}

// Patch 3: @babel/plugin-transform-classes inline-callSuper-helpers.js
const icsFile = 'node_modules/@babel/plugin-transform-classes/lib/inline-callSuper-helpers.js';
if (fs.existsSync(icsFile)) {
  let content = fs.readFileSync(icsFile, 'utf8');
  let patched = false;

  // Patch generateUidIdentifier call
  const oldIcs1 = 'const id = file.scope.generateUidIdentifier("callSuper");';
  const newIcs1 = 'const id = (file.scope||(file.path&&file.path.scope)||{}).generateUidIdentifier?.("callSuper")||{type:"Identifier",name:"callSuper"};';
  if (content.includes(oldIcs1)) {
    content = content.replace(oldIcs1, newIcs1);
    patched = true;
  }

  // Fix unshiftContainer - handle null file.path
  const oldIcs2 = 'const [fnPath] = file.path.unshiftContainer("body", [fn]);';
  const newIcs2 = 'const [fnPath] = file.path ? file.path.unshiftContainer("body", [fn]) : null;';
  if (content.includes(oldIcs2)) {
    content = content.replace(oldIcs2, newIcs2);
    patched = true;
  }

  // Fix registerDeclaration - handle null file.scope
  const oldIcs3 = 'file.scope.registerDeclaration(fnPath);';
  const newIcs3 = 'if (file.scope) file.scope.registerDeclaration(fnPath);';
  if (content.includes(oldIcs3)) {
    content = content.replace(oldIcs3, newIcs3);
    patched = true;
  }

  if (patched) {
    fs.writeFileSync(icsFile, content);
    console.log('✅ Patched @babel/plugin-transform-classes inline-callSuper-helpers');
  } else {
    console.log('⚠️  inline-callSuper-helpers - not patched (already patched or not found)');
  }
} else {
  console.log('⚠️  inline-callSuper-helpers file not found');
}

// Patch 4: @babel/traverse scope/index.js - handle null path
const scopeFile = 'node_modules/@babel/traverse/lib/scope/index.js';
if (fs.existsSync(scopeFile)) {
  let content = fs.readFileSync(scopeFile, 'utf8');
  const oldScope = 'return callExpression(this.path.hub.addHelper(helperName), args);';
  const newScope = 'return callExpression(this.path&&this.path.hub&&this.path.hub.addHelper?this.path.hub.addHelper(helperName):{type:"Identifier",name:helperName}, args);';
  if (content.includes(oldScope)) {
    content = content.replace(oldScope, newScope);
    fs.writeFileSync(scopeFile, content);
    console.log('✅ Patched @babel/traverse scope/index.js');
  } else {
    console.log('ℹ️  @babel/traverse scope/index.js - no change needed');
  }
}

console.log('\n✨ Babel patches complete');
