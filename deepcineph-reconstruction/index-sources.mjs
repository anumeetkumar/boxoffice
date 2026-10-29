import { readFile, writeFile } from 'node:fs/promises';
import { join, relative, resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
const out=process.cwd();
const json=async p=>JSON.parse(await readFile(join(out,p),'utf8'));
const sourceRoot=join(out,'jadx-export/sources');
const sourceFiles=execFileSync('rg',['--files',sourceRoot,'-g','*.java'],{encoding:'utf8',maxBuffer:32*1024*1024}).trim().split(/\r?\n/).sort();
const index=[], urls=[], apiFiles=[], routes=[], markers=[];
for(let batch=0;batch<sourceFiles.length;batch+=16) {
 await Promise.all(sourceFiles.slice(batch,batch+16).map(async p=>{
 const text=await readFile(p,'utf8'), path=relative(out,p).replaceAll('\\','/');
 const application=path.includes('/com/mgs/carparking/')||path.includes('/com/fvvcl/');
 const stubs=(text.match(/throw new UnsupportedOperationException\("Method not decompiled:/g)||[]).length;
 const errors=(text.match(/JADX ERROR:/g)||[]).length;
 index.push({path,bytes:Buffer.byteLength(text),sha256:createHash('sha256').update(text).digest('hex'),application,method_not_decompiled_stubs:stubs,jadx_error_markers:errors});
 if(stubs||errors) markers.push(index.at(-1));
 const lines=text.split('\n');
 for(let i=0;i<lines.length;i++) for(const m of lines[i].matchAll(/https?:\/\/[^\s"'<>\\)]+/g)) urls.push({url:m[0],path,line:i+1,application});
 if(!path.includes('/retrofit2/')&&/import retrofit2\.http\./.test(text)) apiFiles.push({path,annotations:lines.flatMap((line,i)=>/^\s*@[A-Za-z][\w.]*(\(|\s*$)/.test(line)?[{line:i+1,text:line.trim()}]:[])});
 if(/import retrofit2\.http\./.test(text)) for(let i=0;i<lines.length;i++){const match=lines[i].match(/@(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\("([^"\n]*)"\)/);if(match)routes.push({verb:match[1],route:match[2],path,line:i+1});}
 }));
 if(batch%1600===0) console.log('Indexed',Math.min(batch+16,sourceFiles.length),'of',sourceFiles.length);
}
for(const list of [index,urls,apiFiles,routes,markers])list.sort((a,b)=>a.path.localeCompare(b.path)||(a.line??0)-(b.line??0));
await writeFile(join(out,'source-index.json'),JSON.stringify(index,null,2));
await writeFile(join(out,'decompilation-limitations.json'),JSON.stringify(markers,null,2));
await writeFile(join(out,'url-candidates.json'),JSON.stringify(urls,null,2));
await writeFile(join(out,'api-interface-candidates.json'),JSON.stringify(apiFiles,null,2));
await writeFile(join(out,'api-routes.json'),JSON.stringify(routes,null,2));

