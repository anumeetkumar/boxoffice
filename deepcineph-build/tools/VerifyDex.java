import com.android.tools.smali.dexlib2.dexbacked.DexBackedDexFile;
import com.android.tools.smali.dexlib2.iface.ClassDef;
import com.android.tools.smali.baksmali.BaksmaliOptions;
import com.android.tools.smali.baksmali.Adaptors.ClassDefinition;
import com.android.tools.smali.baksmali.formatter.BaksmaliWriter;
import java.nio.file.*;
import java.io.*;
import java.util.*;
import java.util.zip.*;
class VerifyDex {
 static String canonical(ClassDef def)throws Exception {
  BaksmaliOptions options=new BaksmaliOptions();options.debugInfo=true;options.sequentialLabels=true;options.localsDirective=true;
  StringWriter sw=new StringWriter();BaksmaliWriter writer=new BaksmaliWriter(sw);new ClassDefinition(options,def).writeTo(writer);writer.flush();return sw.toString();
 }
 public static void main(String[] args)throws Exception {
  int checked=0,changed=0;
  try(ZipFile before=new ZipFile(args[0]);ZipFile after=new ZipFile(args[1])) {
   for(String name:List.of("classes.dex","classes3.dex")) {
    DexBackedDexFile oldDex=new DexBackedDexFile(before.getInputStream(before.getEntry(name)).readAllBytes(),0);
    DexBackedDexFile newDex=new DexBackedDexFile(after.getInputStream(after.getEntry(name)).readAllBytes(),0);
    Map<String,ClassDef> defs=new HashMap<>();for(int i=0;i<newDex.classCount;i++){ClassDef def=(ClassDef)newDex.classSection.get(i);defs.put(def.getType(),def);}
    if(oldDex.classCount!=defs.size())throw new IllegalStateException("Class counts differ");
    for(int i=0;i<oldDex.classCount;i++) { ClassDef def=(ClassDef)oldDex.classSection.get(i);
     String oldText=canonical(def);String newText=canonical(defs.get(def.getType()));
     if(!oldText.equals(newText)){changed++;System.out.println("SDK configuration class: "+def.getType());}
     if(!oldText.replace("9d0ed3d8efd5204654f4e6ca4a0e52fd","691c5f5ff7b2d3054de60e744c53c242").equals(newText))throw new IllegalStateException("Unexpected bytecode change: "+def.getType());
     checked++;
    }
   }
  }
  if(changed!=2)throw new IllegalStateException("Expected two SDK initialization classes, got "+changed);
  System.out.println("Canonical DEX classes verified: "+checked+"; only SDK initialization constants differ in "+changed+" classes");
 }
}

