import {readFile,readdir,writeFile} from 'node:fs/promises';
import {resolve,join,relative} from 'node:path';
import {createHash} from 'node:crypto';
const root=process.cwd();
const results=[];
for(const abi of await readdir(join(root,'raw-apk/lib'))) for(const name of await readdir(join(root,'raw-apk/lib',abi))) {
 const path=join(root,'raw-apk/lib',abi,name), b=await readFile(path);
 const result={path:relative(root,path).replaceAll('\\','/'),abi,bytes:b.length,sha256:createHash('sha256').update(b).digest('hex'),parser:'supplemental ELF section/dynamic-symbol inventory; no disassembly or execution'};
 try {
  if(b.toString('hex',0,4)!=='7f454c46'||b[5]!==1) throw Error('Not a supported little-endian ELF');
  const wide=b[4]===2; if(!wide&&b[4]!==1) throw Error('Unsupported ELF class');
  const range=(at,n)=>{if(!Number.isSafeInteger(at)||at<0||at+n>b.length)throw Error('ELF range exceeds file');};
  const u16=at=>{range(at,2);return b.readUInt16LE(at);};
  const u32=at=>{range(at,4);return b.readUInt32LE(at);};
  const u64=at=>{range(at,8);const n=b.readBigUInt64LE(at); if(n>BigInt(Number.MAX_SAFE_INTEGER))throw Error('ELF integer exceeds safe range');return Number(n);};
  const word=wide?u64:u32;
  const str=(base,size,index)=>{range(base,size); if(index<0||index>=size)return '';let end=b.indexOf(0,base+index); if(end<0||end>base+size)end=base+size;return b.toString('utf8',base+index,end);};
  const table=word(wide?40:32), stride=u16(wide?58:46), count=u16(wide?60:48), shstr=u16(wide?62:50);
  if(count>65535||stride<(wide?64:40))throw Error('Unsupported section table');range(table,stride*count);
  const sections=[];
  for(let i=0;i<count;i++){const at=table+i*stride;sections.push({name_index:u32(at),type:u32(at+4),offset:word(at+(wide?24:16)),size:word(at+(wide?32:20)),link:u32(at+(wide?40:24)),entry_size:word(at+(wide?56:36))});}
  const names=sections[shstr];
  for(const s of sections)s.name=names?str(names.offset,names.size,s.name_index):'';
  const symbols=[],needed=[];
  for(const s of sections){
   if(s.type===11){const strings=sections[s.link];if(!strings)continue;const step=s.entry_size||(wide?24:16);if(step<(wide?24:16))throw Error('Invalid symbol stride');range(s.offset,s.size);
    for(let at=s.offset;at+step<=s.offset+s.size;at+=step){const index=u32(at),info=b[at+(wide?4:12)],section=u16(at+(wide?6:14));const name=str(strings.offset,strings.size,index);if(name)symbols.push({name,binding:info>>4,type:info&15,defined:section!==0,value:word(at+(wide?8:4)),size:word(at+(wide?16:8))});}
   }
   if(s.type===6){const strings=sections[s.link];if(!strings)continue;const step=wide?16:8;range(s.offset,s.size);for(let at=s.offset;at+step<=s.offset+s.size;at+=step){const tag=word(at),value=word(at+step/2);if(tag===1)needed.push(str(strings.offset,strings.size,value));}}
  }
  result.elf_class=wide?64:32;result.machine=u16(18);result.sections=sections.map(({name,type,offset,size})=>({name,type,offset,size}));result.needed=needed;result.dynamic_symbols=symbols;result.jni_exports=symbols.filter(s=>s.defined&&(/^(Java_|JNI_)/.test(s.name)));
 }catch(e){result.parse_error=String(e);}
 results.push(result);
}
await writeFile(join(root,'native-inventory.json'),JSON.stringify(results,null,2));
console.log(JSON.stringify(results.map(r=>({path:r.path,symbols:r.dynamic_symbols?.length,jni_exports:r.jni_exports?.length,error:r.parse_error})),null,2));

