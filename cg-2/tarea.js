

// lados 

// agarra el tercer argumento de lo recibido por consola
let sides = Number(process.argv[2]);

// valida el nùmero de sides 
if (sides !== sides || sides < 3 || sides > 36) {
  sides = 8;
}


// argumentos para hacer los segmentos 
let args = process.argv.slice(3);
let segments = [];

// si no hay argumentos, ponemos uno por defecto
if (args.length === 0) {
  segments.push({
    height: 6,
    r1: 1.0,
    r2: 0.8
  });
} 
// cada 3 argumentos hacen un segmento
else {
  for (let i = 0; i < args.length; i += 3) {
    let h = Number(args[i]);
    let r1 = Number(args[i + 1]);
    let r2 = Number(args[i + 2]);


    // si hay algo mal, lo ignoramos
    if (h !== h || r1 !== r1 || r2 !== r2) continue;

    segments.push({ height: h, r1, r2 });
  }
}

// si esta vacio, se ponen los default
if (segments.length === 0) {
  segments.push({ height: 6, r1: 1.0, r2: 0.8 });
}

//obj data: vertices, normales y caras

let vertices = [];
let normals = [];
let faces = [];

// agregar vertice y normal
function addVertex(x, y, z, nx, ny, nz) {
  vertices.push({ x, y, z });

  // normalizar
  let L = Math.sqrt(nx * nx + ny * ny + nz * nz);
  if (L === 0) L = 1;

  normals.push({
    nx: nx / L,
    ny: ny / L,
    nz: nz / L
  });

  return vertices.length; // índice obj, 1 
}

// variables a usar
// altura de donde inicia cada segmento
let currentHeight = 0;
// circunferencia completa
const pi_dos = Math.PI * 2;

for (let s = 0; s < segments.length; s++) {

  let seg = segments[s];
  let h = seg.height;
  let r1 = seg.r1;
  let r2 = seg.r2;

  // normal lateral
  let deltaR = r1 - r2;
  let L = Math.sqrt(deltaR * deltaR + h * h);
  let nxBase = h / L;        // horizontal
  let nyBase = deltaR / L;   // vertical

  // inferior (anillo de abajo)
  let bottom = [];
  for (let i = 0; i < sides; i++) {
    let ang = (pi_dos * i) / sides;
    let x = Math.cos(ang) * r1;
    let z = Math.sin(ang) * r1;

    let nx = nxBase * Math.cos(ang);
    let nz = nxBase * Math.sin(ang);

    bottom.push(addVertex(x, currentHeight, z, nx, nyBase, nz));
  }

  // superior (anillo de arriba)
  let top = [];
  for (let i = 0; i < sides; i++) {
    let ang = (pi_dos * i) / sides;
    let x = Math.cos(ang) * r2;
    let z = Math.sin(ang) * r2;

    let nx = nxBase * Math.cos(ang);
    let nz = nxBase * Math.sin(ang);

    top.push(addVertex(x, currentHeight + h, z, nx, nyBase, nz));
  }

  // lados laterales, conectarlos para que formen triángulos
  for (let i = 0; i < sides; i++) {
    let a = bottom[i];
    let b = top[i];
    let a2 = bottom[(i + 1) % sides];
    let b2 = top[(i + 1) % sides];

    faces.push([a, b, a2]);
    faces.push([a2, b, b2]);
  }

  //base del primer segmento
  if (s === 0) {
    let center = addVertex(0, 0, 0, 0, -1, 0);
    for (let i = 0; i < sides; i++) {
      let a = bottom[i];
      let b = bottom[(i + 1) % sides];
      faces.push([center, a, b]);
    }
  }

  // parte arriba del último segmento
  if (s === segments.length - 1) {
    let topY = currentHeight + h;
    let center = addVertex(0, topY, 0, 0, 1, 0);
    for (let i = 0; i < sides; i++) {
      let a = top[(i + 1) % sides];
      let b = top[i];
      faces.push([center, a, b]);
    }
  }

  currentHeight += h;
}

// construir obj, reunir información para haceer el archivo

let lines = [];

lines.push(`# Edificio con segmentos múltiples`);
lines.push(`o edificio`);

for (let v of vertices) lines.push(`v ${v.x} ${v.y} ${v.z}`);
for (let n of normals) lines.push(`vn ${n.nx} ${n.ny} ${n.nz}`);
for (let f of faces) lines.push(`f ${f[0]}//${f[0]} ${f[1]}//${f[1]} ${f[2]}//${f[2]}`);

// guardar obj en archivo

const fs = require("fs");
fs.writeFileSync("edificio.obj", lines.join("\n"));

console.log("OBJ generado correctamente como edificio.obj");
