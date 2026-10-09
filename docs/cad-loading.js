// Lossless transport packaging only: the returned bytes are the source GLB.
export async function decodeCadBytes(input,Decompressor=globalThis.DecompressionStream){
 let bytes=input instanceof ArrayBuffer?input:input.buffer.slice(input.byteOffset,input.byteOffset+input.byteLength);
 let head=new Uint8Array(bytes,0,Math.min(bytes.byteLength,4));
 const glb=h=>h.length===4&&h[0]===103&&h[1]===108&&h[2]===84&&h[3]===70;
 if(glb(head))return bytes; // Some servers already decode Content-Encoding.
 if(head.length<2||head[0]!==31||head[1]!==139)throw Error('CAD download is not a GLB or gzip file');
 if(typeof Decompressor!=='function')throw Error('This browser cannot unpack the CAD asset; use an up-to-date browser');
 bytes=await new Response(new Blob([bytes]).stream().pipeThrough(new Decompressor('gzip'))).arrayBuffer();
 head=new Uint8Array(bytes,0,Math.min(bytes.byteLength,4));if(!glb(head))throw Error('Unpacked CAD asset is not a GLB');return bytes;
}
