import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const data=JSON.parse(await readFile(resolve(root,'content/architecture.json'),'utf8'));
const manifest={};
await mkdir(resolve(root,'svg'),{recursive:true});
for(const d of data.diagrams){
 const source=resolve(root,'diagrams',d.file),dest=resolve(root,'svg',`${d.id}.svg`);
 const args=['-i',source,'-o',dest,'-c',resolve(root,'mermaid.config.json'),'-p',resolve(root,'puppeteer.config.json'),'-b','transparent','--svgId',`arch${d.id}`];
 const result=spawnSync(resolve(root,'node_modules/.bin/mmdc'),args,{stdio:'inherit',cwd:root});
 if(result.status!==0)throw new Error(`Diagram ${d.id} failed`);
 const svg=(await readFile(dest,'utf8')).replaceAll('<br>','<br />');
 await writeFile(dest,svg);
 manifest[d.id]=createHash('sha256').update(await readFile(source)).digest('hex');
}
await writeFile(resolve(root,'svg/manifest.json'),JSON.stringify(manifest,null,2)+'\n');
console.log('Rendered all 18 diagrams');
