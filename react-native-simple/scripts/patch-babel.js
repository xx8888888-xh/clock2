const fs = require("fs");

console.log("Applying Babel null-guard patches...");

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
    console.log("ℹ️  Hub.addHelper() - no patch needed");
  }
}

// Patch 2: @babel/core - null scope guards
const babelCore = "node_modules/@babel/core/lib/transformation/file/file.js";
if (fs.existsSync(babelCore)) {
  let c = fs.readFileSync(babelCore, "utf8");
  let patched = false;

  if (c.includes("const uid = this.scope.generateUidIdentifier(name);")) {
    c = c.replace(
      "const uid = this.scope.generateUidIdentifier(name);",
      "const _s=this.scope||null; const _g=_s?_s.generateUidIdentifier.bind(_s):(n=>({type:'Identifier',name:n})); const uid=_g(name);"
    );
    patched = true;
  }
  if (c.includes("Object.keys(this.scope.getAllBindings())")) {
    c = c.replace(
      "Object.keys(this.scope.getAllBindings())",
      "(this.scope?Object.keys(this.scope.getAllBindings()):[])"
    );
    patched = true;
  }
  if (c.includes("this.path.scope.hasBinding(name, true)")) {
    c = c.replace(
      "this.path.scope.hasBinding(name, true)",
      "(this.path&&this.path.scope?this.path.scope.hasBinding(name,true):false)"
    );
    patched = true;
  }

  if (patched) {
    fs.writeFileSync(babelCore, c);
    console.log("✅ @babel/core patched");
  } else {
    console.log("ℹ️  @babel/core - no patch needed");
  }
} else {
  console.log("ℹ️  @babel/core not found (ESM build, skipping)");
}

// Patch 3: metro-react-native-babel-transformer
const mbrnFile = "node_modules/metro-react-native-babel-transformer/src/index.js";
if (fs.existsSync(mbrnFile)) {
  let c = fs.readFileSync(mbrnFile, "utf8");
  if (c.includes("scope.generateUidIdentifier")) {
    c = c.replace(
      "scope.generateUidIdentifier",
      "(scope?scope.generateUidIdentifier.bind(scope):(n=>({type:'Identifier',name:n})))"
    );
    fs.writeFileSync(mbrnFile, c);
    console.log("✅ metro-react-native-babel-transformer patched");
  } else {
    console.log("ℹ️  metro-react-native-babel-transformer - no patch needed");
  }
}

console.log("Done.");
