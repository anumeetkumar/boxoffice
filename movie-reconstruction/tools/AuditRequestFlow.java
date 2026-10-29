import com.android.tools.smali.dexlib2.dexbacked.DexBackedDexFile;
import com.android.tools.smali.dexlib2.iface.ClassDef;
import com.android.tools.smali.baksmali.BaksmaliOptions;
import com.android.tools.smali.baksmali.Adaptors.ClassDefinition;
import com.android.tools.smali.baksmali.formatter.BaksmaliWriter;
import java.nio.file.*;
import java.io.*;
import java.util.*;
import java.util.zip.*;
public class AuditRequestFlow {
 static boolean selected(String name){
  for(String prefix:List.of("Lsa/","Lcm/","Lt9/","Lp9/","Ln9/","Lq9/","Lem/f;","Lem/k;","Lem/r;","Li9/a;","Lt/a;","Lcom/pp/","Lcom/jiagu/","Lcom/mgs/carparking/model/VIDEOPLAYDETAILVIEWMODEL","Lcom/mgs/carparking/ui/homecontent/videodetail/VideoPlayDetailActivity"))if(name.startsWith(prefix))return true;
  return false;
 }
 static Map<String,String> read(Path apk,Path out)throws Exception{
  Map<String,String> result=new TreeMap<>();
  BaksmaliOptions options=new BaksmaliOptions();options.debugInfo=false;options.sequentialLabels=true;options.localsDirective=true;
  try(ZipFile zip=new ZipFile(apk.toFile())){
   for(var entries=zip.entries();entries.hasMoreElements();){
    ZipEntry entry=entries.nextElement();if(!entry.getName().matches("classes[0-9]*\\.dex"))continue;
    DexBackedDexFile dex=new DexBackedDexFile(zip.getInputStream(entry).readAllBytes(),0);
    for(int index=0;index<dex.classCount;index++){
     ClassDef def=(ClassDef)dex.classSection.get(index);
     if(!selected(def.getType()))continue;
     StringWriter sw=new StringWriter();BaksmaliWriter writer=new BaksmaliWriter(sw);new ClassDefinition(options,def).writeTo(writer);writer.flush();
     String text=sw.toString();result.put(def.getType(),text);
     Path target=out.resolve(def.getType().substring(1,def.getType().length()-1)+".smali");Files.createDirectories(target.getParent());Files.writeString(target,text);
    }
   }
  }return result;
 }
 public static void main(String[] args)throws Exception{
  Path root=Path.of(args[2]);Map<String,String> original=read(Path.of(args[0]),root.resolve("original")),box=read(Path.of(args[1]),root.resolve("boxoffice"));
  List<String> report=new ArrayList<>();
  for(var entry:original.entrySet())report.add((entry.getValue().equals(box.get(entry.getKey()))?"IDENTICAL":"DIFFERENT")+"\t"+entry.getKey());
  Files.write(root.resolve("comparison.tsv"),report);long different=report.stream().filter(s->s.startsWith("DIFFERENT")).count();
  System.out.println("Canonical request/playback flow classes compared: "+report.size()+"; identical: "+(report.size()-different)+"; different: "+different);
  for(String line:report)if(line.startsWith("DIFFERENT"))System.out.println(line);
 }
}
