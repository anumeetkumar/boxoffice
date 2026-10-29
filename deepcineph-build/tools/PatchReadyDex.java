import com.android.tools.smali.dexlib2.dexbacked.*;
import com.android.tools.smali.dexlib2.dexbacked.instruction.*;
import com.android.tools.smali.dexlib2.iface.*;
import com.android.tools.smali.dexlib2.iface.instruction.*;
import com.android.tools.smali.dexlib2.Opcode;
import java.nio.file.*;import java.util.*;import java.util.zip.*;import java.security.*;import java.nio.*;
class PatchReadyDex {
 static final List<String> log=new ArrayList<>();
 static void change(byte[] data,String entry,int at,byte[] replacement,String reason){byte[] before=Arrays.copyOfRange(data,at,at+replacement.length);System.arraycopy(replacement,0,data,at,replacement.length);log.add(entry+"\t"+at+"\t"+replacement.length+"\t"+reason+"\t"+HexFormat.of().formatHex(before)+"\t"+HexFormat.of().formatHex(replacement));}
 static List<Method> methods(ClassDef def){List<Method> out=new ArrayList<>();for(Object m:def.getDirectMethods())out.add((Method)m);for(Object m:def.getVirtualMethods())out.add((Method)m);return out;}
 static List<Instruction> instructions(Method m){List<Instruction> out=new ArrayList<>();if(m.getImplementation()!=null)for(Object i:m.getImplementation().getInstructions())out.add((Instruction)i);return out;}
 static int stringIndex(DexBackedDexFile dex,String text){for(int i=0;i<dex.stringCount;i++)if(text.equals(dex.stringSection.get(i)))return i;return -1;}
 static byte[] constString(int reg,int index,int bytes){if(index<0)throw new IllegalStateException("Required existing string absent");ByteBuffer b=ByteBuffer.allocate(bytes).order(ByteOrder.LITTLE_ENDIAN);if(bytes==4){if(index>65535)throw new IllegalStateException("String needs jumbo");b.put((byte)0x1a).put((byte)reg).putShort((short)index);}else if(bytes==6)b.put((byte)0x1b).put((byte)reg).putInt(index);else throw new IllegalStateException("Unexpected const size");return b.array();}
 public static void main(String[] args)throws Exception{
  Path out=Path.of(args[1]);Files.createDirectories(out);int profile=0,defaults=0,ads=0,initializers=0;
  try(ZipFile zip=new ZipFile(args[0])){for(var entries=zip.entries();entries.hasMoreElements();){var e=entries.nextElement();if(!e.getName().matches("classes[0-9]*\\.dex"))continue;byte[] data=zip.getInputStream(e).readAllBytes();DexBackedDexFile dex=new DexBackedDexFile(data,0);int start=log.size(),emptyList=-1;
   for(int i=0;i<dex.fieldCount;i++)if(dex.fieldSection.get(i).toString().equals("Ljava/util/Collections;->EMPTY_LIST:Ljava/util/List;"))emptyList=i;
   for(int ci=0;ci<dex.classCount;ci++){ClassDef def=(ClassDef)dex.classSection.get(ci);String cls=def.getType();if(!Set.of("Lcom/mgs/carparking/util/RetrofitClient$1;","Lcom/mgs/carparking/util/UserUtils;","Lcom/mgs/carparking/netbean/AdInfoEntry;","Lcom/mgs/carparking/app/AppApplication;","Lcom/mgs/carparking/ui/MainActivity;").contains(cls))continue;
    for(Method m:methods(def)){List<Instruction> ins=instructions(m);if(ins.isEmpty())continue;
     if(cls.endsWith("RetrofitClient$1;")&&m.getName().equals("intercept"))for(int i=0;i<ins.size()-1;i++){Instruction v=ins.get(i),next=ins.get(i+1);if(v instanceof ReferenceInstruction r&&r.getReference().toString().equals("Lcom/mgs/carparking/util/UserUtils;->n()Ljava/lang/String;")&&next.getOpcode().toString().equals("MOVE_RESULT_OBJECT")){int at=((DexBackedInstruction)v).instructionStart,reg=((OneRegisterInstruction)next).getRegisterA();if(v.getCodeUnits()!=3)throw new IllegalStateException("Unexpected invoke size");byte[] body=new byte[8];System.arraycopy(constString(reg,stringIndex(dex,"hi"),6),0,body,0,6);change(data,e.getName(),at,body,"api-profile-hi");profile++;}}
     if(cls.endsWith("AdInfoEntry;")&&m.getName().startsWith("getNetCineVarAd_position_")&&m.getReturnType().equals("Ljava/util/List;")){
      int bytes=ins.stream().mapToInt(x->x.getCodeUnits()*2).sum();if(bytes<6||!m.getImplementation().getTryBlocks().isEmpty())throw new IllegalStateException("Unexpected ad getter body");byte[] body=new byte[bytes];if(emptyList>=0){body[0]=0x62;body[2]=(byte)emptyList;body[3]=(byte)(emptyList>>8);body[4]=0x11;}else{body[0]=0x12;body[2]=0x11;}change(data,e.getName(),((DexBackedInstruction)ins.get(0)).instructionStart,body,"unset-ad-placement:"+m.getName());ads++;
     }
     boolean adInit=cls.endsWith("AppApplication;")&&m.getName().equals("netCineFunnetCineFunLoadAdConf")||cls.endsWith("MainActivity;")&&m.getName().equals("c0")&&m.getParameters().isEmpty();
     if(adInit){if(!m.getReturnType().equals("V"))throw new IllegalStateException("Not void");Instruction v=ins.get(0);byte[] body=new byte[v.getCodeUnits()*2];body[0]=0x0e;change(data,e.getName(),((DexBackedInstruction)v).instructionStart,body,"disable-ad-initialization:"+cls+"."+m.getName());initializers++;}
    }
   }
   if(log.size()>start){byte[] sha=MessageDigest.getInstance("SHA-1").digest(Arrays.copyOfRange(data,32,data.length));System.arraycopy(sha,0,data,12,20);Adler32 a=new Adler32();a.update(data,12,data.length-12);ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN).putInt(8,(int)a.getValue());Files.write(out.resolve(e.getName()),data);}
  }}
  if(profile!=1||defaults!=0||ads<25||initializers!=3)throw new IllegalStateException("Unexpected patch counts profile="+profile+" default="+defaults+" ads="+ads+" init="+initializers);
  Files.write(out.resolve("patches.tsv"),log);System.out.println("Verified anchors: API profile "+profile+", UI default "+defaults+", ad getters "+ads+", ad initializers "+initializers);
 }
}


