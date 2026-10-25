import brut.androlib.smali.SmaliBuilder;
import brut.androlib.smali.SmaliDecoder;
import com.android.tools.smali.dexlib2.Opcodes;
import com.android.tools.smali.dexlib2.dexbacked.DexBackedDexFile;
import com.android.tools.smali.dexlib2.writer.builder.DexBuilder;
import com.android.tools.smali.dexlib2.writer.io.FileDataStore;
import java.nio.file.*;
import java.util.*;
import java.util.zip.*;

public class RebuildSdkDex {
    public static void main(String[] args) throws Exception {
        Path original = Path.of(args[0]), work = Path.of(args[1]);
        String oldValue = args[2], newValue = args[3];
        Files.createDirectories(work);
        try (ZipFile zip = new ZipFile(original.toFile())) {
            for (String entry : List.of("classes5.dex", "classes11.dex")) {
                Path smali = work.resolve(entry + "-smali");
                byte[] bytes = zip.getInputStream(zip.getEntry(entry)).readAllBytes();
                if (!Files.exists(smali)) {
                    Files.createDirectories(smali);
                    SmaliDecoder decoder = new SmaliDecoder(original.toFile(), true);
                    decoder.decodeFile(new DexBackedDexFile(bytes, 0), smali.toFile());
                }
                int version = Integer.parseInt(new String(bytes, 4, 3, java.nio.charset.StandardCharsets.US_ASCII));
                int api = switch(version) { case 35 -> 23; case 37 -> 24; case 38 -> 26; case 39 -> 28; default -> throw new IllegalStateException("Unsupported original DEX version " + version); };
                List<Path> files;
                try (var paths = Files.walk(smali)) { files = paths.filter(p -> p.toString().endsWith(".smali")).sorted().toList(); }
                int replacements = 0;
                int configured = 0;
                for (Path file : files) {
                    String text = Files.readString(file);
                    if (text.contains('"' + oldValue + '"')) {
                        int count = (text.length() - text.replace(oldValue, "").length()) / oldValue.length();
                        text = text.replace('"' + oldValue + '"', '"' + newValue + '"');
                        Files.writeString(file, text);
                        replacements += count;
                        System.out.println("SDK configuration updated: " + file + " (" + count + ")");
                    }
                    configured += (text.length() - text.replace('"' + newValue + '"', "").length()) / (newValue.length() + 2);
                }
                if (configured < 1) throw new IllegalStateException("No SDK configuration call site in " + entry);
                DexBuilder builder = new DexBuilder(new Opcodes(api));
                SmaliBuilder assembler = new SmaliBuilder(api);
                for (Path file : files) if (!assembler.buildFile(file.toFile(), builder)) throw new IllegalStateException("Smali assembly failed: " + file);
                Path generated = work.resolve(entry + ".api" + api);
                FileDataStore output = new FileDataStore(generated.toFile());
                builder.writeTo(output);
                output.raf.close();
                Files.copy(generated, work.resolve(entry), StandardCopyOption.REPLACE_EXISTING);
                System.out.println("Reassembled " + entry + " with sorted DEX tables, " + files.size() + " classes");
            }
        }
    }
}
