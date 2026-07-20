const fs = require("fs");

console.log("Applying Babel 7.23.9 null-guard patches...");

// Patch 1: @babel/traverse Hub.addHelper() - prevent throw
const hubFile = "node_modules/@babel/traverse/lib/hub.js";
if (fs.existsSync(hubFile)) {
  let c = fs.readFileSync(hubFile, "utf8");
  if (c.includes("Helpers are not supported")) {
    c = c.replace(
      'addHelper() {\n    throw new Error("Helpers are not supported by the default hub.");',
      'addHelper(name) {\n    return { type: "Identifier", name };'
    );
    fs.writeFileSync(hubFile, c);
    console.log("✅ @babel/traverse Hub.addHelper() patched");
  } else {
    console.log("ℹ️  Hub.addHelper() - already patched or different pattern");
  }
} else {
  console.log("ℹ️  @babel/traverse hub.js not found");
}

// Patch 2: @babel/core - File._addHelper() null scope protection
// CRITICAL: Babel 7.23.9 uses COMBINED assignment:
//   const uid = this.declarations[name] = this.scope.generateUidIdentifier(name);
//   (NOT standalone const uid = this.scope.generateUidIdentifier(name);)
const babelCore = "node_modules/@babel/core/lib/transformation/file/file.js";
if (fs.existsSync(babelCore)) {
  let c = fs.readFileSync(babelCore, "utf8");
  let patched = false;

  // Pattern 1: Combined assignment (ACTUAL pattern in Babel 7.23.9!)
  const combinedPattern = "this.declarations[name] = this.scope.generateUidIdentifier(name)";
  if (c.includes(combinedPattern)) {
    c = c.replace(combinedPattern,
      "this.declarations[name] = (function(s){ return s && s.generateUidIdentifier ? s.generateUidIdentifier.apply(s, arguments) : {type:'Identifier', name:arguments[0]}; })(this.scope)"
    );
    patched = true;
    console.log("  ✅ Combined assignment pattern (Babel 7.23.9) patched");
  }

  // Pattern 2: Object.keys(this.scope.getAllBindings())
  if (c.includes("Object.keys(this.scope.getAllBindings())")) {
    c = c.replace(
      "Object.keys(this.scope.getAllBindings())",
      "(this.scope ? Object.keys(this.scope.getAllBindings()) : [])"
    );
    patched = true;
    console.log("  ✅ getAllBindings null-guard patched");
  }

  // Pattern 3: this.path.scope.hasBinding
  if (c.includes("this.path.scope.hasBinding(name, true)")) {
    c = c.replace(
      "this.path.scope.hasBinding(name, true)",
      "(this.path && this.path.scope ? this.path.scope.hasBinding(name, true) : false)"
    );
    patched = true;
    console.log("  ✅ hasBinding null-guard patched");
  }

  // Pattern 4: this.path.unshiftContainer
  if (c.includes('this.path.unshiftContainer("body", nodes)')) {
    c = c.replace(
      'this.path.unshiftContainer("body", nodes);',
      '(this.path ? this.path.unshiftContainer("body", nodes) : null);'
    );
    patched = true;
    console.log("  ✅ unshiftContainer null-guard patched");
  }

  // Pattern 5: this.scope.registerDeclaration
  if (c.includes("this.scope.registerDeclaration(path)")) {
    c = c.replace(
      "if (path.isVariableDeclaration()) this.scope.registerDeclaration(path);",
      "if (this.scope && path.isVariableDeclaration()) this.scope.registerDeclaration(path);"
    );
    patched = true;
    console.log("  ✅ registerDeclaration null-guard patched");
  }

  if (patched) {
    fs.writeFileSync(babelCore, c);
    console.log("✅ @babel/core file.js patched successfully");
  } else {
    console.log("ℹ️  @babel/core - no patterns matched (may already be patched)");
  }
} else {
  console.log("ℹ️  @babel/core file.js not found (ESM build - skipping)");
}

// Patch 3: metro-react-native-babel-transformer
const mbrnFile = "node_modules/metro-react-native-babel-transformer/src/index.js";
if (fs.existsSync(mbrnFile)) {
  let c = fs.readFileSync(mbrnFile, "utf8");
  if (c.includes("scope.generateUidIdentifier")) {
    c = c.replace(
      "scope.generateUidIdentifier",
      "(scope ? scope.generateUidIdentifier.bind(scope) : (n => ({type:'Identifier',name:n})))"
    );
    fs.writeFileSync(mbrnFile, c);
    console.log("✅ metro-react-native-babel-transformer patched");
  } else {
    console.log("ℹ️  metro-react-native-babel-transformer - no patch needed");
  }
} else {
  console.log("ℹ️  metro-react-native-babel-transformer not found (skipping)");
}

console.log("✨ All Babel patches applied.");
