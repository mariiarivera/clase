/*
 * Two objects:
 * 1) Pivot star (pink), independent VAO
 * 2) Yellow face, independent VAO
 * GUI:
 *  - Move pivot
 *  - Move/rotate/scale face around pivot
 */

'use strict';

import * as twgl from 'twgl-base.js';
import { M3 } from '../../libs/2d-lib.js';
import GUI from 'lil-gui';

// ---------------- SHADERS ----------------

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

// -------- GLOBAL UI OBJECT --------

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

// -------- SHAPE: STAR PIVOT (PINK) --------

function generatePivotStar(xc, yc, radius = 40) {
    const pos = [];
    const col = [];
    const indices = [];

    const spikes = 5;
    let angle = 0;
    const step = (Math.PI * 2) / spikes;

    for (let i = 0; i < spikes; i++) {
        // triángulo entre centro y dos puntos consecutivos
        let x1 = xc + Math.cos(angle) * radius;
        let y1 = yc + Math.sin(angle) * radius;

        let x2 = xc + Math.cos(angle + step) * radius;
        let y2 = yc + Math.sin(angle + step) * radius;

        const base = pos.length / 2;

        pos.push(xc, yc, x1, y1, x2, y2);

        for (let k = 0; k < 3; k++) col.push(1, 0.4, 0.7, 1); // rosa

        indices.push(base, base + 1, base + 2);

        angle += step;
    }

    return {
        a_position: { numComponents: 2, data: pos },
        a_color: { numComponents: 4, data: col },
        indices: { numComponents: 3, data: indices }
    };
}

// -------- SHAPE: YELLOW FACE --------

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

    // Square
    addQuad(
        [cx - half, cy - half],
        [cx + half, cy - half],
        [cx + half, cy + half],
        [cx - half, cy + half],
        [1, 1, 0.4, 1]
    );

    // Eyes
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

    // Mouth line
    const mouthWidth = size * 0.5;
    const mouthY = cy + size * 0.10;
    addQuad(
        [cx - mouthWidth / 2, mouthY - 3],
        [cx + mouthWidth / 2, mouthY - 3],
        [cx + mouthWidth / 2, mouthY + 3],
        [cx - mouthWidth / 2, mouthY + 3],
        [0, 0, 0, 1]
    );

    // Teeth
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

// ---------------- MAIN ----------------

function main() {
    const canvas = document.querySelector('canvas');
    const gl = canvas.getContext('webgl2');

    twgl.resizeCanvasToDisplaySize(gl.canvas);
    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

    setupUI(gl);

    const programInfo = twgl.createProgramInfo(gl, [vsGLSL, fsGLSL]);

    // --- CREATE STAR VAO ---
    const starArrays = generatePivotStar(0, 0, 40);
    const starBuffer = twgl.createBufferInfoFromArrays(gl, starArrays);
    const starVAO = twgl.createVAOFromBufferInfo(gl, programInfo, starBuffer);

    // --- CREATE FACE VAO ---
    const faceArrays = generateFace(0, 0, 180);
    const faceBuffer = twgl.createBufferInfoFromArrays(gl, faceArrays);
    const faceVAO = twgl.createVAOFromBufferInfo(gl, programInfo, faceBuffer);

    drawScene(gl, programInfo, starVAO, starBuffer, faceVAO, faceBuffer);
}

function drawScene(gl, programInfo, starVAO, starBuffer, faceVAO, faceBuffer) {

    twgl.resizeCanvasToDisplaySize(gl.canvas);
    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

    gl.useProgram(programInfo.program);

    // ========================
    // 1. DRAW PIVOT STAR
    // ========================
    let starTrans = M3.translation([
        objects.pivot.x,
        objects.pivot.y
    ]);

    twgl.setUniforms(programInfo, {
        u_resolution: [gl.canvas.width, gl.canvas.height],
        u_transforms: starTrans
    });

    gl.bindVertexArray(starVAO);
    twgl.drawBufferInfo(gl, starBuffer);


    // ========================
    // 2. DRAW FACE (ALWAYS ROTATE AROUND PIVOT)
    // ========================

    const tx = objects.face.translate.x;   
    const ty = objects.face.translate.y;
    const angle = objects.face.rotate;     
    const sx = objects.face.scale.x;
    const sy = objects.face.scale.y;

    // Matrices
    let T_face  = M3.translation([tx, ty]); 
    let T_pivot = M3.translation([objects.pivot.x, objects.pivot.y]);
    let T_back  = M3.translation([-objects.pivot.x, -objects.pivot.y]);
    let R       = M3.rotation(angle);
    let S       = M3.scale([sx, sy]);

    // ORDEN CORRECTO FINAL
    //
    //    T_face  →  T_pivot → R → T_back → S
    //
    let transform = M3.identity();
    transform = M3.multiply(T_face, transform);      // mover toda la cara
    transform = M3.multiply(T_pivot, transform);     // llevar al pivote
    transform = M3.multiply(R, transform);           // rotar alrededor del pivote
    transform = M3.multiply(T_back, transform);      // regresar
    transform = M3.multiply(S, transform);           // escalar independiente

    twgl.setUniforms(programInfo, {
        u_resolution: [gl.canvas.width, gl.canvas.height],
        u_transforms: transform
    });

    gl.bindVertexArray(faceVAO);
    twgl.drawBufferInfo(gl, faceBuffer);


    // LOOP
    requestAnimationFrame(() => 
        drawScene(gl, programInfo, starVAO, starBuffer, faceVAO, faceBuffer)
    );
}




// ---------------- UI ----------------

function setupUI(gl) {
    const gui = new GUI();

    const radius = 40; // mismo radio usado en generatePivotStar()

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
