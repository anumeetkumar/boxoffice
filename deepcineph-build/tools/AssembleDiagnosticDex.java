import com.android.tools.smali.dexlib2.Opcodes;
import com.android.tools.smali.dexlib2.writer.builder.DexBuilder;
import com.android.tools.smali.dexlib2.writer.io.FileDataStore;
import brut.androlib.smali.SmaliBuilder;
import java.nio.file.*;
public class AssembleDiagnosticDex {
    public static void main(String[] args) throws Exception {
        Path directory=Path.of(args[0]), output=Path.of(args[1]);
        Files.createDirectories(output.getParent());
        DexBuilder dex=new DexBuilder(new Opcodes(24));
        SmaliBuilder assembler=new SmaliBuilder(24);
        int count=0;
        try(var paths=Files.walk(directory)){
            for(Path file:paths.filter(p->p.toString().endsWith(".smali")).sorted().toList()){
                if(!assembler.buildFile((file.endsWith(Path.of("com/mgs/carparking/app/AppApplication.smali"))?Path.of(args[2]):file).toFile(),dex))throw new IllegalStateException("Assembly failed: "+file);
                count++;
            }
        }
        FileDataStore store=new FileDataStore(output.toFile());
        try { dex.writeTo(store); } finally { store.raf.close(); }
        System.out.println("BoxOffice assembled "+count+" classes using original DEX 037 format");
    }
}

