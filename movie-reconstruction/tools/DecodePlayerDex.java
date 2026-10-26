import brut.androlib.smali.SmaliDecoder;
import com.android.tools.smali.dexlib2.dexbacked.DexBackedDexFile;
import java.nio.file.*;
import java.util.zip.*;
public class DecodePlayerDex {
 public static void main(String[] args) throws Exception {
  Path apk=Path.of(args[0]), root=Path.of(args[1]);
  try(ZipFile zip=new ZipFile(apk.toFile())) {
   for(String number:new String[]{"7","8"}) {
    Path out=root.resolve("smali"+number);
    if(Files.exists(out)) continue;
    Files.createDirectories(out);
    new SmaliDecoder(apk.toFile(),true).decodeFile(new DexBackedDexFile(zip.getInputStream(zip.getEntry("classes"+number+".dex")).readAllBytes(),0),out.toFile());
   }
  }
 }
}
