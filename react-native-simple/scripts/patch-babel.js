const fs = require('fs');
const path = require('path');

/**
 * Clean, safe Babel patches for RN 0.73 / Babel 7.23.x
 * Only patches if the exact pattern is found (no blind replaces).
 */

function patchFile(filePath, oldContent, newContent) {
  if (!fs.existsSync(filePath)) return false;
  let content = fs.readFileSync(filePath, 'utf8');
  if (!content.includes(oldContent)) return false;
  content = content.replace(oldContent, newContent);
  fs.writeFileSync(filePath, content);
  return true;
}

console.log('🔧 Applying Babel patches...\n');

// Patch 1: @babel/traverse Hub.addHelper() - prevent throw in RN context
const hubFile = 'node_modules/@babel/traverse/lib/hub.js';
const patched1 = patchFile(hubFile,
  `addHelper() {
    throw new Error("Helpers are not supported by the default hub.");`,
  `addHelper(name) {
    return { type: "Identifier", name };`
);
console.log(patched1 ? '✅ Patched @babel/traverse Hub.addHelper()' 
  : '⚠️  @babel/traverse Hub.addHelper() - already patched or not found');

// Patch 2: @babel/core - File._addHelper() null scope protection
const file = 'node_modules/@babel/core/lib/transformation/file/file.js';
if (fs.existsSync(file)) {
  let content = fs.readFileSync(file, 'utf8');
  let dirty = false;

  // Guard generateUidIdentifier
  const genPattern = 'const uid = this.scope.generateUidIdentifier(name);';
  const genReplacement = 'const _s = this.scope; const _g = _s ? _s.generateUidIdentifier.bind(_s) : (n => ({ type: "Identifier", name: n })); const uid = _g(name);';
  if (content.includes(genPattern)) {
    content = content.replace(genPattern, genReplacement);
    dirty = true;
  }

  // Guard getAllBindings
  if (content.includes('Object.keys(this.scope.getAllBindings())')) {
    content = content.replace(
      'Object.keys(this.scope.getAllBindings())',
      '(this.scope ? Object.keys(this.scope.getAllBindings()) : [])'
    );
    dirty = true;
  }

  // Guard hasBinding
  if (content.includes('this.path.scope.hasBinding(name, true)')) {
    content = content.replace(
      'this.path.scope.hasBinding(name, true)',
      '(this.path && this.path.scope ? this.path.scope.hasBinding(name, true) : false)'
    );
    dirty = true;
  }

  if (dirty) {
    fs.writeFileSync(file, content);
    console.log('✅ Patched @babel/core file.js');
  } else {
    console.log('ℹ️  @babel/core file.js - no patches needed');
  }
} else {
  console.log('ℹ️  @babel/core file.js - not found (may be ESM, skipping)');
}

// Patch 3: metro-react-native-babel-transformer - guard generateUidIdentifier
const mbrnFile = 'node_modules/metro-react-native-babel-transformer/src/index.js';
if (fs.existsSync(mbrnFile)) {
  let content = fs.readFileSync(mbrnFile, 'utf8');
  if (content.includes('scope.generateUidIdentifier')) {
    content = content.replace(
      'scope.generateUidIdentifier',
      '(scope ? scope.generateUidIdentifier.bind(scope) : (n => ({type:"Identifier",name:n})))'
    );
    fs.writeFileSync(mbrnFile, content);
    console.log('✅ Patched metro-react-native-babel-transformer');
  } else {
    console.log('ℹ️  metro-react-native-babel-transformer - already patched or no change needed');
  }
}

console.log('\n✨ Babel patches complete');
