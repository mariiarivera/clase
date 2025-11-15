/*
 * Maria Rivera A01029678
 * Carita amarilla con pivote rosa
 * Tarea 1 CG
 * cara que rota, escala y se traslada 
 * la rotacion es alrededor de un pivote
 * usando TWGL
 */

'use strict';

import * as twgl from 'twgl-base.js';
import { M3 } from '../../libs/2d-lib.js';
import GUI from 'lil-gui';

// color

const vsGLSL = `#version 300 es
in vec2 a_position;
in vec4 a_color;

uniform vec2 u_resolution;
uniform mat3 u_transforms;

out vec4 v_color;

void main() {
    vec2 position = (u_transforms * vec3(a_position, 1.0)).xy;

    vec2 zeroToOne = position / u_resolution;
    vec2 clipSpace = zeroToOne * 2.0 - 1.0;

    gl_Position = vec4(clipSpace * vec2(1.0, -1.0), 0.0, 1.0);
    v_color = a_color;
}
`;

const fsGLSL = `#version 300 es
precision highp float;
in vec4 v_color;
out vec4 outColor;

void main() {
    outColor = v_color;
}
`;

// objetos

const objects = {
    pivot: {
        x: 300,
        y: 300,
    },
    face: {
        translate: { x: 600, y: 300 },
        rotate: 0,
        scale: { x: 1, y: 1 },
    },
};

// pivot un pentagono rosa

function generatePivotStar(xc, yc, radius = 40) {
    const pos = [];
    const col = [];
    const indices = [];

    const spikes = 5;
    let angle = 0;
    const step = (Math.PI * 2) / spikes;

    for (let i = 0; i < spikes; i++) {
        let x1 = xc + Math.cos(angle) * radius;
        let y1 = yc + Math.sin(angle) * radius;

        let x2 = xc + Math.cos(angle + step) * radius;
        let y2 = yc + Math.sin(angle + step) * radius;

        const base = pos.length / 2;

        pos.push(xc, yc, x1, y1, x2, y2);

        for (let k = 0; k < 3; k++) col.push(1, 0.4, 0.7, 1); 

        indices.push(base, base + 1, base + 2);

        angle += step;
    }

    return {
        a_position: { numComponents: 2, data: pos },
        a_color: { numComponents: 4, data: col },
        indices: { numComponents: 3, data: indices }
    };
}

// cara amarillo con ojos y boca

function generateFace(cx, cy, size) {

    const arrays = {
        a_position: { numComponents: 2, data: [] },
        a_color: { numComponents: 4, data: [] },
        indices: { numComponents: 3, data: [] },
    };

    const pos = arrays.a_position.data;
    const col = arrays.a_color.data;
    const ind = arrays.indices.data;

    const half = size / 2;

    function addQuad(a, b, c, d, color) {
        const base = pos.length / 2;
        pos.push(...a, ...b, ...c, ...d);
        for (let i = 0; i < 4; i++) col.push(...color);
        ind.push(base, base + 1, base + 2, base, base + 2, base + 3);
    }

    // cuadrado
    addQuad(
        [cx - half, cy - half],
        [cx + half, cy - half],
        [cx + half, cy + half],
        [cx - half, cy + half],
        [1, 1, 0.4, 1]
    );

    // ojos
    const eyeSize = size * 0.12;
    const eyeY = cy - half * 0.55;
    const eyeOffsetX = size * 0.25;

    function addDiamond(x, y, s) {
        addQuad(
            [x - s, y],
            [x, y - s],
            [x + s, y],
            [x, y + s],
            [0, 0, 0, 1]
        );
    }

    addDiamond(cx - eyeOffsetX, eyeY, eyeSize);
    addDiamond(cx + eyeOffsetX, eyeY, eyeSize);

    // boca
    const mouthWidth = size * 0.5;
    const mouthY = cy + size * 0.10;
    addQuad(
        [cx - mouthWidth / 2, mouthY - 3],
        [cx + mouthWidth / 2, mouthY - 3],
        [cx + mouthWidth / 2, mouthY + 3],
        [cx - mouthWidth / 2, mouthY + 3],
        [0, 0, 0, 1]
    );

    // dientes
    const toothSize = size * 0.12;
    const toothGap = 5;
    const toothY = mouthY + toothSize * 0.9;

    function addTooth(x, y, s) {
        const h = s / 2;
        addQuad(
            [x - h, y - h],
            [x + h, y - h],
            [x + h, y + h],
            [x - h, y + h],
            [1, 1, 1, 1]
        );
    }

    addTooth(cx - (toothSize + toothGap), toothY, toothSize);
    addTooth(cx + toothGap, toothY, toothSize);

    return arrays;
}



function main() {
    const canvas = document.querySelector('canvas');
    const gl = canvas.getContext('webgl2');

    twgl.resizeCanvasToDisplaySize(gl.canvas);
    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

    setupUI(gl);

    const programInfo = twgl.createProgramInfo(gl, [vsGLSL, fsGLSL]);

    // crear estrella pivote
    const starArrays = generatePivotStar(0, 0, 40);
    const starBuffer = twgl.createBufferInfoFromArrays(gl, starArrays);
    const starVAO = twgl.createVAOFromBufferInfo(gl, programInfo, starBuffer);

    // crear cara
    const faceArrays = generateFace(0, 0, 180);
    const faceBuffer = twgl.createBufferInfoFromArrays(gl, faceArrays);
    const faceVAO = twgl.createVAOFromBufferInfo(gl, programInfo, faceBuffer);

    drawScene(gl, programInfo, starVAO, starBuffer, faceVAO, faceBuffer);
}

function drawScene(gl, programInfo, starVAO, starBuffer, faceVAO, faceBuffer) {

    twgl.resizeCanvasToDisplaySize(gl.canvas);
    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

    gl.useProgram(programInfo.program);

    // dibuja pivote (estrella rosa)
    const starTrans = M3.translation([
        objects.pivot.x,
        objects.pivot.y
    ]);

    twgl.setUniforms(programInfo, {
        u_resolution: [gl.canvas.width, gl.canvas.height],
        u_transforms: starTrans
    });

    gl.bindVertexArray(starVAO);
    twgl.drawBufferInfo(gl, starBuffer);


    // dibuja cara, especial con transformaciones

    const faceX = objects.face.translate.x;   
    const faceY = objects.face.translate.y;
    const angle = objects.face.rotate;
    const sx = objects.face.scale.x;
    const sy = objects.face.scale.y;

    const pivotX = objects.pivot.x;
    const pivotY = objects.pivot.y;

  
    const offsetX = faceX - pivotX;
    const offsetY = faceY - pivotY;

    // matrices básicas
    const S      = M3.scale([sx, sy]);                 
    const Toff   = M3.translation([offsetX, offsetY]); 
    const R      = M3.rotation(angle);                 
    const Tpivot = M3.translation([pivotX, pivotY]);   

    
    let transform = M3.identity();
    transform = M3.multiply(S, transform);       
    transform = M3.multiply(Toff, transform);    
    transform = M3.multiply(R, transform);       
    transform = M3.multiply(Tpivot, transform);  

    twgl.setUniforms(programInfo, {
        u_resolution: [gl.canvas.width, gl.canvas.height],
        u_transforms: transform
    });

    gl.bindVertexArray(faceVAO);
    twgl.drawBufferInfo(gl, faceBuffer);

    // loop
    requestAnimationFrame(() =>
        drawScene(gl, programInfo, starVAO, starBuffer, faceVAO, faceBuffer)
    );
}






// ui

function setupUI(gl) {
    const gui = new GUI();

    const radius = 40; 

    const pivotFolder = gui.addFolder("Pivot (Star)");
    pivotFolder.add(objects.pivot, "x", radius, gl.canvas.width - radius);
    pivotFolder.add(objects.pivot, "y", radius, gl.canvas.height - radius);

    const faceT = gui.addFolder("Face Translation");
    faceT.add(objects.face.translate, "x", 0, gl.canvas.width);
    faceT.add(objects.face.translate, "y", 0, gl.canvas.height);

    const faceR = gui.addFolder("Face Rotation");
    faceR.add(objects.face, "rotate", 0, Math.PI * 2);

    const faceS = gui.addFolder("Face Scale");
    faceS.add(objects.face.scale, "x", -3, 3);
    faceS.add(objects.face.scale, "y", -3, 3);
}

main();
