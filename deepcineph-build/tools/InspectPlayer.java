import com.android.tools.smali.dexlib2.dexbacked.*;
import com.android.tools.smali.dexlib2.dexbacked.instruction.*;
import com.android.tools.smali.dexlib2.iface.*;
import com.android.tools.smali.dexlib2.iface.instruction.*;
import com.android.tools.smali.baksmali.*;
import com.android.tools.smali.baksmali.Adaptors.*;
import com.android.tools.smali.baksmali.formatter.*;
import java.util.*;import java.util.zip.*;import java.nio.file.*;import java.io.*;
class InspectPlayer {
 public static void main(String[] args)throws Exception{
  try(ZipFile zip=new ZipFile(args[0])){
   for(var entries=zip.entries();entries.hasMoreElements();){var entry=entries.nextElement();if(!entry.getName().matches("classes[0-9]*\\.dex"))continue;
    DexBackedDexFile dex=new DexBackedDexFile(zip.getInputStream(entry).readAllBytes(),0);
    for(int i=0;i<dex.classCount;i++){ClassDef def=(ClassDef)dex.classSection.get(i);if(!def.getType().equals("Lcom/mgs/carparking/ui/VideoPlayDetailActivity;"))continue;
     System.out.println("CLASS_DEX "+entry.getName());
     StringWriter sw=new StringWriter();BaksmaliWriter w=new BaksmaliWriter(sw);new ClassDefinition(new BaksmaliOptions(),def).writeTo(w);w.flush();Files.writeString(Path.of(args[1]),sw.toString());
     for(Object obj:def.getVirtualMethods()){Method m=(Method)obj;if(!m.getName().equals("onConfigurationChanged"))continue;
      for(Object ins:m.getImplementation().getInstructions()){Instruction in=(Instruction)ins;String ref=in instanceof ReferenceInstruction r?r.getReference().toString():"";System.out.println(((DexBackedInstruction)in).instructionStart+" "+in.getOpcode()+" "+ref);}
     }
    }
   }
  }
 }
}

